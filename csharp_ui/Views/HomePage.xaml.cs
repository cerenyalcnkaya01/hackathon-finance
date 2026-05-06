using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using csharp_ui.Models;
using csharp_ui.Services;

namespace csharp_ui.Views
{
    public class HomeStockModel
    {
        public string Symbol { get; set; } = "";
        public string Sector { get; set; } = "";
        public double Close { get; set; }
        public double High { get; set; }
        public double Low { get; set; }
    }

    public partial class HomePage : Page
    {
        private UserProfile _profile;
        private ApiService _api = new ApiService();

        public HomePage(UserProfile profile)
        {
            InitializeComponent();
            _profile = profile;
            ProfileNameText.Text = _profile.Name;
            IndicatorsText.Text = string.Join(", ", _profile.SelectedIndicators.Select(i => i.Name));
            
            Loaded += HomePage_Loaded;
        }

        private async void HomePage_Loaded(object sender, RoutedEventArgs e)
        {
            await LoadDataAsync();
        }

        private async void Refresh_Click(object sender, RoutedEventArgs e)
        {
            await LoadDataAsync();
        }

        private async Task LoadDataAsync()
        {
            StatusPanel.Visibility = Visibility.Visible;
            ListScroll.Visibility = Visibility.Collapsed;
            StatusText.Text = "Hisseler taranıyor...";
            StatusSubText.Text = "Piyasa verileri alınıyor...";

            // Fetch screened stocks from backend
            var results = await _api.GetScreenAsync("bist30", "summary", "3mo");
            
            if (results == null || results.Count == 0)
            {
                StatusText.Text = "Hisse bulunamadı.";
                StatusSubText.Text = "Sunucu yanıt vermiyor veya kriterlere uygun hisse yok.";
                return;
            }

            var homeModels = new List<HomeStockModel>();
            int count = 0;
            int total = Math.Min(results.Count, 12);

            foreach (var res in results.Take(total))
            {
                count++;
                StatusText.Text = $"Veriler yükleniyor... ({count}/{total})";
                StatusSubText.Text = $"{res.Symbol} detayları alınıyor...";

                var data = await _api.GetStockDataAsync(res.Symbol, "1mo");
                double high = res.Close;
                double low = res.Close;

                if (data?.Data != null && data.Data.Count > 0)
                {
                    high = data.Data.Max(d => d.High);
                    low = data.Data.Min(d => d.Low);
                }

                homeModels.Add(new HomeStockModel
                {
                    Symbol = res.Symbol,
                    Sector = res.Sector,
                    Close = res.Close,
                    High = high,
                    Low = low
                });
            }

            StocksList.ItemsSource = homeModels;
            StatusPanel.Visibility = Visibility.Collapsed;
            ListScroll.Visibility = Visibility.Visible;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }

        private void Stock_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (sender is FrameworkElement el && el.DataContext is HomeStockModel stock)
            {
                NavigationService?.Navigate(new StockDetailPage(stock.Symbol));
            }
        }
    }
}
