using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using csharp_ui.Models;
using csharp_ui.Services;

namespace csharp_ui.ViewModels
{
    /// <summary>
    /// The main view model for the UI, handling user interactions and bindings.
    /// </summary>
    public partial class MainViewModel : ObservableObject
    {
        private readonly IPythonCoreService _pythonService;
        private readonly ICppOptimizationService _cppService;

        [ObservableProperty]
        private string _selectedSymbol;

        [ObservableProperty]
        private ObservableCollection<StockData> _chartData;

        [ObservableProperty]
        private AnalysisResult _currentAnalysis;

        public MainViewModel(IPythonCoreService pythonService, ICppOptimizationService cppService)
        {
            _pythonService = pythonService;
            _cppService = cppService;
            ChartData = new ObservableCollection<StockData>();
        }

        [RelayCommand]
        private async Task AnalyzeStockAsync()
        {
            // The actual connection and retrieval logic is left open/unimplemented
            // e.g. CurrentAnalysis = await _pythonService.GetAiAnalysisAsync(SelectedSymbol);
        }

        [RelayCommand]
        private async Task RunPerformanceScanAsync()
        {
            // Intended to invoke C++ core
        }
    }
}
