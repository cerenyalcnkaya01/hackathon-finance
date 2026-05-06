import yfinance as yf
import pandas as pd
import logging
import os
from typing import Optional

# Logger ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Basit RAM Cache
_data_cache = {}
_info_cache = {}

def fetch_historical_data(ticker_symbol: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
    """
    Belirtilen tarih aralığında geçmiş borsa verilerini çeker.
    
    Args:
        ticker_symbol (str): Hisse senedi sembolü (örn. 'AAPL', 'THYAO.IS').
        start_date (str): Başlangıç tarihi (YYYY-MM-DD).
        end_date (str): Bitiş tarihi (YYYY-MM-DD).
        interval (str): Veri aralığı (örn. '1d', '1h', '15m').
        
    Returns:
        pd.DataFrame: Borsa verilerini içeren DataFrame. Hata durumunda boş DataFrame döner.
    """
    logger.info(f"{ticker_symbol} için {start_date} - {end_date} aralığında veri çekiliyor (Aralık: {interval})...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        
        if df.empty:
            logger.warning(f"{ticker_symbol} için belirtilen tarihlerde veri bulunamadı.")
            return pd.DataFrame()
            
        logger.info(f"{ticker_symbol} verisi başarıyla çekildi. Toplam satır: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"{ticker_symbol} verisi çekilirken hata oluştu: {str(e)}")
        return pd.DataFrame()

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_recent_data(ticker_symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Verileri SSD üzerinde cache'ler. Eğer cache varsa sadece eksik günleri indirir.
    """
    cache_file = os.path.join(CACHE_DIR, f"{ticker_symbol}_{interval}.csv")
    df_cached = pd.DataFrame()
    
    if os.path.exists(cache_file):
        try:
            df_cached = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            # Ensure index is timezone-aware if needed, but yfinance usually returns tz-aware.
            if not df_cached.empty:
                df_cached.index = pd.to_datetime(df_cached.index, utc=True)
                logger.info(f"{ticker_symbol} verisi SSD cache'den yüklendi. Son tarih: {df_cached.index[-1]}")
        except Exception as e:
            logger.warning(f"Cache okuma hatası: {e}")
            df_cached = pd.DataFrame()

    try:
        ticker = yf.Ticker(ticker_symbol)
        
        if not df_cached.empty:
            # Sadece yeni verileri çek (son tarihten bugüne)
            last_date = df_cached.index[-1]
            # yfinance start param expects YYYY-MM-DD
            start_str = last_date.strftime('%Y-%m-%d')
            logger.info(f"{ticker_symbol} için {start_str} sonrasındaki yeni veriler çekiliyor...")
            df_new = ticker.history(start=start_str, interval=interval)
            
            if not df_new.empty:
                df_new.index = pd.to_datetime(df_new.index, utc=True)
                # Aynı günleri üst üste bindirme, yeni olanları ekle
                df_new = df_new[~df_new.index.isin(df_cached.index)]
                if not df_new.empty:
                    df = pd.concat([df_cached, df_new])
                    logger.info(f"{len(df_new)} yeni satır eklendi.")
                else:
                    df = df_cached
            else:
                df = df_cached
        else:
            logger.info(f"{ticker_symbol} için son {period} verisi sıfırdan çekiliyor...")
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                df.index = pd.to_datetime(df.index, utc=True)
        
        if df.empty:
            return pd.DataFrame()
            
        # Kaydet
        df.to_csv(cache_file)
        
        # Son periyodu sınırla (isteğe bağlı, çok büyümemesi için)
        # return df.tail(1000)
        return df
    except Exception as e:
        logger.error(f"{ticker_symbol} verisi çekilirken hata oluştu: {str(e)}")
        return df_cached if not df_cached.empty else pd.DataFrame()

def get_stock_info(ticker_symbol: str) -> dict:
    """
    Hisse senedi hakkında genel bilgileri çeker. RAM cache kullanır.
    """
    if ticker_symbol in _info_cache:
        return _info_cache[ticker_symbol]

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        result = {
            "symbol": info.get("symbol"),
            "shortName": info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "previousClose": info.get("previousClose"),
            "open": info.get("open"),
            "dayLow": info.get("dayLow"),
            "dayHigh": info.get("dayHigh"),
            "marketCap": info.get("marketCap"),
            "volume": info.get("volume"),
            "currency": info.get("currency")
        }
        _info_cache[ticker_symbol] = result
        return result
    except Exception as e:
        logger.error(f"{ticker_symbol} bilgileri çekilirken hata oluştu: {str(e)}")
        return {}

if __name__ == "__main__":
    # Test amaçlı kullanım
    print("BIST 30 Örneği: THYAO.IS")
    df_thy = fetch_recent_data("THYAO.IS", period="1mo", interval="1d")
    print(df_thy.head())
    
    print("\nAAPL Genel Bilgiler:")
    info = get_stock_info("AAPL")
    for key, value in info.items():
        print(f"{key}: {value}")
