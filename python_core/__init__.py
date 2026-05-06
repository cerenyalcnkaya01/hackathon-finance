# python_core module
"""
Borsa AI Bot — Python Core Paketi

Bu paket, finansal veri çekme, teknik indikatör hesaplama,
grafik oluşturma, hisse tarama ve AI analiz modüllerini içerir.
Tüm modüller bu paket altından import edilerek kullanılır.
"""

from python_core.data_fetcher import (
    fetch_historical_data,
    fetch_recent_data,
    get_stock_info,
)

from python_core.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    add_all_indicators,
)

from python_core.charting import plot_indicators

from python_core.stock_screener import (
    screen_by_rsi,
    screen_by_macd_crossover,
    screen_summary,
    BIST_30,
    US_TECH,
)

from python_core.pipeline import (
    analyze_stock,
    analyze_multiple,
)

from python_core.ollama_client import (
    check_ollama_status,
    generate_ai_analysis,
    generate_screening_summary,
    list_available_models,
)

from python_core.cpp_bridge import (
    is_cpp_available,
    get_engine_info,
    calculate_sma_fast,
    calculate_ema_fast,
    calculate_rsi_fast,
    calculate_macd_fast,
    add_all_indicators_fast,
)

__all__ = [
    # Data Fetcher
    "fetch_historical_data",
    "fetch_recent_data",
    "get_stock_info",
    # Indicators
    "calculate_sma",
    "calculate_ema",
    "calculate_rsi",
    "calculate_macd",
    "add_all_indicators",
    # Charting
    "plot_indicators",
    # Stock Screener
    "screen_by_rsi",
    "screen_by_macd_crossover",
    "screen_summary",
    "BIST_30",
    "US_TECH",
    # Pipeline
    "analyze_stock",
    "analyze_multiple",
    # Ollama AI
    "check_ollama_status",
    "generate_ai_analysis",
    "generate_screening_summary",
    "list_available_models",
    # C++ Bridge
    "is_cpp_available",
    "get_engine_info",
    "calculate_sma_fast",
    "calculate_ema_fast",
    "calculate_rsi_fast",
    "calculate_macd_fast",
    "add_all_indicators_fast",
]
