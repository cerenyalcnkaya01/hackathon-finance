import pandas as pd
import ta

def calculate_sma(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.Series:
    """SMA hesaplar (ta kütüphanesi ile)."""
    return ta.trend.sma_indicator(df[column], window=window, fillna=True)

def calculate_ema(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.Series:
    """EMA hesaplar (ta kütüphanesi ile)."""
    return ta.trend.ema_indicator(df[column], window=window, fillna=True)

def calculate_rsi(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.Series:
    """RSI hesaplar (ta kütüphanesi ile)."""
    return ta.momentum.rsi(df[column], window=window, fillna=True)

def calculate_macd(df: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9, column: str = "Close") -> pd.DataFrame:
    """MACD hesaplar (ta kütüphanesi ile)."""
    macd_line = ta.trend.macd(df[column], window_slow=long_window, window_fast=short_window, fillna=True)
    signal_line = ta.trend.macd_signal(df[column], window_slow=long_window, window_fast=short_window, window_sign=signal_window, fillna=True)
    macd_histogram = ta.trend.macd_diff(df[column], window_slow=long_window, window_fast=short_window, window_sign=signal_window, fillna=True)
    
    return pd.DataFrame({
        'MACD': macd_line,
        'Signal': signal_line,
        'Histogram': macd_histogram
    })

def calculate_bbands(df: pd.DataFrame, window: int = 20, window_dev: int = 2, column: str = "Close") -> pd.DataFrame:
    """Bollinger Bands hesaplar (ta kütüphanesi ile)."""
    bb = ta.volatility.BollingerBands(close=df[column], window=window, window_dev=window_dev, fillna=True)
    return pd.DataFrame({
        'BBL': bb.bollinger_lband(),
        'BBM': bb.bollinger_mavg(),
        'BBH': bb.bollinger_hband()
    })

def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """ATR hesaplar (ta kütüphanesi ile)."""
    return ta.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=window, fillna=True)

def add_all_indicators(df: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
    """
    Tüm indikatörleri (RSI, MACD, SMA, EMA, BB, ATR) DataFrame'e ekler ve döndürür.
    """
    df = df.copy()
    
    # MA
    df['SMA_14'] = calculate_sma(df, window=14, column=column)
    df['EMA_14'] = calculate_ema(df, window=14, column=column)
    
    # RSI
    df['RSI_14'] = calculate_rsi(df, window=14, column=column)
    
    # MACD
    macd_df = calculate_macd(df, column=column)
    df = pd.concat([df, macd_df], axis=1)
    
    # Bollinger Bands
    bb_df = calculate_bbands(df, column=column)
    df = pd.concat([df, bb_df], axis=1)
    
    # ATR
    if all(c in df.columns for c in ["High", "Low", "Close"]):
        df['ATR_14'] = calculate_atr(df, window=14)
    else:
        df['ATR_14'] = 0.0
        
    return df
