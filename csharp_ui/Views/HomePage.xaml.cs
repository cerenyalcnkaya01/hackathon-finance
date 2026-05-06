using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using csharp_ui.Models;
using csharp_ui.Services;

namespace csharp_ui.Views
{
    public class HomeStockModel : System.ComponentModel.INotifyPropertyChanged
    {
        private string _symbol = "";
        private string _sector = "";
        private double _close;
        private double _high;
        private double _low;
        private double _rsi;
        private string _signal = "";
        private double _changePct;

        public string Symbol { get => _symbol; set { _symbol = value; OnPropertyChanged(); } }
        public string Sector { get => _sector; set { _sector = value; OnPropertyChanged(); } }
        public double Close  { get => _close; set { _close = value; OnPropertyChanged(); OnPropertyChanged(nameof(ChangePctStr)); OnPropertyChanged(nameof(ChangeColor)); } }
        public double High   { get => _high; set { _high = value; OnPropertyChanged(); } }
        public double Low    { get => _low; set { _low = value; OnPropertyChanged(); } }
        public int    Score  { get; set; }
        public double Rsi    { get => _rsi; set { _rsi = value; OnPropertyChanged(); OnPropertyChanged(nameof(RsiColor)); } }
        public string Signal { get => _signal; set { _signal = value; OnPropertyChanged(); OnPropertyChanged(nameof(SignalColor)); } }
        public double ChangePct { get => _changePct; set { _changePct = value; OnPropertyChanged(); OnPropertyChanged(nameof(ChangePctStr)); OnPropertyChanged(nameof(ChangeColor)); } }

        public string SignalColor => Signal.Contains("Satış") || Signal.Contains("Sat") ? "#FF4560" : 
                                     Signal.Contains("Alış") || Signal.Contains("Al") ? "#00E396" : "#EAEAEA";
        public string ChangePctStr => ChangePct >= 0 ? $"+{ChangePct:F2}%" : $"{ChangePct:F2}%";
        public string ChangeColor  => ChangePct >= 0 ? "#00E396" : "#FF4560";
        public string RsiColor => Rsi < 30 ? "#00E396" : Rsi > 70 ? "#FF4560" : "#EAEAEA";

        public event System.ComponentModel.PropertyChangedEventHandler? PropertyChanged;
        protected void OnPropertyChanged([System.Runtime.CompilerServices.CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new System.ComponentModel.PropertyChangedEventArgs(name));
    }

    public partial class HomePage : Page
    {
        private UserProfile _profile;
        private ApiService  _api = new ApiService();
        private ObservableCollection<HomeStockModel> _stocks = new();
        private string _cachePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "stocks_cache.json");

        public HomePage(UserProfile profile)
        {
            InitializeComponent();
            _profile = profile;
            ProfileNameText.Text  = _profile.Name;
            IndicatorsText.Text   = string.Join(", ", _profile.SelectedIndicators.Select(i => i.Name));
            StocksList.ItemsSource = _stocks;
            Loaded += HomePage_Loaded;
        }

        private async void HomePage_Loaded(object sender, RoutedEventArgs e) => await LoadDataAsync();
        private async void Refresh_Click(object sender, RoutedEventArgs e)   => await LoadDataAsync();

        private async Task LoadDataAsync()
        {
            // 1. Load from cache first for zero-wait UI
            LoadFromCache();
            
            if (_stocks.Count > 0)
            {
                StatusPanel.Visibility = Visibility.Collapsed;
                ListScroll.Visibility = Visibility.Visible;
            }
            else
            {
                StatusPanel.Visibility = Visibility.Visible;
                ListScroll.Visibility = Visibility.Collapsed;
                StatusText.Text = "Veriler hazırlanıyor...";
            }

            // 2. Start progressive update with selected indicators
            var selectedIndicators = _profile.SelectedIndicators.Select(i => i.Id).ToList();
            
            // 3. Sektör taramasını da arka planda başlat (paralel)
            _ = BackgroundSectorScreeningAsync();
            
            await UpdateProgressivelyAsync(selectedIndicators);
        }

        private async Task BackgroundSectorScreeningAsync()
        {
            try
            {
                // Sektör taraması (BIST 30 genel özet) arka planda yapılır ve cache'lenir
                var results = await _api.GetScreenAsync("bist30", "summary", "3mo");
                if (results.Count > 0)
                {
                    var cachePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "sector_cache.json");
                    var json = JsonSerializer.Serialize(results);
                    await File.WriteAllTextAsync(cachePath, json);
                }
            }
            catch { /* Background task error ignore */ }
        }

        private void LoadFromCache()
        {
            try
            {
                if (File.Exists(_cachePath))
                {
                    var json = File.ReadAllText(_cachePath);
                    var cached = JsonSerializer.Deserialize<List<HomeStockModel>>(json);
                    if (cached != null)
                    {
                        _stocks.Clear();
                        foreach (var s in cached) _stocks.Add(s);
                    }
                }
            }
            catch { /* Ignore cache errors */ }
        }

        private async Task UpdateProgressivelyAsync(List<string> indicators)
        {
            try
            {
                // Get symbols first
                var symbols = await _api.GetPresetsAsync("bist30");
                if (symbols.Count == 0) symbols = new List<string> { "THYAO.IS", "EREGL.IS", "ASELS.IS", "SISE.IS", "TUPRS.IS" };

                // Ensure all symbols exist in the collection (placeholders)
                foreach (var sym in symbols)
                {
                    if (!_stocks.Any(s => s.Symbol == sym))
                        _stocks.Add(new HomeStockModel { Symbol = sym, Signal = "Bekleniyor..." });
                }

                StatusPanel.Visibility = Visibility.Collapsed;
                ListScroll.Visibility = Visibility.Visible;

                // Update one by one
                foreach (var sym in symbols)
                {
                    var stock = _stocks.FirstOrDefault(s => s.Symbol == sym);
                    if (stock == null) continue;

                    // Update single stock via screen API - Use custom type if indicators are selected
                    string screenType = indicators.Count > 0 ? "custom" : "summary";
                    var screen = await _api.GetScreenAsync("", screenType, "3mo", indicators, new List<string> { sym });
                    if (screen.Count > 0)
                    {
                        var res = screen[0];
                        stock.Close = res.Close;
                        stock.High = res.High;
                        stock.Low = res.Low;
                        stock.Rsi = res.Rsi;
                        stock.Signal = res.Signal;
                        stock.ChangePct = res.ChangePct;
                        stock.Sector = res.Sector;
                        stock.Score = res.Score;
                    }

                    // Save to SSD after each update for maximum persistence
                    await SaveToCacheAsync();
                }
            }
            catch (Exception ex)
            {
                StatusText.Text = "Hata oluştu.";
                StatusSubText.Text = ex.Message;
            }
        }

        private async Task SaveToCacheAsync()
        {
            try
            {
                var json = JsonSerializer.Serialize(_stocks.ToList());
                await File.WriteAllTextAsync(_cachePath, json);
            }
            catch { /* Ignore save errors */ }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }

        private void Stock_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (sender is FrameworkElement el && el.DataContext is HomeStockModel stock)
                NavigationService?.Navigate(new StockDetailPage(stock.Symbol));
        }
    }
}
