using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace csharp_ui.Services
{
    public class StockDataPoint
    {
        [JsonProperty("date")]   public string Date   { get; set; } = "";
        [JsonProperty("open")]   public double Open   { get; set; }
        [JsonProperty("high")]   public double High   { get; set; }
        [JsonProperty("low")]    public double Low    { get; set; }
        [JsonProperty("close")]  public double Close  { get; set; }
        [JsonProperty("volume")] public long   Volume { get; set; }
    }

    public class StockDataResponse
    {
        [JsonProperty("symbol")] public string Symbol { get; set; } = "";
        [JsonProperty("count")]  public int Count     { get; set; }
        [JsonProperty("data")]   public List<StockDataPoint> Data { get; set; } = new();
    }

    public class AnalysisResult
    {
        [JsonProperty("symbol")]  public string Symbol  { get; set; } = "";
        [JsonProperty("period")]  public string Period  { get; set; } = "";
        [JsonProperty("indicators")] public JObject? Indicators { get; set; }
        [JsonProperty("signals")] public JObject? Signals { get; set; }
        [JsonProperty("ai")]      public string? Ai     { get; set; }
    }

    public class ScreenResult
    {
        [JsonProperty("symbol")]  public string Symbol  { get; set; } = "";
        [JsonProperty("sector")]  public string Sector  { get; set; } = "";
        [JsonProperty("close")]   public double Close   { get; set; }
        [JsonProperty("rsi")]     public double Rsi     { get; set; }
        [JsonProperty("macd")]    public double Macd    { get; set; }
        [JsonProperty("signal")]  public string Signal  { get; set; } = "";
        [JsonProperty("change_pct")] public double ChangePct { get; set; }
        [JsonProperty("score")]   public int Score { get; set; }
    }

    public class HealthStatus
    {
        [JsonProperty("api")]        public string Api       { get; set; } = "";
        [JsonProperty("cpp_engine")] public bool CppEngine   { get; set; }
        [JsonProperty("ollama")]     public JObject? Ollama  { get; set; }
    }

    public class ApiService
    {
        private readonly HttpClient _http;
        private const string BaseUrl = "http://localhost:8000";

        public ApiService()
        {
            _http = new HttpClient { BaseAddress = new Uri(BaseUrl), Timeout = TimeSpan.FromSeconds(30) };
        }

        public async Task<HealthStatus?> GetHealthAsync()
        {
            try
            {
                var json = await _http.GetStringAsync("/api/health");
                return JsonConvert.DeserializeObject<HealthStatus>(json);
            }
            catch { return null; }
        }

        public async Task<StockDataResponse?> GetStockDataAsync(string symbol, string period = "3mo", string interval = "1d")
        {
            try
            {
                var json = await _http.GetStringAsync($"/api/stock/{symbol}?period={period}&interval={interval}");
                return JsonConvert.DeserializeObject<StockDataResponse>(json);
            }
            catch { return null; }
        }

        public async Task<List<ScreenResult>> GetScreenAsync(string preset = "bist30", string screenType = "summary", string period = "3mo", List<string>? indicators = null)
        {
            try
            {
                var payload = new { preset, screen_type = screenType, period, indicators = indicators ?? new List<string>() };
                var response = await _http.PostAsJsonAsync("/api/screen", payload);
                var json = await response.Content.ReadAsStringAsync();
                var obj = JObject.Parse(json);
                var results = obj["results"]?.ToObject<List<ScreenResult>>();
                return results ?? new();
            }
            catch { return new(); }
        }

        public async Task<AnalysisResult?> GetAnalysisAsync(string symbol, string period = "3mo", bool aiAnalysis = false)
        {
            try
            {
                var payload = new { symbol, period, ai_analysis = aiAnalysis, save_chart = false };
                var response = await _http.PostAsJsonAsync("/api/analyze", payload);
                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<AnalysisResult>(json);
            }
            catch { return null; }
        }

        public async Task<string> GetAiAnalysisAsync(string symbol, string period = "3mo", string model = "llama3.1")
        {
            try
            {
                var json = await _http.GetStringAsync($"/api/ai/analyze/{symbol}?period={period}&model={model}");
                var obj = JObject.Parse(json);
                return obj["ai"]?.ToString() ?? "AI analizi alınamadı.";
            }
            catch (Exception ex) { return $"Hata: {ex.Message}"; }
        }

        public async Task<List<string>> GetPresetsAsync(string preset)
        {
            try
            {
                var json = await _http.GetStringAsync("/api/presets");
                var obj = JObject.Parse(json);
                return obj[preset]?.ToObject<List<string>>() ?? new();
            }
            catch { return new(); }
        }
    }
}
