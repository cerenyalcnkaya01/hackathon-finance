using System.Windows;
using System.Windows.Controls;
using csharp_ui.ViewModels;

namespace csharp_ui.Views
{
    public partial class StockDetailPage : Page
    {
        private MainViewModel _viewModel;

        public StockDetailPage(string symbol)
        {
            InitializeComponent();
            _viewModel = new MainViewModel();
            _viewModel.SymbolInput = symbol;
            this.DataContext = _viewModel;
            Loaded += StockDetailPage_Loaded;
        }

        private void StockDetailPage_Loaded(object sender, RoutedEventArgs e)
        {
            if (_viewModel.LoadStockCommand.CanExecute(null))
            {
                _viewModel.LoadStockCommand.Execute(null);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }
    }
}
