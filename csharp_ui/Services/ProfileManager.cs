using System;
using System.Collections.Generic;
using System.Linq;
using csharp_ui.Models;

namespace csharp_ui.Services
{
    public class ProfileManager
    {
        private static ProfileManager? _instance;
        public static ProfileManager Instance => _instance ??= new ProfileManager();

        public List<UserProfile> Profiles { get; private set; } = new();

        public ProfileManager()
        {
            // Seed with default profile
            var defaultProfile = new UserProfile
            {
                Name = "Varsayılan Profil",
                IsDefault = true,
                SelectedIndicators = new List<Indicator>
                {
                    new Indicator { Id = "rsi", Name = "RSI", Description = "Relative Strength Index", IsSelected = true },
                    new Indicator { Id = "macd", Name = "MACD", Description = "Moving Average Convergence Divergence", IsSelected = true }
                }
            };
            Profiles.Add(defaultProfile);
        }

        public void AddProfile(UserProfile profile)
        {
            Profiles.Add(profile);
        }

        public List<Indicator> GetAllAvailableIndicators()
        {
            return new List<Indicator>
            {
                new Indicator { Id = "rsi", Name = "RSI", Description = "Relative Strength Index (Aşırı Alım/Satım Göstergesi)" },
                new Indicator { Id = "macd", Name = "MACD", Description = "Moving Average Convergence Divergence (Trend Takipçisi)" },
                new Indicator { Id = "sma", Name = "SMA", Description = "Simple Moving Average (Basit Hareketli Ortalama)" },
                new Indicator { Id = "ema", Name = "EMA", Description = "Exponential Moving Average (Üstel Hareketli Ortalama)" },
                new Indicator { Id = "bollinger", Name = "Bollinger Bands", Description = "Volatilite ve Fiyat Sınırları Göstergesi" },
                new Indicator { Id = "stochastic", Name = "Stochastic Oscillator", Description = "Fiyatın kapanış seviyesinin fiyat aralığına göre konumu" }
            };
        }
    }
}
