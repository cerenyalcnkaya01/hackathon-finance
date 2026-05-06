using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using csharp_ui.Services;
using LiveChartsCore;
using LiveChartsCore.Defaults;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using SkiaSharp;

namespace csharp_ui.ViewModels
{
    public class AssetRow
    {
        public string Name    { get; set; } = "";
        public string Symbol  { get; set; } = "";
        public double Close   { get; set; }
        public double Rsi     { get; set; }
        public string Sector  { get; set; } = "";
        public string Signal  { get; set; } = "";
        public double ChangePct { get; set; }
        public string ChangePctStr => ChangePct >= 0 ? $"+{ChangePct:F2}%" : $"{ChangePct:F2}%";
        public string ChangeColor  => ChangePct >= 0 ? "#00E396" : "#FF4560";
        public string RsiColor     => Rsi < 30 ? "#00E396" : Rsi > 70 ? "#FF4560" : "#EAEAEA";
    }

    public class MainViewModel : BaseViewModel
    {
        private readonly ApiService _api = new();

        // ── Status ──────────────────────────────────────────────
        private string _statusText = "Bağlanılıyor...";
        public  string StatusText  { get => _statusText; set => SetField(ref _statusText, value); }

        private bool _isConnected;
        public  bool IsConnected   { get => _isConnected; set => SetField(ref _isConnected, value); }

        private bool _isLoading;
        public  bool IsLoading     { get => _isLoading; set => SetField(ref _isLoading, value); }

        // ── Selected Stock / Period ─────────────────────────────
        private string _selectedSymbol = "THYAO.IS";
        public  string SelectedSymbol  { get => _selectedSymbol; set => SetField(ref _selectedSymbol, value); }

        private string _selectedPeriod = "3mo";
        public  string SelectedPeriod  { get => _selectedPeriod; set => SetField(ref _selectedPeriod, value); }

        private string _selectedPreset = "bist30";
        public  string SelectedPreset  { get => _selectedPreset; set => SetField(ref _selectedPreset, value); }

        // ── Stats ───────────────────────────────────────────────
        private string _currentPrice = "—";
        public  string CurrentPrice    { get => _currentPrice; set => SetField(ref _currentPrice, value); }

        private string _priceChange = "—";
        public  string PriceChange     { get => _priceChange; set => SetField(ref _priceChange, value); }

        private string _priceChangeColor = "#00E396";
        public  string PriceChangeColor  { get => _priceChangeColor; set => SetField(ref _priceChangeColor, value); }

        private string _highPrice = "—";
        public  string HighPrice       { get => _highPrice; set => SetField(ref _highPrice, value); }

        private string _lowPrice = "—";
        public  string LowPrice        { get => _lowPrice; set => SetField(ref _lowPrice, value); }

        private string _volumeText = "—";
        public  string VolumeText      { get => _volumeText; set => SetField(ref _volumeText, value); }

        private string _rsiText = "—";
        public  string RsiText         { get => _rsiText; set => SetField(ref _rsiText, value); }

        private string _macdSignal = "—";
        public  string MacdSignal      { get => _macdSignal; set => SetField(ref _macdSignal, value); }

        private string _aiAnalysis = "AI analizi için sembol seçin ve 'AI Analiz' butonuna tıklayın.";
        public  string AiAnalysis      { get => _aiAnalysis; set => SetField(ref _aiAnalysis, value); }

        private int _totalAssets;
        public  int TotalAssets        { get => _totalAssets; set => SetField(ref _totalAssets, value); }

        // ── Chart ───────────────────────────────────────────────
        public ObservableCollection<ISeries> ChartSeries { get; } = new();
        public Axis[] XAxes { get; } = new[]
        {
            new Axis
            {
                LabelsPaint = new SolidColorPaint(SKColor.Parse("#6B7280")),
                TextSize = 10,
                SeparatorsPaint = new SolidColorPaint(SKColor.Parse("#1E2530")),
                TicksPaint = null
            }
        };
        public Axis[] YAxes { get; } = new[]
        {
            new Axis
            {
                LabelsPaint = new SolidColorPaint(SKColor.Parse("#6B7280")),
                TextSize = 10,
                SeparatorsPaint = new SolidColorPaint(SKColor.Parse("#1E2530")),
                TicksPaint = null,
                Position = LiveChartsCore.Measure.AxisPosition.End
            }
        };

        // ── Assets Table ────────────────────────────────────────
        public ObservableCollection<AssetRow> Assets { get; } = new();

        // ── Search / Input ──────────────────────────────────────
        private string _symbolInput = "THYAO.IS";
        public  string SymbolInput   { get => _symbolInput; set => SetField(ref _symbolInput, value); }

        // ── Commands ─────────────────────────────────────────────
        public ICommand LoadStockCommand  { get; }
        public ICommand AiAnalyzeCommand  { get; }
        public ICommand SetPeriodCommand  { get; }
        public ICommand SetPresetCommand  { get; }
        public ICommand RefreshAllCommand { get; }

        public MainViewModel()
        {
            LoadStockCommand  = new RelayCommand(async _ => await LoadStockAsync());
            AiAnalyzeCommand  = new RelayCommand(async _ => await LoadAiAnalysisAsync());
            SetPeriodCommand  = new RelayCommand(async p => { SelectedPeriod = p?.ToString() ?? "3mo"; await LoadStockAsync(); });
            SetPresetCommand  = new RelayCommand(async p => { SelectedPreset = p?.ToString() ?? "bist30"; await LoadScreenAsync(); });
            RefreshAllCommand = new RelayCommand(async _ => await InitAsync());

            _ = InitAsync();
        }

        private async Task InitAsync()
        {
            IsLoading = true;
            await CheckHealthAsync();
            if (IsConnected)
            {
                await LoadStockAsync();
                await LoadScreenAsync();
            }
            IsLoading = false;
        }

        private async Task CheckHealthAsync()
        {
            var h = await _api.GetHealthAsync();
            if (h != null)
            {
                IsConnected = true;
                var ollamaStatus = h.Ollama?["status"]?.ToString() ?? "unknown";
                StatusText = $"✓ API Bağlı | C++ Motor: {(h.CppEngine ? "Aktif" : "Kapalı")} | AI: {ollamaStatus}";
            }
            else
            {
                IsConnected = false;
                StatusText = "✗ API'ye bağlanılamadı — uvicorn'un çalıştığından emin olun (port 8000)";
            }
        }

        private async Task LoadStockAsync()
        {
            var symbol = SymbolInput.Trim().ToUpper();
            if (string.IsNullOrEmpty(symbol)) return;

            SelectedSymbol = symbol;
            IsLoading = true;

            try
            {
                var data = await _api.GetStockDataAsync(symbol, SelectedPeriod);
                if (data?.Data == null || data.Data.Count == 0)
                {
                    CurrentPrice = "Veri yok";
                    IsLoading = false;
                    return;
                }

                var closes = data.Data.Select(d => d.Close).ToList();
                var labels = data.Data.Select(d => d.Date.Length >= 10 ? d.Date[5..10] : d.Date).ToArray();

                // Update stats
                var last  = data.Data.Last();
                var first = data.Data.First();
                CurrentPrice = $"{last.Close:N2}";
                var pct = (last.Close - first.Close) / first.Close * 100;
                PriceChange     = pct >= 0 ? $"+{pct:F2}%" : $"{pct:F2}%";
                PriceChangeColor = pct >= 0 ? "#00E396" : "#FF4560";
                HighPrice   = $"{closes.Max():N2}";
                LowPrice    = $"{closes.Min():N2}";
                VolumeText  = $"{last.Volume / 1_000_000.0:F1}M";

                // Build chart series
                var points = closes.Select(c => new ObservableValue(c)).ToArray();

                Application.Current.Dispatcher.Invoke(() =>
                {
                    ChartSeries.Clear();
                    ChartSeries.Add(new LineSeries<ObservableValue>
                    {
                        Values = points,
                        Name   = symbol,
                        Stroke = new SolidColorPaint(SKColor.Parse("#00F5A0"), 2),
                        GeometrySize = 0,
                        GeometryFill = null,
                        GeometryStroke = null,
                        Fill = new LinearGradientPaint(
                            new[] { SKColor.Parse("#5500F5A0"), SKColor.Parse("#0000F5A0") },
                            new SKPoint(0, 0), new SKPoint(0, 1)),
                        LineSmoothness = 0.4
                    });

                    XAxes[0].Labels = labels;
                });

                // Get analysis for RSI/MACD
                var analysis = await _api.GetAnalysisAsync(symbol, SelectedPeriod);
                if (analysis?.Indicators != null)
                {
                    var rsi = analysis.Indicators["RSI"]?.ToString();
                    RsiText    = rsi != null ? $"{double.Parse(rsi):F1}" : "—";
                    var macd   = analysis.Signals?["macd"]?.ToString() ?? "—";
                    MacdSignal = macd;
                }
            }
            catch (Exception ex)
            {
                CurrentPrice = $"Hata: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task LoadScreenAsync()
        {
            IsLoading = true;
            var rows = await _api.GetScreenAsync(SelectedPreset);
            TotalAssets = rows.Count;

            var mapped = rows.Select(r => new AssetRow
            {
                Name      = r.Symbol,
                Symbol    = r.Symbol,
                Sector    = r.Sector,
                Close     = r.Close,
                Rsi       = r.Rsi,
                Signal    = r.Signal,
                ChangePct = r.ChangePct
            }).Take(20).ToList();

            Application.Current.Dispatcher.Invoke(() =>
            {
                Assets.Clear();
                foreach (var row in mapped) Assets.Add(row);
            });

            IsLoading = false;
        }

        private async Task LoadAiAnalysisAsync()
        {
            AiAnalysis = "⏳ AI analiz yapılıyor...";
            var result = await _api.GetAiAnalysisAsync(SelectedSymbol, SelectedPeriod);
            AiAnalysis = result;
        }
    }
}
