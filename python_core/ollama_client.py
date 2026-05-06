"""
Ollama AI İstemcisi (Ollama Client)

Yerel olarak çalışan Ollama LLM servisine bağlanarak finansal analiz
yorumları ve AI içgörüleri üretir. Bu modül, pipeline sonuçlarını
alıp Ollama'ya gönderir ve doğal dilde analiz raporu döndürür.
"""

import requests
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Varsayılan Ayarlar ────────────────────────────────────────────────────────

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


# ── Yardımcı Fonksiyonlar ─────────────────────────────────────────────────────

def check_ollama_status() -> dict:
    """
    Ollama servisinin çalışıp çalışmadığını kontrol eder.
    
    Returns:
        dict: {"online": bool, "models": list[str], "error": str|None}
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            model_names = [m["name"] for m in data.get("models", [])]
            return {"online": True, "models": model_names, "error": None}
        return {"online": False, "models": [], "error": f"HTTP {resp.status_code}"}
    except requests.ConnectionError:
        return {"online": False, "models": [], "error": "Ollama servisi çalışmıyor. 'ollama serve' ile başlatın."}
    except Exception as e:
        return {"online": False, "models": [], "error": str(e)}


def list_available_models() -> list:
    """Ollama'da yüklü modelleri listeler."""
    status = check_ollama_status()
    return status.get("models", [])


# ── Ana Analiz Fonksiyonu ─────────────────────────────────────────────────────

def generate_ai_analysis(analysis_result: dict, model: str = DEFAULT_MODEL,
                         language: str = "tr") -> dict:
    """
    Pipeline'dan gelen analiz sonuçlarını Ollama LLM'e göndererek
    doğal dilde finansal yorum ve tavsiye üretir.
    
    Args:
        analysis_result (dict): pipeline.analyze_stock() çıktısı.
        model (str): Kullanılacak Ollama modeli (varsayılan: 'llama3').
        language (str): Yanıt dili ('tr' veya 'en').
        
    Returns:
        dict: {
            "ai_commentary": str,  -- AI'nın doğal dilde yorumu
            "model_used": str,     -- Kullanılan model adı
            "success": bool,       -- Başarılı mı?
            "error": str|None      -- Hata varsa açıklama
        }
    """
    # Ollama çevrimiçi mi kontrol et
    status = check_ollama_status()
    if not status["online"]:
        return {
            "ai_commentary": None,
            "model_used": model,
            "success": False,
            "error": status["error"]
        }
    
    # Prompt oluşturma
    symbol = analysis_result.get("symbol", "Bilinmiyor")
    last_price = analysis_result.get("last_price", "N/A")
    rsi = analysis_result.get("rsi", "N/A")
    macd = analysis_result.get("macd", "N/A")
    macd_signal = analysis_result.get("macd_signal", "N/A")
    signal = analysis_result.get("signal", "N/A")
    sma = analysis_result.get("sma_14", "N/A")
    ema = analysis_result.get("ema_14", "N/A")
    info = analysis_result.get("info", {})
    sector = info.get("sector", "Bilinmiyor")
    market_cap = info.get("marketCap", "N/A")

    if language == "tr":
        system_prompt = (
            "Sen deneyimli bir finansal analist ve borsa uzmanısın. "
            "Sana verilen teknik analiz verilerini inceleyerek kısa, net ve "
            "profesyonel bir yatırım değerlendirmesi yap. "
            "Yanıtını Türkçe olarak ver. Maksimum 200 kelime kullan."
        )
        user_prompt = f"""Aşağıdaki teknik analiz verilerini değerlendir:

Hisse: {symbol}
Sektör: {sector}
Piyasa Değeri: {market_cap}
Son Kapanış Fiyatı: {last_price}
SMA (14 gün): {sma}
EMA (14 gün): {ema}
RSI (14): {rsi}
MACD: {macd}
MACD Sinyal: {macd_signal}
Genel Sinyal: {signal}

Lütfen:
1. Mevcut teknik durumu özetle
2. Kısa vadeli (1-2 hafta) ve orta vadeli (1-3 ay) görüşünü belirt
3. Risk faktörlerini sırala
4. Net bir tavsiye ver (Al / Tut / Sat)
"""
    else:
        system_prompt = (
            "You are an experienced financial analyst. Analyze the given technical "
            "data and provide a concise, professional investment assessment. "
            "Maximum 200 words."
        )
        user_prompt = f"""Analyze the following technical data:

Stock: {symbol}
Sector: {sector}
Market Cap: {market_cap}
Last Close: {last_price}
SMA (14): {sma}
EMA (14): {ema}
RSI (14): {rsi}
MACD: {macd}
MACD Signal: {macd_signal}
Overall Signal: {signal}

Please:
1. Summarize the current technical situation
2. Short-term (1-2 weeks) and medium-term (1-3 months) outlook
3. Risk factors
4. Clear recommendation (Buy / Hold / Sell)
"""
    
    # Ollama API çağrısı
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "num_predict": 512,
                }
            },
            timeout=120
        )
        
        if resp.status_code == 200:
            data = resp.json()
            ai_message = data.get("message", {}).get("content", "")
            return {
                "ai_commentary": ai_message.strip(),
                "model_used": model,
                "success": True,
                "error": None
            }
        else:
            return {
                "ai_commentary": None,
                "model_used": model,
                "success": False,
                "error": f"Ollama API hatası: HTTP {resp.status_code} — {resp.text[:200]}"
            }
    except requests.Timeout:
        return {
            "ai_commentary": None,
            "model_used": model,
            "success": False,
            "error": "Ollama yanıt zaman aşımına uğradı (120s). Model çok büyük olabilir."
        }
    except Exception as e:
        return {
            "ai_commentary": None,
            "model_used": model,
            "success": False,
            "error": f"Beklenmeyen hata: {str(e)}"
        }


def generate_screening_summary(screening_results: list, model: str = DEFAULT_MODEL) -> dict:
    """
    Toplu tarama sonuçlarını AI'a gönderip genel bir piyasa değerlendirmesi alır.
    
    Args:
        screening_results (list): screen_summary() veya analyze_multiple() çıktıları.
        model (str): Kullanılacak Ollama modeli.
        
    Returns:
        dict: AI yorumunu içeren sonuç sözlüğü.
    """
    status = check_ollama_status()
    if not status["online"]:
        return {
            "ai_commentary": None,
            "model_used": model,
            "success": False,
            "error": status["error"]
        }
    
    # Tarama sonuçlarını tablo formatında hazırla
    lines = []
    for r in screening_results:
        if isinstance(r, dict):
            sym = r.get("symbol") or r.get("Sembol", "?")
            price = r.get("last_price") or r.get("Son Fiyat", "?")
            rsi = r.get("rsi") or r.get("RSI_14", "?")
            sig = r.get("signal") or r.get("Sinyal", "?")
            lines.append(f"  {sym}: Fiyat={price}, RSI={rsi}, Sinyal={sig}")
    
    summary_text = "\n".join(lines) if lines else "Veri yok"
    
    prompt = f"""Aşağıda birden fazla hisse senedinin teknik analiz özeti var.
Bu verilere bakarak genel bir piyasa değerlendirmesi yap (Türkçe, max 150 kelime):

{summary_text}

1. Piyasa genel trendi nedir?
2. En dikkat çekici fırsatlar hangileri?
3. Risk uyarıları nelerdir?
"""
    
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "Sen profesyonel bir finansal analistsin. Türkçe yanıt ver."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {"temperature": 0.4, "num_predict": 400}
            },
            timeout=120
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "ai_commentary": data.get("message", {}).get("content", "").strip(),
                "model_used": model,
                "success": True,
                "error": None
            }
        return {
            "ai_commentary": None,
            "model_used": model,
            "success": False,
            "error": f"HTTP {resp.status_code}"
        }
    except Exception as e:
        return {
            "ai_commentary": None,
            "model_used": model,
            "success": False,
            "error": str(e)
        }
