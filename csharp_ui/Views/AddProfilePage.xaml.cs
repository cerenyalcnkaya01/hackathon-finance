using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using csharp_ui.Models;
using csharp_ui.Services;

namespace csharp_ui.Views
{
    public partial class AddProfilePage : Page
    {
        private List<Indicator> _allIndicators;

        public AddProfilePage()
        {
            InitializeComponent();
            _allIndicators = ProfileManager.Instance.GetAllAvailableIndicators();
            IndicatorsList.ItemsSource = _allIndicators;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }

        private void SearchBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (_allIndicators == null) return;

            var query = SearchBox.Text.ToLower().Trim();
            if (string.IsNullOrEmpty(query))
            {
                IndicatorsList.ItemsSource = _allIndicators;
            }
            else
            {
                IndicatorsList.ItemsSource = _allIndicators.Where(i => 
                    i.Name.ToLower().Contains(query) || 
                    i.Description.ToLower().Contains(query)).ToList();
            }
        }

        private void Save_Click(object sender, RoutedEventArgs e)
        {
            var name = ProfileNameBox.Text.Trim();
            if (string.IsNullOrEmpty(name))
            {
                MessageBox.Show("Lütfen profil adı girin.", "Hata", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var selected = _allIndicators.Where(i => i.IsSelected).ToList();
            if (selected.Count == 0)
            {
                MessageBox.Show("Lütfen en az bir indikatör seçin.", "Hata", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var profile = new UserProfile
            {
                Name = name,
                SelectedIndicators = selected,
                IsDefault = false
            };

            ProfileManager.Instance.AddProfile(profile);
            NavigationService?.GoBack();
        }
    }
}
