"""
Çoklu Hisse Tarama Modülü (Stock Screener)

Birden fazla hisse senedini toplu olarak tarar, her biri için veri çeker
ve temel filtreleme kriterleri uygulayarak uygun hisseleri listeler.
Bu modül BIST (Borsa Istanbul) ve global piyasalar için kullanılabilir.
"""

import pandas as pd
import logging
from typing import List, Optional
from python_core.data_fetcher import fetch_recent_data, get_stock_info
from python_core.indicators import add_all_indicators

# Logger ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── Popüler Hisse Listeleri ────────────────────────────────────────────────────

# BIST 30 (Borsa İstanbul) — Semboller ".IS" soneki ile kullanılır
BIST_30 = [
    "THYAO.IS", "GARAN.IS", "ASELS.IS", "EREGL.IS", "BIMAS.IS",
    "KCHOL.IS", "SAHOL.IS", "AKBNK.IS", "SISE.IS",  "TUPRS.IS",
    "YKBNK.IS", "PGSUS.IS", "TAVHL.IS", "TOASO.IS", "HEKTS.IS",
    "KOZAL.IS", "FROTO.IS", "TCELL.IS", "EKGYO.IS", "PETKM.IS",
    "SASA.IS",  "KONTR.IS", "ENKAI.IS", "GUBRF.IS", "KRDMD.IS",
    "TTKOM.IS", "VESTL.IS", "ODAS.IS",  "MGROS.IS", "ISDMR.IS"
]

# ABD Teknoloji Hisseleri
US_TECH = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "AMD",   "INTC", "CRM"
]

# ─── Tarama Fonksiyonları ────────────────────────────────────────────────────────

def screen_by_rsi(symbols: List[str], period: str = "3mo",
                  rsi_low: float = 30.0, rsi_high: float = 70.0,
                  signal: str = "oversold") -> pd.DataFrame:
    """
    RSI değerine göre hisse taraması yapar.
    
    Args:
        symbols (List[str]): Taranacak hisse sembolleri listesi.
        period (str): Veri çekim periyodu (varsayılan: '3mo').
        rsi_low (float): Aşırı satım eşiği (varsayılan: 30).
        rsi_high (float): Aşırı alım eşiği (varsayılan: 70).
        signal (str): 'oversold' (aşırı satım) veya 'overbought' (aşırı alım).
        
    Returns:
        pd.DataFrame: Filtrelenen hisselerin sembol, son fiyat, RSI değeri ve sinyalini içerir.
    """
    results = []
    
    for symbol in symbols:
        try:
            df = fetch_recent_data(symbol, period=period, interval="1d")
            if df.empty or len(df) < 20:
                continue
                
            df_ind = add_all_indicators(df)
            last_row = df_ind.iloc[-1]
            current_rsi = last_row.get("RSI_14")
            
            if current_rsi is None or pd.isna(current_rsi):
                continue
            
            # Filtreleme
            if signal == "oversold" and current_rsi <= rsi_low:
                results.append({
                    "Sembol": symbol,
                    "Son Fiyat": round(last_row["Close"], 2),
                    "RSI": round(current_rsi, 2),
                    "Sinyal": "🟢 Aşırı Satım (Alım Fırsatı)"
                })
            elif signal == "overbought" and current_rsi >= rsi_high:
                results.append({
                    "Sembol": symbol,
                    "Son Fiyat": round(last_row["Close"], 2),
                    "RSI": round(current_rsi, 2),
                    "Sinyal": "🔴 Aşırı Alım (Satış Sinyali)"
                })
                
        except Exception as e:
            logger.warning(f"{symbol} taranırken hata: {str(e)}")
            continue
    
    return pd.DataFrame(results)


def screen_by_macd_crossover(symbols: List[str], period: str = "3mo") -> pd.DataFrame:
    """
    MACD çaprazlama (crossover) sinyali veren hisseleri tarar.
    Son 2 gün içinde MACD çizgisinin Signal çizgisini yukarı veya aşağı
    kestiği hisseleri bulur.
    
    Args:
        symbols (List[str]): Taranacak hisse sembolleri listesi.
        period (str): Veri çekim periyodu (varsayılan: '3mo').
        
    Returns:
        pd.DataFrame: Çaprazlama sinyali tespit edilen hisseler.
    """
    results = []
    
    for symbol in symbols:
        try:
            df = fetch_recent_data(symbol, period=period, interval="1d")
            if df.empty or len(df) < 30:
                continue
                
            df_ind = add_all_indicators(df)
            
            # Son 2 satıra bak (bugün ve dün)
            prev = df_ind.iloc[-2]
            curr = df_ind.iloc[-1]
            
            prev_diff = prev.get("MACD", 0) - prev.get("Signal", 0)
            curr_diff = curr.get("MACD", 0) - curr.get("Signal", 0)
            
            if pd.isna(prev_diff) or pd.isna(curr_diff):
                continue
            
            # Yukarı kesişim (Bullish Crossover): dün MACD < Signal, bugün MACD > Signal
            if prev_diff < 0 and curr_diff > 0:
                results.append({
                    "Sembol": symbol,
                    "Son Fiyat": round(curr["Close"], 2),
                    "MACD": round(curr["MACD"], 4),
                    "Signal": round(curr["Signal"], 4),
                    "Sinyal": "🟢 Yukarı Kesişim (Bullish)"
                })
            # Aşağı kesişim (Bearish Crossover): dün MACD > Signal, bugün MACD < Signal
            elif prev_diff > 0 and curr_diff < 0:
                results.append({
                    "Sembol": symbol,
                    "Son Fiyat": round(curr["Close"], 2),
                    "MACD": round(curr["MACD"], 4),
                    "Signal": round(curr["Signal"], 4),
                    "Sinyal": "🔴 Aşağı Kesişim (Bearish)"
                })
                
        except Exception as e:
            logger.warning(f"{symbol} MACD taranırken hata: {str(e)}")
            continue
    
    return pd.DataFrame(results)


def screen_summary(symbols: List[str], period: str = "3mo") -> pd.DataFrame:
    """
    Verilen hisse listesi için özet bir tablo oluşturur.
    Her hisse için son fiyat, RSI, MACD ve genel sinyal bilgisini döndürür.
    
    Args:
        symbols (List[str]): Taranacak hisse sembolleri listesi.
        period (str): Veri çekim periyodu.
        
    Returns:
        pd.DataFrame: Tüm hisseler için özet bilgi tablosu.
    """
    results = []
    
    for symbol in symbols:
        try:
            df = fetch_recent_data(symbol, period=period, interval="1d")
            if df.empty or len(df) < 30:
                continue
                
            df_ind = add_all_indicators(df)
            last = df_ind.iloc[-1]
            
            rsi_val = last.get("RSI_14")
            macd_val = last.get("MACD")
            signal_val = last.get("Signal")
            
            # Genel sinyal belirleme
            sinyal = "⚪ Nötr"
            if rsi_val is not None and not pd.isna(rsi_val):
                if rsi_val <= 30:
                    sinyal = "🟢 Alım"
                elif rsi_val >= 70:
                    sinyal = "🔴 Satış"

            # Sektör bilgisini getir (Cache'den gelecek)
            info = get_stock_info(symbol)
            sector = info.get("sector", "Bilinmiyor")

            results.append({
                "Sembol": symbol,
                "Sektör": sector,
                "Son Fiyat": round(last["Close"], 2),
                "RSI_14": round(rsi_val, 2) if rsi_val and not pd.isna(rsi_val) else None,
                "MACD": round(macd_val, 4) if macd_val and not pd.isna(macd_val) else None,
                "Sinyal": sinyal
            })
            
        except Exception as e:
            logger.warning(f"{symbol} özeti alınırken hata: {str(e)}")
            continue
    
    return pd.DataFrame(results)


# ─── Test Kullanımı ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("   BIST 30 — RSI Aşırı Satım Taraması (RSI <= 30)")
    print("=" * 60)
    
    # Hızlı test için küçük bir alt küme kullanıyoruz
    test_symbols = BIST_30[:5]
    
    rsi_results = screen_by_rsi(test_symbols, period="3mo", signal="oversold")
    if rsi_results.empty:
        print("Aşırı satım bölgesinde hisse bulunamadı.")
    else:
        print(rsi_results.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("   BIST 30 — MACD Çaprazlama Taraması")
    print("=" * 60)
    
    macd_results = screen_by_macd_crossover(test_symbols, period="3mo")
    if macd_results.empty:
        print("MACD çaprazlama sinyali bulunamadı.")
    else:
        print(macd_results.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("   Hisse Özet Tablosu")
    print("=" * 60)
    
    summary = screen_summary(test_symbols, period="3mo")
    if not summary.empty:
        print(summary.to_string(index=False))
