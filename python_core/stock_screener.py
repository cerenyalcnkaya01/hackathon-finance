"""
Çoklu Hisse Tarama Modülü (Stock Screener)

Birden fazla hisse senedini toplu olarak tarar, her biri için veri çeker
ve temel filtreleme kriterleri uygulayarak uygun hisseleri listeler.
Bu modül BIST (Borsa Istanbul) ve global piyasalar için kullanılabilir.
"""

import pandas as pd
import logging
from typing import List, Optional
from python_core.data_fetcher import fetch_bulk_data, get_stock_info
from python_core.cpp_bridge import add_all_indicators_fast as add_all_indicators

# Logger ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── Popüler Hisse Listeleri ────────────────────────────────────────────────────

# BIST 30 (Borsa İstanbul) — Semboller ".IS" soneki ile kullanılır
BIST_30 = [
    "THYAO.IS", "GARAN.IS", "ASELS.IS", "EREGL.IS", "BIMAS.IS",
    "KCHOL.IS", "SAHOL.IS", "AKBNK.IS", "SISE.IS",  "TUPRS.IS",
    "YKBNK.IS", "PGSUS.IS", "TAVHL.IS", "TOASO.IS", "HEKTS.IS",
    "FROTO.IS", "TCELL.IS", "EKGYO.IS", "PETKM.IS",
    "SASA.IS",  "KONTR.IS", "ENKAI.IS", "GUBRF.IS", "KRDMD.IS",
    "TTKOM.IS", "VESTL.IS", "ODAS.IS",  "MGROS.IS", "ISDMR.IS",
    "ALARK.IS", "ASTOR.IS", "DOAS.IS",  "ENJSA.IS", "TUKAS.IS",
    "CIMSA.IS", "SOKM.IS",  "AKSEN.IS", "BERA.IS",  "BRSAN.IS",
    "CANTE.IS", "CWENE.IS", "DOHOL.IS", "EUPWR.IS", "GESAN.IS",
    "KAYSE.IS", "ASUZU.IS", "TMSN.IS",  "KARSN.IS",
    "BAGFS.IS", "EGEEN.IS", "GOLTS.IS", "QUAGR.IS", "SMRTG.IS",
    "YEOTK.IS", "ALBRK.IS", "SKBNK.IS", "TSKB.IS",  "ISCTR.IS",
    "HALKB.IS", "VAKBN.IS", "AEFES.IS", "CCOLA.IS", "ULKER.IS"
]

# ABD Teknoloji Hisseleri
US_TECH = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "AMD",   "INTC", "CRM"
]

# ─── Tarama Fonksiyonları ────────────────────────────────────────────────────────

def screen_summary(symbols: List[str], period: str = "3mo") -> pd.DataFrame:
    """
    Verilen hisse listesi için özet bir tablo oluşturur.
    Sinyalleri RSI ve MACD kombinasyonuna göre hesaplar ve en iyi fırsatları en üste getirir.
    """
    if not symbols: return pd.DataFrame()
    
    # Tüm verileri tek seferde çek
    bulk_data = fetch_bulk_data(symbols, period=period)
    results = []
    
    for symbol in symbols:
        df = bulk_data.get(symbol)
        if df is None or df.empty or len(df) < 30: continue
        
        try:
            df_ind = add_all_indicators(df)
            if 'Close' not in df_ind.columns:
                logger.warning(f"{symbol} için 'Close' kolonu bulunamadı.")
                continue

            last = df_ind.iloc[-1]
            prev = df_ind.iloc[-2]
            
            # Değişim yüzdesi
            change_pct = ((last["Close"] - prev["Close"]) / prev["Close"]) * 100
            
            rsi_val = last.get("RSI_14")
            macd_val = last.get("MACD")
            signal_val = last.get("Signal")
            
            # Puanlama sistemi (Alış fırsatlarını belirlemek için)
            score = 0
            
            # RSI Sinyalleri
            if rsi_val is not None and not pd.isna(rsi_val):
                if rsi_val <= 30: score += 2 # Güçlü Al
                elif rsi_val <= 40: score += 1 # Zayıf Al
                elif rsi_val >= 70: score -= 2 # Güçlü Sat
                elif rsi_val >= 65: score -= 1 # Zayıf Sat
            
            # MACD Sinyalleri
            if macd_val is not None and signal_val is not None:
                if prev["MACD"] <= prev["Signal"] and last["MACD"] > last["Signal"]:
                    score += 1 # MACD Yukarı Kesişim (AL)
                elif prev["MACD"] >= prev["Signal"] and last["MACD"] < last["Signal"]:
                    score -= 1 # MACD Aşağı Kesişim (SAT)

            # Sinyal Etiketi
            if score >= 2: sinyal = "🟢 Alış"
            elif score >= 1: sinyal = "🟡 Zayıf Al"
            elif score <= -2: sinyal = "🔴 Satış"
            elif score <= -1: sinyal = "🟠 Zayıf Sat"
            else: sinyal = "⚪ Nötr"

            sector = "BIST / Teknoloji" if ".IS" in symbol else "Global / Tech"

            results.append({
                "Sembol": symbol, 
                "Sektör": sector, 
                "Son Fiyat": round(last["Close"], 2),
                "En Yüksek": round(df_ind["High"].max(), 2),
                "En Düşük": round(df_ind["Low"].min(), 2),
                "RSI_14": round(rsi_val, 2) if rsi_val and not pd.isna(rsi_val) else None,
                "MACD": round(macd_val, 4) if macd_val and not pd.isna(macd_val) else None,
                "Sinyal": sinyal,
                "ChangePct": round(change_pct, 2),
                "Score": score
            })
        except Exception as e:
            logger.warning(f"{symbol} işlenirken hata: {e}")
            continue
            
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        # Puanlamaya göre sırala (En yüksek puanlı 'Al' sinyalleri en üstte)
        df_res = df_res.sort_values(by="Score", ascending=False)
        
    return df_res

def screen_by_custom_indicators(symbols: List[str], period: str = "3mo", indicators: List[str] = []) -> pd.DataFrame:
    """
    Kullanıcı tarafından seçilen indikatörlere göre hisseleri tarar.
    Toplu veri çekme ile optimize edilmiştir.
    """
    if not symbols: return pd.DataFrame()
    bulk_data = fetch_bulk_data(symbols, period=period)
    results = []
    indicators = [i.lower() for i in indicators]
    
    for symbol in symbols:
        df = bulk_data.get(symbol)
        if df is None or df.empty or len(df) < 30: continue
        
        try:
            df_ind = add_all_indicators(df)
            last = df_ind.iloc[-1]
            prev = df_ind.iloc[-2]
            close = last["Close"]
            
            change_pct = ((close - prev["Close"]) / prev["Close"]) * 100
            
            score = 0
            signals = []
            
            if "rsi" in indicators and "RSI_14" in last and not pd.isna(last["RSI_14"]):
                if last["RSI_14"] <= 30:
                    score += 1
                    signals.append("RSI Al")
                elif last["RSI_14"] >= 70:
                    score -= 1
                    signals.append("RSI Sat")
                    
            if "macd" in indicators and "MACD" in last and "Signal" in last and not pd.isna(last["MACD"]):
                if last["MACD"] > last["Signal"]:
                    score += 1
                    signals.append("MACD Al")
                else:
                    score -= 1
                    signals.append("MACD Sat")
                    
            if "sma" in indicators and "SMA_14" in last and not pd.isna(last["SMA_14"]):
                if close > last["SMA_14"]:
                    score += 1
                    signals.append("SMA Al")
                    
            if "ema" in indicators and "EMA_14" in last and not pd.isna(last["EMA_14"]):
                if close > last["EMA_14"]:
                    score += 1
                    signals.append("EMA Al")
                    
            if "bollinger" in indicators and "BBL" in last and not pd.isna(last["BBL"]):
                if close <= last["BBL"]:
                    score += 1
                    signals.append("BB Al")
                elif close >= last["BBH"]:
                    score -= 1
                    signals.append("BB Sat")

            # info = get_stock_info(symbol)
            sector = "BIST / Teknoloji" if ".IS" in symbol else "Global / Tech"
            sinyal_str = ", ".join(signals) if signals else "Nötr"

            results.append({
                "Sembol": symbol,
                "Sektör": sector,
                "Son Fiyat": round(close, 2),
                "En Yüksek": round(df_ind["High"].max(), 2),
                "En Düşük": round(df_ind["Low"].min(), 2),
                "RSI_14": round(last.get("RSI_14", 0), 2),
                "MACD": round(last.get("MACD", 0), 4),
                "Sinyal": sinyal_str,
                "ChangePct": round(change_pct, 2),
                "Score": score
            })
        except Exception as e:
            logger.warning(f"{symbol} custom screening hatası: {e}")
            continue
            
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="Score", ascending=False)
        
    return df_res
def screen_by_rsi(symbols: List[str], period: str = "3mo", signal: str = "oversold") -> pd.DataFrame:
    """
    RSI değerine göre hisseleri filtreler (Aşırı alım/satım).
    """
    df_summary = screen_summary(symbols, period)
    if df_summary.empty: return df_summary
    
    if signal == "oversold":
        return df_summary[df_summary["RSI_14"] <= 30]
    elif signal == "overbought":
        return df_summary[df_summary["RSI_14"] >= 70]
    return df_summary

def screen_by_macd_crossover(symbols: List[str], period: str = "3mo") -> pd.DataFrame:
    """
    MACD kesişimine göre hisseleri filtreler (MACD > Signal).
    """
    if not symbols: return pd.DataFrame()
    bulk_data = fetch_bulk_data(symbols, period=period)
    results = []
    
    for symbol in symbols:
        df = bulk_data.get(symbol)
        if df is None or df.empty or len(df) < 30: continue
        
        try:
            df_ind = add_all_indicators(df)
            last = df_ind.iloc[-1]
            prev = df_ind.iloc[-2]
            
            # MACD yukarı kesişim: Önceki gün MACD < Signal, bugün MACD > Signal
            if prev["MACD"] <= prev["Signal"] and last["MACD"] > last["Signal"]:
                # info = get_stock_info(symbol)
                sector = "BIST / Teknoloji" if ".IS" in symbol else "Global / Tech"
                change_pct = ((last["Close"] - prev["Close"]) / prev["Close"]) * 100
                
                results.append({
                    "Sembol": symbol,
                    "Sektör": sector,
                    "Son Fiyat": round(last["Close"], 2),
                    "RSI_14": round(last["RSI_14"], 2) if not pd.isna(last["RSI_14"]) else None,
                    "MACD": round(last["MACD"], 4),
                    "Sinyal": "🟢 MACD Kesişim (AL)",
                    "ChangePct": round(change_pct, 2),
                    "Score": 1
                })
        except Exception as e:
            logger.warning(f"{symbol} MACD screening hatası: {e}")
            continue
            
    return pd.DataFrame(results)
