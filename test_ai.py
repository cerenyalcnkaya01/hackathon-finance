from python_core.ollama_client import generate_ai_analysis

analysis_result = {
    "symbol": "ABC",
    "last_price": 100,
    "rsi": 30,
    "macd": 0.5,
    "signal": "Buy",
    "info": {"sector": "Tech"}
}

resp = generate_ai_analysis(analysis_result)
print(resp)
