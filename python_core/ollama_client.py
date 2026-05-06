"""
Embedded AI İstemcisi (llama-cpp-python)

Yerel GGUF modelini doğrudan yükleyerek çalışır. Ollama servisinin 
arkada çalışmasına gerek duymaz.
"""

import os
import logging
from typing import Optional
from llama_cpp import Llama

logger = logging.getLogger(__name__)

# ── Model Ayarları ────────────────────────────────────────────────────────────

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, "models", "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")

# Global model örneği (Lazy loading)
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model dosyası bulunamadı: {MODEL_PATH}")
            return None
        
        logger.info(f"Model yükleniyor: {MODEL_PATH}...")
        try:
            # GPU varsa kullanmaya çalış (n_gpu_layers=-1), yoksa CPU (0)
            _llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0, # Hackathon ortamında CPU daha güvenli
                verbose=False
            )
            logger.info("Model başarıyla yüklendi.")
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            return None
    return _llm

# ── Yardımcı Fonksiyonlar ─────────────────────────────────────────────────────

def check_ollama_status() -> dict:
    """Ollama yerine artık yerel model durumunu kontrol eder."""
    if os.path.exists(MODEL_PATH):
        return {"online": True, "models": ["Llama-3.1-8B-Embedded"], "error": None}
    return {"online": False, "models": [], "error": "Model dosyası bulunamadı."}

def list_available_models() -> list:
    return ["Llama-3.1-8B-Embedded"] if os.path.exists(MODEL_PATH) else []

# ── Ana Analiz Fonksiyonu ─────────────────────────────────────────────────────

def generate_ai_analysis(analysis_result: dict, model: str = "embedded",
                         language: str = "tr") -> dict:
    llm = get_llm()
    if not llm:
        return {
            "ai_commentary": None,
            "success": False,
            "error": "Model yüklenemedi veya dosya eksik."
        }
    
    # Prompt hazırlama (Llama 3 formatı)
    symbol = analysis_result.get("symbol", "?")
    last_price = analysis_result.get("last_price", "?")
    rsi = analysis_result.get("rsi", "?")
    macd = analysis_result.get("macd", "?")
    signal = analysis_result.get("signal", "?")
    info = analysis_result.get("info", {})
    sector = info.get("sector", "Bilinmiyor")

    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n" \
             f"Sen profesyonel bir finansal analistsin. Verilen teknik verileri Türkçe olarak yorumla. <|eot_id|>" \
             f"<|start_header_id|>user<|end_header_id|>\n\n" \
             f"Hisse: {symbol}, Sektör: {sector}, Fiyat: {last_price}, RSI: {rsi}, MACD: {macd}, Sinyal: {signal}. " \
             f"Kısa bir değerlendirme ve Al/Tut/Sat tavsiyesi ver. <|eot_id|>" \
             f"<|start_header_id|>assistant<|end_header_id|>\n\n"

    try:
        output = llm(prompt, max_tokens=256, stop=["<|eot_id|>"], echo=False)
        text = output["choices"][0]["text"].strip()
        return {
            "ai_commentary": text,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "ai_commentary": None,
            "success": False,
            "error": str(e)
        }

def generate_screening_summary(screening_results: list, model: str = "embedded") -> dict:
    llm = get_llm()
    if not llm:
        return {"ai_commentary": None, "success": False, "error": "Model hatası"}
    
    lines = []
    for r in screening_results:
        sym = r.get("symbol") or r.get("Sembol", "?")
        sig = r.get("signal") or r.get("Sinyal", "?")
        lines.append(f"{sym}: {sig}")
    
    summary_text = ", ".join(lines)
    
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n" \
             f"Piyasa özetini Türkçe yorumla. <|eot_id|>" \
             f"<|start_header_id|>user<|end_header_id|>\n\n" \
             f"Şu hisseleri değerlendir: {summary_text} <|eot_id|>" \
             f"<|start_header_id|>assistant<|end_header_id|>\n\n"

    try:
        output = llm(prompt, max_tokens=200, stop=["<|eot_id|>"])
        return {
            "ai_commentary": output["choices"][0]["text"].strip(),
            "success": True,
            "error": None
        }
    except Exception as e:
        return {"ai_commentary": None, "success": False, "error": str(e)}
