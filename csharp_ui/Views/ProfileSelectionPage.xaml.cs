using System.Windows;
using System.Windows.Controls;
using csharp_ui.Models;
using csharp_ui.Services;

namespace csharp_ui.Views
{
    public partial class ProfileSelectionPage : Page
    {
        public ProfileSelectionPage()
        {
            InitializeComponent();
            Loaded += ProfileSelectionPage_Loaded;
        }

        private void ProfileSelectionPage_Loaded(object sender, RoutedEventArgs e)
        {
            ProfilesList.ItemsSource = null;
            ProfilesList.ItemsSource = ProfileManager.Instance.Profiles;
        }

        private void Profile_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (sender is FrameworkElement el && el.DataContext is UserProfile profile)
            {
                NavigationService?.Navigate(new HomePage(profile));
            }
        }

        private void AddProfile_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.Navigate(new AddProfilePage());
        }
    }
}
