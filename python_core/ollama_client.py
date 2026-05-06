"""
Embedded AI İstemcisi

Önce Ollama'yı dener (llama3.1 / llama3). Ollama yoksa kural tabanlı
finansal analiz motoru ile akıllı, okunabilir Türkçe analiz üretir.
"""

import logging
import requests

logger = logging.getLogger(__name__)

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODELS = ["llama3.1", "llama3", "mistral", "gemma2", "phi3"]

_ollama_available = None  # None = henüz test edilmedi

# ─── Ollama Bağlantı ──────────────────────────────────────────────────────────

def _check_ollama() -> tuple[bool, str]:
    """Ollama'nın çalışıp çalışmadığını ve kullanılabilir modeli döndürür."""
    global _ollama_available
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"].split(":")[0] for m in r.json().get("models", [])]
            for preferred in OLLAMA_MODELS:
                if preferred in models:
                    _ollama_available = (True, preferred)
                    return True, preferred
            if models:
                _ollama_available = (True, models[0])
                return True, models[0]
    except Exception:
        pass
    _ollama_available = (False, "")
    return False, ""


def _ollama_generate(prompt: str, model: str) -> str | None:
    """Ollama API'sine istek atar ve yanıtı döndürür."""
    try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sen uzman bir finansal analistsin. "
                        "Verilen hisse verilerini Türkçe olarak yorumla. "
                        "Kısa, net ve profesyonel yaz. "
                        "Mutlaka AL / SAT / TUT tavsiyesi ver."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 300}
        }
        r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=60)
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.warning(f"Ollama hatası: {e}")
    return None


# ─── Kural Tabanlı Analiz Motoru ─────────────────────────────────────────────

def _rule_based_analysis(symbol: str, last_price, rsi, macd, signal: str, sector: str) -> str:
    """
    RSI + MACD + sinyal değerlerine göre zengin, okunabilir Türkçe analiz üretir.
    """
    lines = []

    # — RSI yorumu —
    try:
        rsi_val = float(rsi)
        if rsi_val <= 30:
            rsi_comment = (
                f"RSI {rsi_val:.1f} seviyesinde olup aşırı satım bölgesindedir. "
                "Bu durum, hissenin kısa vadede teknik bir toparlanma potansiyeli taşıdığına işaret eder."
            )
            rsi_signal = "AL"
        elif rsi_val >= 70:
            rsi_comment = (
                f"RSI {rsi_val:.1f} ile aşırı alım bölgesine girmiş durumda. "
                "Momentum yavaşlayabilir ve kısa vadeli bir düzeltme riski bulunmaktadır."
            )
            rsi_signal = "SAT"
        elif rsi_val >= 55:
            rsi_comment = (
                f"RSI {rsi_val:.1f} ile güçlü momentum bölgesinde seyrediyor. "
                "Alıcı baskısı devam etmektedir."
            )
            rsi_signal = "TUT"
        elif rsi_val <= 45:
            rsi_comment = (
                f"RSI {rsi_val:.1f} ile zayıf momentum görülmektedir. "
                "Satıcı baskısı baskın olabilir."
            )
            rsi_signal = "TUT/İZLE"
        else:
            rsi_comment = (
                f"RSI {rsi_val:.1f} ile nötr bölgede bulunuyor. "
                "Net bir yön sinyali üretilmemiş."
            )
            rsi_signal = "TUT"
    except Exception:
        rsi_comment = "RSI verisi hesaplanamadı."
        rsi_signal = "TUT"
        rsi_val = 50.0

    # — MACD yorumu —
    try:
        macd_val = float(macd)
        if macd_val > 0:
            macd_comment = (
                f"MACD {macd_val:.4f} ile pozitif bölgede. "
                "Orta vadeli trend yukarı yönlü devam etmektedir."
            )
            macd_signal = "AL"
        elif macd_val < 0:
            macd_comment = (
                f"MACD {macd_val:.4f} ile negatif bölgede. "
                "Trend aşağı yönlü baskı altında."
            )
            macd_signal = "SAT"
        else:
            macd_comment = "MACD sıfır çizgisine yakın, trend belirsiz."
            macd_signal = "TUT"
    except Exception:
        macd_comment = "MACD verisi hesaplanamadı."
        macd_signal = "TUT"
        macd_val = 0.0

    # — Sektör notu —
    sector_note = ""
    if sector and sector not in ("Bilinmiyor", "Unknown", ""):
        sector_note = f"{sector} sektöründe faaliyet gösteren "
    else:
        sector_note = ""

    # — Tavsiye belirleme —
    buy_count  = [rsi_signal, macd_signal].count("AL")
    sell_count = [rsi_signal, macd_signal].count("SAT")

    if buy_count >= 2:
        tavsiye = "✅ AL"
        tavsiye_aciklama = "Teknik göstergeler birlikte AL sinyali üretiyor."
    elif sell_count >= 2:
        tavsiye = "🔴 SAT"
        tavsiye_aciklama = "Teknik göstergeler birlikte SAT sinyali üretiyor."
    elif buy_count == 1 and sell_count == 0:
        tavsiye = "📊 ZAYIF AL"
        tavsiye_aciklama = "Bir gösterge AL, diğerleri nötr. Dikkatli pozisyon alınabilir."
    elif sell_count == 1 and buy_count == 0:
        tavsiye = "⚠️ ZAYIF SAT"
        tavsiye_aciklama = "Bir gösterge SAT, diğerleri nötr. Stop-loss önerilir."
    else:
        tavsiye = "⏸ TUT"
        tavsiye_aciklama = "Göstergeler çelişkili. Daha net sinyal oluşana kadar bekle."

    # — Metin oluşturma —
    lines.append(
        f"{sector_note}{symbol} hissesi şu anda {last_price} TL/USD seviyesinde işlem görmektedir.\n"
    )
    lines.append(f"📌 RSI Analizi: {rsi_comment}\n")
    lines.append(f"📌 MACD Analizi: {macd_comment}\n")

    if signal and signal != "?":
        lines.append(f"📌 Sistem Sinyali: {signal}\n")

    lines.append(f"\n🏷 Tavsiye: {tavsiye}\n{tavsiye_aciklama}")

    return "\n".join(lines)


def _rule_based_summary(stock_signals: list[dict]) -> str:
    """Hisse sinyallerine bakarak piyasa özeti oluşturur."""
    if not stock_signals:
        return "Yeterli veri bulunamadı."

    al  = sum(1 for s in stock_signals if "al" in s.get("signal", "").lower() or "buy" in s.get("signal", "").lower())
    sat = sum(1 for s in stock_signals if "sat" in s.get("signal", "").lower() or "sell" in s.get("signal", "").lower())
    top = len(stock_signals)
    notr = top - al - sat

    if al > sat * 1.5:
        genel = "OLUMLU 📈 — Alım sinyalleri baskın. Piyasada yükseliş momentumu gözlemleniyor."
    elif sat > al * 1.5:
        genel = "OLUMSUZ 📉 — Satış sinyalleri baskın. Piyasada düşüş baskısı mevcut."
    else:
        genel = "KARIŞIK ↔ — Piyasa karma sinyaller veriyor. Seçici olunması öneriliyor."

    lines = [
        f"📊 Piyasa Özeti ({top} hisse analiz edildi):",
        f"  • AL Sinyali  : {al} hisse",
        f"  • SAT Sinyali : {sat} hisse",
        f"  • Nötr        : {notr} hisse",
        f"\n🔎 Genel Görünüm: {genel}"
    ]

    # En güçlü 3 hisseyi listele
    top3 = stock_signals[:3]
    if top3:
        lines.append("\n🌟 Öne Çıkan Hisseler:")
        for s in top3:
            lines.append(f"  • {s.get('symbol','?')} — {s.get('signal','?')}")

    return "\n".join(lines)


# ─── Dışa Açık Fonksiyonlar ──────────────────────────────────────────────────

def check_ollama_status() -> dict:
    ok, model = _check_ollama()
    if ok:
        return {"online": True, "models": [model], "error": None, "mode": "ollama"}
    return {"online": True, "models": ["Kural Tabanlı Motor"], "error": None, "mode": "rule_based"}


def list_available_models() -> list:
    ok, model = _check_ollama()
    if ok:
        return [model, "Kural Tabanlı Motor (Yedek)"]
    return ["Kural Tabanlı Motor"]


def generate_ai_analysis(analysis_result: dict, model: str = "embedded", language: str = "tr") -> dict:
    symbol     = analysis_result.get("symbol", "?")
    last_price = analysis_result.get("last_price", "?")
    rsi        = analysis_result.get("rsi", "?")
    macd       = analysis_result.get("macd", "?")
    signal     = analysis_result.get("signal", "?")
    info       = analysis_result.get("info", {})
    sector     = info.get("sector", "Bilinmiyor") if isinstance(info, dict) else "Bilinmiyor"

    # — Önce Ollama dene —
    ok, ollama_model = _check_ollama()
    if ok:
        prompt = (
            f"Hisse: {symbol}\n"
            f"Fiyat: {last_price}\n"
            f"RSI: {rsi}\n"
            f"MACD: {macd}\n"
            f"Sinyal: {signal}\n"
            f"Sektör: {sector}\n\n"
            "Bu verilere göre 3-4 cümle Türkçe analiz yap ve AL / SAT / TUT tavsiyesi ver."
        )
        result = _ollama_generate(prompt, ollama_model)
        if result:
            return {"ai_commentary": result, "success": True, "error": None, "source": "ollama"}

    # — Ollama yoksa kural tabanlı —
    commentary = _rule_based_analysis(symbol, last_price, rsi, macd, signal, sector)
    return {"ai_commentary": commentary, "success": True, "error": None, "source": "rule_based"}


def generate_screening_summary(screening_results: list, model: str = "embedded") -> dict:
    if not screening_results:
        return {"ai_commentary": "Tarama sonucu bulunamadı.", "success": True, "error": None}

    # — Önce Ollama dene —
    ok, ollama_model = _check_ollama()
    if ok:
        lines = []
        for r in screening_results[:12]:
            sym = r.get("symbol") or r.get("Sembol", "?")
            sig = r.get("signal") or r.get("Sinyal", "?")
            lines.append(f"{sym}: {sig}")
        summary_text = ", ".join(lines)
        prompt = (
            f"Şu hisselerin teknik sinyalleri: {summary_text}\n\n"
            "Bu sinyallere göre piyasanın genel durumunu Türkçe olarak 3-4 cümle ile özetle."
        )
        result = _ollama_generate(prompt, ollama_model)
        if result:
            return {"ai_commentary": result, "success": True, "error": None, "source": "ollama"}

    # — Kural tabanlı —
    mapped = [{"symbol": r.get("symbol") or r.get("Sembol", "?"),
               "signal": r.get("signal") or r.get("Sinyal", "?")}
              for r in screening_results]
    commentary = _rule_based_summary(mapped)
    return {"ai_commentary": commentary, "success": True, "error": None, "source": "rule_based"}
