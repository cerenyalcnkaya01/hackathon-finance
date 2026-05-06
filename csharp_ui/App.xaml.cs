using System.Windows;
using LiveChartsCore.SkiaSharpView;

namespace csharp_ui
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            LiveChartsCore.LiveCharts.Configure(config =>
                config
                    .AddDefaultMappers()
                    .AddDarkTheme()
            );
        }
    }
}
