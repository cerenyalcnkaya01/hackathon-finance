"""
FastAPI Backend Sunucusu — Borsa AI Bot
Başlatma: uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
"""
import os, sys, logging
from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from python_core.data_fetcher import fetch_recent_data, get_stock_info
from python_core.pipeline import analyze_stock, analyze_multiple
from python_core.stock_screener import screen_by_rsi, screen_by_macd_crossover, screen_summary, BIST_30, US_TECH
from python_core.ollama_client import check_ollama_status, generate_ai_analysis, generate_screening_summary, list_available_models
from python_core.cpp_bridge import get_engine_info, is_cpp_available

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Borsa AI Bot API", version="1.0.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files
WEB_UI_DIR = os.path.join(ROOT_DIR, "web_ui")
ICON_DIR = os.path.join(ROOT_DIR, "icon")
if os.path.exists(WEB_UI_DIR):
    app.mount("/static", StaticFiles(directory=WEB_UI_DIR), name="static")
if os.path.exists(ICON_DIR):
    app.mount("/icons", StaticFiles(directory=ICON_DIR), name="icons")

class AnalyzeRequest(BaseModel):
    symbol: str; period: str = "3mo"; interval: str = "1d"
    save_chart: bool = True; ai_analysis: bool = False; ai_model: str = "llama3.1"

class MultiAnalyzeRequest(BaseModel):
    symbols: List[str]; period: str = "3mo"
    save_chart: bool = False; ai_summary: bool = False; ai_model: str = "llama3.1"

class ScreenRequest(BaseModel):
    symbols: List[str] = []; preset: str = "bist30"; period: str = "3mo"
    screen_type: str = "summary"; indicators: List[str] = []

@app.get("/api/info", tags=["System"])
def system_info():
    return {"service": "Borsa AI Bot", "status": "online", "engine": get_engine_info(), "timestamp": datetime.now().isoformat()}

@app.get("/api/health", tags=["System"])
def health():
    return {"api": "healthy", "cpp_engine": is_cpp_available(), "ollama": check_ollama_status()}

@app.get("/api/stock/{symbol}", tags=["Data"])
def get_stock(symbol: str, period: str = "3mo", interval: str = "1d"):
    df = fetch_recent_data(symbol, period=period, interval=interval)
    if df.empty:
        raise HTTPException(404, f"{symbol} verisi bulunamadı.")
    records = [{"date": str(i), "open": round(float(r.get("Open",0)),4), "high": round(float(r.get("High",0)),4), "low": round(float(r.get("Low",0)),4), "close": round(float(r.get("Close",0)),4), "volume": int(r.get("Volume",0))} for i, r in df.iterrows()]
    return {"symbol": symbol, "count": len(records), "data": records}

@app.get("/api/stock/{symbol}/info", tags=["Data"])
def stock_info(symbol: str):
    info = get_stock_info(symbol)
    if not info: raise HTTPException(404, f"{symbol} bilgisi alınamadı.")
    return info

@app.post("/api/analyze", tags=["Analysis"])
def analyze(req: AnalyzeRequest):
    result = analyze_stock(req.symbol, req.period, req.interval, req.save_chart, False)
    if "error" in result: raise HTTPException(404, result["error"])
    
    # Align with C# frontend expectations
    result["period"] = req.period
    result["indicators"] = {
        "RSI": result.get("rsi"),
        "MACD": result.get("macd"),
        "SMA": result.get("sma_14"),
        "EMA": result.get("ema_14")
    }
    result["signals"] = {
        "macd": result.get("signal"), # C# code uses Signals["macd"] for the signal text
        "rsi": "Aşırı Satım" if (result.get("rsi") or 50) <= 30 else "Aşırı Alım" if (result.get("rsi") or 50) >= 70 else "Nötr"
    }
    
    if req.ai_analysis: result["ai"] = generate_ai_analysis(result, req.ai_model)["ai_commentary"]
    return result

@app.post("/api/analyze/multi", tags=["Analysis"])
def analyze_multi(req: MultiAnalyzeRequest):
    results = analyze_multiple(req.symbols, req.period, req.save_chart, False)
    resp = {"results": results}
    if req.ai_summary: resp["ai_summary"] = generate_screening_summary(results, req.ai_model)
    return resp

@app.get("/api/analyze/{symbol}/chart", tags=["Analysis"])
def chart(symbol: str, period: str = "3mo"):
    result = analyze_stock(symbol, period, save_chart=True, save_json=False)
    p = result.get("chart_path")
    if p and os.path.exists(p): return FileResponse(p, media_type="image/png")
    raise HTTPException(500, "Grafik oluşturulamadı.")

@app.post("/api/screen", tags=["Screening"])
def screen(req: ScreenRequest):
    syms = BIST_30 if req.preset == "bist30" else US_TECH if req.preset == "us_tech" else req.symbols
    if not syms: raise HTTPException(400, "Sembol listesi gerekli.")
    
    if req.indicators and len(req.indicators) > 0:
        from python_core.stock_screener import screen_by_custom_indicators
        df = screen_by_custom_indicators(syms, req.period, req.indicators)
    else:
        fn = {"rsi_oversold": lambda: screen_by_rsi(syms, req.period, signal="oversold"), "rsi_overbought": lambda: screen_by_rsi(syms, req.period, signal="overbought"), "macd_crossover": lambda: screen_by_macd_crossover(syms, req.period)}.get(req.screen_type, lambda: screen_summary(syms, req.period))
        df = fn()
        
    if not df.empty:
        # Rename columns to match C# models (lowercase)
        rename_map = {
            "Sembol": "symbol",
            "Sektör": "sector",
            "Son Fiyat": "close",
            "En Yüksek": "high",
            "En Düşük": "low",
            "RSI": "rsi",
            "RSI_14": "rsi",
            "MACD": "macd",
            "Sinyal": "signal",
            "ChangePct": "change_pct",
            "Score": "score"
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return {"results": df.to_dict("records") if not df.empty else [], "count": len(df), "type": req.screen_type}

@app.get("/api/ai/status", tags=["AI"])
def ai_status():
    return check_ollama_status()

@app.get("/api/ai/models", tags=["AI"])
def ai_models():
    return {"models": list_available_models()}

@app.get("/api/ai/analyze/{symbol}", tags=["AI"])
def ai_analyze(symbol: str, period: str = "3mo", model: str = "llama3.1"):
    result = analyze_stock(symbol, period, save_chart=False, save_json=False)
    if "error" in result: raise HTTPException(404, result["error"])
    ai_resp = generate_ai_analysis(result, model)
    if ai_resp["success"]:
        return {"symbol": symbol, "ai": ai_resp["ai_commentary"]}
    else:
        return {"symbol": symbol, "ai": f"AI Hatası: {ai_resp['error']}"}

@app.get("/api/engine", tags=["System"])
def engine():
    return get_engine_info()

@app.get("/api/presets", tags=["Data"])
def presets():
    return {"bist30": BIST_30, "us_tech": US_TECH}
