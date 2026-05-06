using System.Collections.Generic;
using System.Threading.Tasks;
using csharp_ui.Models;

namespace csharp_ui.Services
{
    /// <summary>
    /// Interface for interacting with the Python Core Service (FastAPI + Ollama).
    /// </summary>
    public interface IPythonCoreService
    {
        Task<IEnumerable<StockData>> GetHistoricalDataAsync(string symbol, string timeframe);
        Task<AnalysisResult> GetAiAnalysisAsync(string symbol);
    }
}
