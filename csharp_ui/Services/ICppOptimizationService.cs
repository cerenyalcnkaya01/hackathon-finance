using System.Threading.Tasks;

namespace csharp_ui.Services
{
    /// <summary>
    /// Interface for interacting with the C++ Optimization Worker (via gRPC or ZeroMQ).
    /// </summary>
    public interface ICppOptimizationService
    {
        Task<bool> RunHighFrequencyScanAsync(string[] symbols);
        Task<double> CalculateComplexPatternAsync(double[] priceData);
    }
}
