"""
C++ Köprü Modülü (C++ Bridge)

C++ ile derlenen pybind11 modülünü (cpp_indicators) Python tarafında
kullanılabilir hale getirir. Eğer C++ modülü derlenmediyse otomatik
olarak saf Python (fallback) implementasyonuna yönlendirir.

Bu sayede C++ derlenmese bile sistem çalışmaya devam eder.
"""

import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

# ── C++ Modülünü Yükleme Denemesi ────────────────────────────────────────────

_CPP_AVAILABLE = False
_cpp_module = None

try:
    import cpp_indicators as _cpp_module
    _CPP_AVAILABLE = True
    logger.info("✅ C++ indikatör modülü (cpp_indicators) başarıyla yüklendi — YÜKSEK PERFORMANS modu aktif.")
except ImportError:
    logger.warning(
        "⚠️  C++ modülü (cpp_indicators) bulunamadı. Saf Python implementasyonu kullanılacak.\n"
        "    C++ modülünü derlemek için: cd cpp_core && mkdir build && cd build && cmake .. && cmake --build ."
    )


def is_cpp_available() -> bool:
    """C++ modülünün kullanılabilir olup olmadığını döndürür."""
    return _CPP_AVAILABLE


def get_engine_info() -> dict:
    """Aktif hesaplama motorunun bilgilerini döndürür."""
    return {
        "engine": "C++" if _CPP_AVAILABLE else "Python (NumPy/Pandas)",
        "cpp_available": _CPP_AVAILABLE,
        "module_name": "cpp_indicators" if _CPP_AVAILABLE else "python_core.indicators",
    }


# ── Hibrit Hesaplama Fonksiyonları ────────────────────────────────────────────
# C++ varsa onu kullanır, yoksa Python'a fallback yapar.

def calculate_sma_fast(prices: list, period: int) -> list:
    """
    SMA hesaplar — C++ varsa C++, yoksa Python kullanır.
    
    Args:
        prices: Fiyat listesi (list[float])
        period: Periyot (int)
    Returns:
        list[float]: SMA değerleri
    """
    if _CPP_AVAILABLE:
        return _cpp_module.calculate_sma(prices, period)
    
    # Python fallback
    from python_core.indicators import calculate_sma
    df = pd.DataFrame({"Close": prices})
    result = calculate_sma(df, window=period, column="Close")
    return result.tolist()


def calculate_ema_fast(prices: list, period: int) -> list:
    """EMA hesaplar — C++ varsa C++, yoksa Python kullanır."""
    if _CPP_AVAILABLE:
        return _cpp_module.calculate_ema(prices, period)
    
    from python_core.indicators import calculate_ema
    df = pd.DataFrame({"Close": prices})
    result = calculate_ema(df, window=period, column="Close")
    return result.tolist()


def calculate_rsi_fast(prices: list, period: int = 14) -> list:
    """RSI hesaplar — C++ varsa C++, yoksa Python kullanır."""
    if _CPP_AVAILABLE:
        return _cpp_module.calculate_rsi(prices, period)
    
    from python_core.indicators import calculate_rsi
    df = pd.DataFrame({"Close": prices})
    result = calculate_rsi(df, window=period, column="Close")
    return result.tolist()


def calculate_macd_fast(prices: list, fast: int = 12, slow: int = 26,
                        signal: int = 9) -> dict:
    """
    MACD hesaplar — C++ varsa C++, yoksa Python kullanır.
    
    Returns:
        dict: {"macd_line": [...], "signal_line": [...], "histogram": [...]}
    """
    if _CPP_AVAILABLE:
        result = _cpp_module.calculate_macd(prices, fast, slow, signal)
        return {
            "macd_line": list(result.macd_line),
            "signal_line": list(result.signal_line),
            "histogram": list(result.histogram),
        }
    
    from python_core.indicators import calculate_macd
    df = pd.DataFrame({"Close": prices})
    macd_df = calculate_macd(df, short_window=fast, long_window=slow,
                             signal_window=signal, column="Close")
    return {
        "macd_line": macd_df["MACD"].tolist(),
        "signal_line": macd_df["Signal"].tolist(),
        "histogram": macd_df["Histogram"].tolist(),
    }


def add_all_indicators_fast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tüm indikatörleri ekler — C++ varsa performans-kritik hesaplamalar
    C++ tarafında, yoksa saf Python'da yapılır.
    
    Args:
        df: Fiyat verisi DataFrame'i (Close sütunu zorunlu)
    Returns:
        pd.DataFrame: İndikatör sütunları eklenmiş DataFrame
    """
    df = df.copy()
    prices = df["Close"].tolist()
    
    if _CPP_AVAILABLE:
        logger.debug("C++ motoru ile indikatörler hesaplanıyor...")
        
        # SMA & EMA
        sma_values = _cpp_module.calculate_sma(prices, 14)
        ema_values = _cpp_module.calculate_ema(prices, 14)
        df["SMA_14"] = sma_values
        df["EMA_14"] = ema_values
        
        # RSI
        rsi_values = _cpp_module.calculate_rsi(prices, 14)
        df["RSI_14"] = rsi_values
        
        # MACD
        macd_result = _cpp_module.calculate_macd(prices, 12, 26, 9)
        df["MACD"] = list(macd_result.macd_line)
        df["Signal"] = list(macd_result.signal_line)
        df["Histogram"] = list(macd_result.histogram)
        
        # C++ SMA sonuçlarında period'dan önceki değerler 0 olur — NaN yap
        df.loc[df["SMA_14"] == 0, "SMA_14"] = float("nan")
        df.loc[df["EMA_14"] == 0, "EMA_14"] = float("nan")
        df.loc[df["RSI_14"] == 0, "RSI_14"] = float("nan")
        
        # Add BB and ATR via Python fallback since C++ module doesn't have them yet
        from python_core.indicators import calculate_bbands, calculate_atr
        bb_df = calculate_bbands(df, column="Close")
        df = pd.concat([df, bb_df], axis=1)
        if all(c in df.columns for c in ["High", "Low", "Close"]):
            df['ATR_14'] = calculate_atr(df, window=14)
        else:
            df['ATR_14'] = 0.0
        
        return df
    else:
        # Python fallback — mevcut fonksiyonu kullan
        from python_core.indicators import add_all_indicators
        return add_all_indicators(df)
