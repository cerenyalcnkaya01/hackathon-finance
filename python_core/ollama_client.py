"""
Embedded AI İstemcisi (Transformers)

Yerel HuggingFace modellerini (örn. TinyLlama) doğrudan yükleyerek çalışır.
Ollama veya llama.cpp'ye gerek duymaz. "kodla beraber" çalışır.
"""

import os
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# Global model örneği (Lazy loading)
_ai_pipeline = None

def get_llm():
    global _ai_pipeline
    if _ai_pipeline is None:
        logger.info("Local AI (Transformers) yükleniyor... Bu işlem ilk seferde biraz zaman alabilir (model indiriliyor).")
        try:
            # Daha hızlı ve küçük bir model seçiyoruz. 
            # İsteğe bağlı olarak "Qwen/Qwen1.5-0.5B-Chat" veya "TinyLlama/TinyLlama-1.1B-Chat-v1.0" kullanılabilir.
            # sentiment-analysis de kullanılabilir ama metin üretimi istendiği için text-generation kullanıyoruz.
            _ai_pipeline = pipeline(
                "text-generation", 
                model="Qwen/Qwen1.5-0.5B-Chat", 
                device_map="auto" # GPU varsa kullan, yoksa CPU
            )
            logger.info("Local AI başarıyla yüklendi.")
        except Exception as e:
            logger.error(f"Local AI yükleme hatası: {e}")
            return None
    return _ai_pipeline

def check_ollama_status() -> dict:
    """Yapay zeka durumunu kontrol eder."""
    try:
        # Pipeline test
        get_llm()
        return {"online": True, "models": ["Qwen1.5-0.5B-Chat (Local)"], "error": None}
    except Exception as e:
        return {"online": False, "models": [], "error": str(e)}

def list_available_models() -> list:
    return ["Qwen1.5-0.5B-Chat (Local)"]

def generate_ai_analysis(analysis_result: dict, model: str = "embedded", language: str = "tr") -> dict:
    llm = get_llm()
    if not llm:
        return {"ai_commentary": None, "success": False, "error": "AI model yüklenemedi."}
    
    symbol = analysis_result.get("symbol", "?")
    last_price = analysis_result.get("last_price", "?")
    rsi = analysis_result.get("rsi", "?")
    macd = analysis_result.get("macd", "?")
    signal = analysis_result.get("signal", "?")
    info = analysis_result.get("info", {})
    sector = info.get("sector", "Bilinmiyor")

    prompt = (
        f"Sen bir finansal analistsin. Aşağıdaki verileri kısaca yorumla ve Al/Sat/Tut tavsiyesi ver.\n"
        f"Hisse: {symbol}\nFiyat: {last_price}\nRSI: {rsi}\nMACD: {macd}\nSinyal: {signal}\n"
        f"Yorum (Türkçe):"
    )

    try:
        # Prompt'u Qwen chat formatına uygun verebiliriz
        messages = [
            {"role": "system", "content": "Sen profesyonel bir finansal analistsin. Sadece Türkçe yanıt ver."},
            {"role": "user", "content": prompt}
        ]
        
        output = llm(messages, max_new_tokens=150, do_sample=True, temperature=0.3)
        text = output[0]["generated_text"][-1]["content"] if isinstance(output[0]["generated_text"], list) else output[0]["generated_text"]
        
        return {
            "ai_commentary": str(text).strip(),
            "success": True,
            "error": None
        }
    except Exception as e:
        return {"ai_commentary": None, "success": False, "error": str(e)}

def generate_screening_summary(screening_results: list, model: str = "embedded") -> dict:
    llm = get_llm()
    if not llm:
        return {"ai_commentary": None, "success": False, "error": "Model hatası"}
    
    lines = []
    for r in screening_results[:10]: # En fazla 10 hisseyi gönder
        sym = r.get("symbol") or r.get("Sembol", "?")
        sig = r.get("signal") or r.get("Sinyal", "?")
        lines.append(f"{sym}: {sig}")
    
    summary_text = ", ".join(lines)
    prompt = f"Şu hisselerin teknik sinyallerine göre piyasanın genel durumunu Türkçe olarak kısaca özetle: {summary_text}"
    
    try:
        messages = [
            {"role": "system", "content": "Sen bir piyasa analistisin. Verilen hisse sinyallerini özetle."},
            {"role": "user", "content": prompt}
        ]
        output = llm(messages, max_new_tokens=150, do_sample=True, temperature=0.3)
        text = output[0]["generated_text"][-1]["content"] if isinstance(output[0]["generated_text"], list) else output[0]["generated_text"]
        
        return {
            "ai_commentary": str(text).strip(),
            "success": True,
            "error": None
        }
    except Exception as e:
        return {"ai_commentary": None, "success": False, "error": str(e)}
