"""
Borsa AI Bot — Ana Giriş Noktası (Main Entry Point)

Bu dosya tüm sistemi başlatır:
  1. Python modüllerini kontrol eder
  2. C++ motorunun durumunu raporlar
  3. Ollama AI bağlantısını kontrol eder
  4. FastAPI sunucusunu ayağa kaldırır

Kullanım:
    python main.py              # Sunucuyu başlat (port 8000)
    python main.py --port 9000  # Özel port
    python main.py --test       # Hızlı test (sunucu başlatmadan)
"""

import os
import sys
import argparse
import logging

# Proje kök dizinini path'e ekle
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Windows terminal unicode desteği
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_banner():
    """Başlangıç banner'ını yazdırır."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗  ██████╗ ██████╗ ███████╗ █████╗                   ║
║   ██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗                  ║
║   ██████╔╝██║   ██║██████╔╝███████╗███████║                  ║
║   ██╔══██╗██║   ██║██╔══██╗╚════██║██╔══██║                  ║
║   ██████╔╝╚██████╔╝██║  ██║███████║██║  ██║                  ║
║   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                  ║
║                                                              ║
║   █████╗ ██╗    ██████╗  ██████╗ ████████╗                   ║
║   ██╔══██╗██║    ██╔══██╗██╔═══██╗╚══██╔══╝                  ║
║   ███████║██║    ██████╔╝██║   ██║   ██║                     ║
║   ██╔══██║██║    ██╔══██╗██║   ██║   ██║                     ║
║   ██║  ██║██║    ██████╔╝╚██████╔╝   ██║                     ║
║   ╚═╝  ╚═╝╚═╝    ╚═════╝  ╚═════╝    ╚═╝                     ║
║                                                              ║
║   SolveX AI Hackathon 2026 — Borsa Analiz Botu              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_system():
    """Tüm sistem bileşenlerini kontrol eder ve durum raporu yazdırır."""
    print("\n" + "=" * 60)
    print("  SISTEM DURUM KONTROLU")
    print("=" * 60)

    # 1. Python modülleri
    print("\n[1/4] Python modülleri kontrol ediliyor...")
    modules_ok = True
    required = [
        ("python_core.data_fetcher", "Veri Çekme"),
        ("python_core.indicators", "İndikatörler"),
        ("python_core.charting", "Grafik"),
        ("python_core.pipeline", "Pipeline"),
        ("python_core.stock_screener", "Hisse Tarama"),
        ("python_core.ollama_client", "Ollama AI İstemcisi"),
        ("python_core.cpp_bridge", "C++ Köprüsü"),
    ]
    for mod_name, label in required:
        try:
            __import__(mod_name)
            print(f"  OK  {label} ({mod_name})")
        except ImportError as e:
            print(f"  HATA  {label} ({mod_name}): {e}")
            modules_ok = False

    # 2. C++ Motoru
    print("\n[2/4] C++ hesaplama motoru kontrol ediliyor...")
    from python_core.cpp_bridge import get_engine_info
    engine = get_engine_info()
    if engine["cpp_available"]:
        print(f"  OK  C++ motoru aktif ({engine['module_name']})")
    else:
        print(f"  UYARI  C++ derlenemiyor, Python fallback kullanilacak")
        print(f"         Derlemek icin: cd cpp_core && mkdir build && cd build && cmake .. && cmake --build .")

    # 3. Ollama AI
    print("\n[3/4] Ollama AI servisi kontrol ediliyor...")
    from python_core.ollama_client import check_ollama_status
    ai_status = check_ollama_status()
    if ai_status["online"]:
        print(f"  OK  Ollama cevrimici — Modeller: {', '.join(ai_status['models'][:5])}")
    else:
        print(f"  UYARI  Ollama cevrimdisi: {ai_status['error']}")
        print(f"         Baslatmak icin: ollama serve")

    # 4. Bağımlılıklar
    print("\n[4/4] Temel bağımlılıklar kontrol ediliyor...")
    deps = ["pandas", "numpy", "yfinance", "matplotlib", "fastapi", "uvicorn", "requests"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"  OK  {dep}")
        except ImportError:
            print(f"  EKSIK  {dep} — pip install {dep}")
            modules_ok = False

    print("\n" + "=" * 60)
    if modules_ok:
        print("  Tum kontroller basarili!")
    else:
        print("  Bazi bilesenler eksik — yukaridaki uyarilari kontrol edin.")
    print("=" * 60)

    return modules_ok


def run_quick_test():
    """Hızlı test — sunucu başlatmadan pipeline'ı dener."""
    print("\n" + "=" * 60)
    print("  HIZLI TEST — THYAO.IS Analizi")
    print("=" * 60)

    from python_core.pipeline import analyze_stock
    result = analyze_stock("THYAO.IS", period="1mo", save_chart=False, save_json=False)

    if "error" in result:
        print(f"\n  HATA: {result['error']}")
        return False

    print(f"\n  Sembol    : {result.get('symbol')}")
    print(f"  Son Fiyat : {result.get('last_price')}")
    print(f"  RSI (14)  : {result.get('rsi')}")
    print(f"  MACD      : {result.get('macd')}")
    print(f"  Sinyal    : {result.get('signal')}")

    # C++ bridge testi
    from python_core.cpp_bridge import get_engine_info
    engine = get_engine_info()
    print(f"\n  Motor     : {engine['engine']}")

    print("\n  Test basarili!")
    return True


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """FastAPI sunucusunu başlatır."""
    import uvicorn

    print(f"\n  FastAPI sunucusu baslatiliyor...")
    print(f"  Adres  : http://{host}:{port}")
    print(f"  Docs   : http://localhost:{port}/docs")
    print(f"  ReDoc  : http://localhost:{port}/redoc")
    print(f"  Durdurmak icin: Ctrl+C\n")

    uvicorn.run("api_server:app", host=host, port=port, reload=True)


def main():
    parser = argparse.ArgumentParser(description="Borsa AI Bot — Ana Giris Noktasi")
    parser.add_argument("--host", default="0.0.0.0", help="Sunucu adresi (varsayilan: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Sunucu portu (varsayilan: 8000)")
    parser.add_argument("--test", action="store_true", help="Hizli test calistir (sunucu baslatmadan)")
    parser.add_argument("--check", action="store_true", help="Sadece sistem kontrolu yap")
    args = parser.parse_args()

    print_banner()

    # Sistem kontrolü her zaman çalışır
    ok = check_system()

    if args.check:
        return

    if args.test:
        run_quick_test()
        return

    # Sunucuyu başlat
    if ok:
        start_server(host=args.host, port=args.port)
    else:
        print("\n  Kritik bilesenler eksik. Once bagimliliklari kurun:")
        print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()
