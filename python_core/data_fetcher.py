import yfinance as yf
import pandas as pd
import logging
from typing import Optional

# Logger ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def fetch_recent_data(ticker_symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Son belirli bir periyoda ait borsa verilerini çeker.
    
    Args:
        ticker_symbol (str): Hisse senedi sembolü (örn. 'AAPL', 'THYAO.IS').
        period (str): Zaman periyodu ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max').
        interval (str): Veri aralığı (örn. '1d', '1h', '15m').
        
    Returns:
        pd.DataFrame: Borsa verilerini içeren DataFrame. Hata durumunda boş DataFrame döner.
    """
    logger.info(f"{ticker_symbol} için son {period} verisi çekiliyor (Aralık: {interval})...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            logger.warning(f"{ticker_symbol} için veri bulunamadı (Periyot: {period}).")
            return pd.DataFrame()
            
        logger.info(f"{ticker_symbol} verisi başarıyla çekildi. Toplam satır: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"{ticker_symbol} verisi çekilirken hata oluştu: {str(e)}")
        return pd.DataFrame()

def get_stock_info(ticker_symbol: str) -> dict:
    """
    Hisse senedi hakkında genel bilgileri çeker.
    
    Args:
        ticker_symbol (str): Hisse senedi sembolü (örn. 'AAPL', 'THYAO.IS').
        
    Returns:
        dict: Hisse bilgilerini içeren sözlük.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        return {
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
