"""
Uçtan Uca Pipeline (End-to-End Pipeline)

Bu modül data_fetcher, indicators ve charting modüllerini birleştirerek
tek bir çağrı ile veri çekme → indikatör hesaplama → grafik oluşturma
akışını gerçekleştirir. FastAPI servisine entegre edilecek ana iş mantığıdır.
"""

import pandas as pd
import logging
import json
import os
import sys
from datetime import datetime
from typing import List, Optional

# Windows terminalinde emoji/unicode desteği
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from python_core.data_fetcher import fetch_recent_data, fetch_historical_data, get_stock_info
from python_core.cpp_bridge import add_all_indicators_fast as add_all_indicators
from python_core.charting import plot_indicators

# Logger ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Grafik çıktıları için dizin
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def analyze_stock(symbol: str, period: str = "3mo", interval: str = "1d",
                  save_chart: bool = True, save_json: bool = True) -> dict:
    """
    Tek bir hisse senedi için uçtan uca analiz pipeline'ı çalıştırır.
    
    Akış:
        1. yfinance ile veri çek
        2. Teknik indikatörleri hesapla (RSI, MACD, SMA, EMA)
        3. (Opsiyonel) Grafik oluştur ve kaydet
        4. (Opsiyonel) JSON olarak sonuçları kaydet
    
    Args:
        symbol (str): Hisse sembolü (örn. 'THYAO.IS', 'AAPL').
        period (str): Veri periyodu (varsayılan: '3mo').
        interval (str): Veri aralığı (varsayılan: '1d').
        save_chart (bool): Grafik PNG dosyası oluşturulsun mu?
        save_json (bool): Sonuçlar JSON dosyasına kaydedilsin mi?
        
    Returns:
        dict: Analiz sonuçlarını içeren sözlük.
              - "symbol": Hisse sembolü
              - "info": Genel hisse bilgileri
              - "last_price": Son kapanış fiyatı
              - "rsi": Son RSI değeri
              - "macd": Son MACD değeri
              - "signal": Genel değerlendirme (Alım/Satış/Nötr)
              - "data_points": Toplam veri sayısı
              - "chart_path": Grafik dosya yolu (varsa)
    """
    logger.info(f"═══ {symbol} analiz pipeline'ı başlatılıyor ═══")
    result = {"symbol": symbol, "timestamp": datetime.now().isoformat()}
    
    # ── 1. Veri Çekme ──────────────────────────────────────────────
    logger.info(f"[1/4] {symbol} verisi çekiliyor...")
    df = fetch_recent_data(symbol, period=period, interval=interval)
    
    if df.empty:
        result["error"] = "Veri çekilemedi."
        logger.error(f"{symbol}: Veri bulunamadı, pipeline sonlandırıldı.")
        return result
    
    result["data_points"] = len(df)
    result["date_range"] = {
        "start": str(df.index[0]),
        "end": str(df.index[-1])
    }
    
    # ── 2. Hisse Bilgileri ─────────────────────────────────────────
    logger.info(f"[2/4] {symbol} genel bilgileri çekiliyor...")
    info = get_stock_info(symbol)
    result["info"] = info
    
    # ── 3. İndikatör Hesaplama ─────────────────────────────────────
    logger.info(f"[3/4] İndikatörler hesaplanıyor...")
    df_ind = add_all_indicators(df)
    last = df_ind.iloc[-1]
    
    result["last_price"] = round(float(last["Close"]), 2)
    result["rsi"] = round(float(last.get("RSI_14", 0)), 2)
    result["macd"] = round(float(last.get("MACD", 0)), 4)
    result["macd_signal"] = round(float(last.get("Signal", 0)), 4)
    result["sma_14"] = round(float(last.get("SMA_14", 0)), 2)
    result["ema_14"] = round(float(last.get("EMA_14", 0)), 2)
    
    # Genel sinyal değerlendirmesi
    rsi = result["rsi"]
    if rsi <= 30:
        result["signal"] = "🟢 ALIM — Aşırı satım bölgesinde"
    elif rsi >= 70:
        result["signal"] = "🔴 SATIŞ — Aşırı alım bölgesinde"
    elif result["macd"] > result["macd_signal"]:
        result["signal"] = "🟡 ZAYIF ALIM — MACD pozitif"
    elif result["macd"] < result["macd_signal"]:
        result["signal"] = "🟠 ZAYIF SATIŞ — MACD negatif"
    else:
        result["signal"] = "⚪ NÖTR"
    
    # ── 4. Grafik Oluşturma ────────────────────────────────────────
    if save_chart:
        logger.info(f"[4/4] Grafik oluşturuluyor...")
        safe_symbol = symbol.replace(".", "_")
        chart_filename = f"{safe_symbol}_{datetime.now().strftime('%Y%m%d')}.png"
        chart_path = os.path.join(OUTPUT_DIR, chart_filename)
        
        try:
            plot_indicators(df_ind, symbol=symbol, output_path=chart_path)
            result["chart_path"] = chart_path
            logger.info(f"Grafik kaydedildi: {chart_path}")
        except Exception as e:
            logger.warning(f"Grafik oluşturulamadı: {str(e)}")
            result["chart_path"] = None
    
    # ── 5. JSON Kaydetme ───────────────────────────────────────────
    if save_json:
        safe_symbol = symbol.replace(".", "_")
        json_filename = f"{safe_symbol}_{datetime.now().strftime('%Y%m%d')}.json"
        json_path = os.path.join(OUTPUT_DIR, json_filename)
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"JSON kaydedildi: {json_path}")
        except Exception as e:
            logger.warning(f"JSON kaydedilemedi: {str(e)}")
    
    logger.info(f"═══ {symbol} analizi tamamlandı: {result['signal']} ═══")
    return result


def analyze_multiple(symbols: List[str], period: str = "3mo",
                     save_chart: bool = True, save_json: bool = True) -> List[dict]:
    """
    Birden fazla hisse için toplu analiz çalıştırır.
    
    Args:
        symbols (List[str]): Hisse sembolleri listesi.
        period (str): Veri periyodu.
        save_chart (bool): Her hisse için grafik oluşturulsun mu?
        save_json (bool): Her hisse için JSON kaydedilsin mi?
        
    Returns:
        List[dict]: Her hisse için analiz sonuçlarının listesi.
    """
    results = []
    total = len(symbols)
    
    for i, symbol in enumerate(symbols, 1):
        logger.info(f"[{i}/{total}] {symbol} işleniyor...")
        result = analyze_stock(symbol, period=period, save_chart=save_chart, save_json=save_json)
        results.append(result)
    
    # Özet tablo yazdır
    print("\n" + "=" * 70)
    print("   TOPLU ANALİZ SONUÇLARI")
    print("=" * 70)
    
    summary_data = []
    for r in results:
        if "error" not in r:
            summary_data.append({
                "Sembol": r["symbol"],
                "Fiyat": r["last_price"],
                "RSI": r["rsi"],
                "MACD": r["macd"],
                "Sinyal": r["signal"]
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
    
    return results


# ─── Test Kullanımı ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Tek hisse analizi
    print("=" * 70)
    print("   TEK HİSSE ANALİZİ: THYAO.IS")
    print("=" * 70)
    
    result = analyze_stock("THYAO.IS", period="3mo", save_chart=True, save_json=True)
    
    print(f"\nSembol    : {result.get('symbol')}")
    print(f"Son Fiyat : {result.get('last_price')}")
    print(f"RSI (14)  : {result.get('rsi')}")
    print(f"MACD      : {result.get('macd')}")
    print(f"Sinyal    : {result.get('signal')}")
    print(f"Grafik    : {result.get('chart_path')}")
    
    # Çoklu hisse analizi
    print("\n")
    test_symbols = ["THYAO.IS", "GARAN.IS", "AAPL"]
    analyze_multiple(test_symbols, period="3mo", save_chart=False, save_json=False)
