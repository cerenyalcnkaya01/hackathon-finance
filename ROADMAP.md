# Geliştirme Yol Haritası (ROADMAP)

> **Oluşturan:** Plan Agent (AI)
> **Tarih:** 2026-05-06

Aşağıdaki yol haritası, 3 kişilik geliştirici ekibi ve AI ajanlarının işbirliği ile tamamlanacaktır. Takım lideri Issue'ları açarak görev atamalarını yapacaktır.

## Aşama 1: Temel Kurulum (Setup) - [Tamamlandı]
- [x] GitHub Repository oluşturulması.
- [x] `.gitignore`, `.cursorrules` ve mimari dokümanların (`ARCHITECTURE.md`, `ROADMAP.md`) oluşturulması.
- [x] GitHub Issue şablonlarının hazırlanması.

## Aşama 2: Veri Çekme ve Analiz Modülü (Python) - [Bekliyor]
- [ ] Borsa verilerini çekmek için Python scriptlerinin (örn. `yfinance` ile) hazırlanması.
- [x] Temel teknik analiz indikatörlerinin (RSI, MACD, MA) hesaplanması.
- **AI Katkısı (Skills Agent):** İndikatör hesaplama algoritmalarının optimizasyonu.

## Aşama 3: AI Model Entegrasyonu (Ollama) - [Bekliyor]
- [ ] Local Ollama kurulumu (örn. Llama 3 veya finansal modeller).
- [ ] Python üzerinden Ollama API'sine bağlanılması.
- [ ] Hisse verilerini analiz etmek üzere uygun Prompt Engineering yapılması.
- **AI Katkısı (Skills Agent):** LLM'e gidecek promptların tasarlanması.

## Aşama 4: Performans Optimizasyonu (C++) - [Bekliyor]
- [ ] Python'da yavaş çalışan tarama döngülerinin C++'a taşınması (pybind11 veya gRPC).
- [ ] C++ kodunun derlenip Python içerisinden çağrılması.

## Aşama 5: Kullanıcı Arayüzü (C#) - [Bekliyor]
- [ ] C# ile masaüstü (veya Web) arayüzü oluşturulması.
- [ ] Python API'si ile C# arayüzü arasında HTTP/WebSocket bağlantısı kurulması.
- [ ] Kullanıcının hisse kriterlerini girmesi ve analiz sonuçlarını/AI yorumlarını ekranda görmesi.

## Aşama 6: Docker ve Dağıtım (Deployment) - [Bekliyor]
- [ ] Tüm servislerin (Python API, Ollama, C++ Worker) Dockerfile'larının yazılması.
- [ ] `docker-compose.yml` dosyasının oluşturulması ve tek tuşla ayağa kaldırılabilir hale getirilmesi.
- **AI Katkısı:** Dockerfile ve Compose optimizasyonları (Refactoring).
