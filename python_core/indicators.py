import pandas as pd

def calculate_sma(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.Series:
    """
    Basit Hareketli Ortalama (SMA - Simple Moving Average) hesaplar.
    
    Args:
        df (pd.DataFrame): Fiyat verilerini içeren DataFrame.
        window (int): SMA hesaplanacak periyot (varsayılan: 14).
        column (str): Hesaplanacak fiyat sütunu (varsayılan: "Close").
        
    Returns:
        pd.Series: SMA değerleri.
    """
    return df[column].rolling(window=window).mean()

def calculate_ema(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.Series:
    """
    Üstel Hareketli Ortalama (EMA - Exponential Moving Average) hesaplar.
    
    Args:
        df (pd.DataFrame): Fiyat verilerini içeren DataFrame.
        window (int): EMA hesaplanacak periyot (varsayılan: 14).
        column (str): Hesaplanacak fiyat sütunu (varsayılan: "Close").
        
    Returns:
        pd.Series: EMA değerleri.
    """
    return df[column].ewm(span=window, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.Series:
    """
    Göreceli Güç Endeksi (RSI - Relative Strength Index) hesaplar.
    Wilder'ın Smoothing yöntemi kullanılmıştır.
    
    Args:
        df (pd.DataFrame): Fiyat verilerini içeren DataFrame.
        window (int): RSI hesaplanacak periyot (varsayılan: 14).
        column (str): Hesaplanacak fiyat sütunu (varsayılan: "Close").
        
    Returns:
        pd.Series: RSI değerleri (0-100 arası).
    """
    delta = df[column].diff()
    
    # Kazançları (Gains) ve Kayıpları (Losses) ayır
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Wilder'ın düzleştirme (smoothing) metoduna uygun EMA hesapla
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    
    # RS (Relative Strength) ve RSI hesapla
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Sıfıra bölme hatalarını engelle
    rsi = rsi.fillna(0)
    rsi[avg_loss == 0] = 100.0 # Kayıp yoksa RSI 100'dür
    
    return rsi

def calculate_macd(df: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9, column: str = "Close") -> pd.DataFrame:
    """
    Hareketli Ortalama Yakınsama Iraksama (MACD - Moving Average Convergence Divergence) hesaplar.
    
    Args:
        df (pd.DataFrame): Fiyat verilerini içeren DataFrame.
        short_window (int): Kısa periyotlu EMA (varsayılan: 12).
        long_window (int): Uzun periyotlu EMA (varsayılan: 26).
        signal_window (int): Sinyal çizgisi periyodu (varsayılan: 9).
        column (str): Hesaplanacak fiyat sütunu (varsayılan: "Close").
        
    Returns:
        pd.DataFrame: 'MACD', 'Signal' ve 'Histogram' sütunlarını içeren DataFrame.
    """
    short_ema = calculate_ema(df, window=short_window, column=column)
    long_ema = calculate_ema(df, window=long_window, column=column)
    
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'MACD': macd_line,
        'Signal': signal_line,
        'Histogram': macd_histogram
    })

def add_all_indicators(df: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
    """
    Tüm indikatörleri (RSI, MACD, SMA, EMA) DataFrame'e ekler ve döndürür.
    
    Args:
        df (pd.DataFrame): İşlenecek DataFrame.
        column (str): Baz alınacak sütun.
        
    Returns:
        pd.DataFrame: İndikatör sütunları eklenmiş orijinal DataFrame.
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
    
    return df
