# Proje Mimarisi (ARCHITECTURE)

> **Oluşturan:** Plan Agent (AI)
> **Tarih:** 2026-05-06

## 1. Genel Bakış
Bu proje, borsa hisselerini belirli kriterlere göre tarayan, analiz eden ve yerel bir LLM (Ollama) ile kararlar destekleyen yapay zeka destekli bir borsa botudur. 
Uygulama mikroservis/modüler bir mimari benimsenerek tasarlanmıştır.

## 2. Sistem Bileşenleri

### 2.1. Python Core Service (Veri ve AI Katmanı)
- **Görev:** Piyasa verilerini çekmek, indikatör hesaplamalarını yapmak ve Ollama modeline prompt göndererek analiz sonuçlarını almak.
- **Teknoloji:** Python 3.10+, FastAPI (servisleşme için), Pandas, yfinance/ccxt (veri kaynağına göre).

### 2.2. C++ Optimization Worker (Performans Katmanı)
- **Görev:** Çok yüksek miktarda anlık veriyi taramak veya özel algoritmaları (örn. karmaşık pattern matching) hızlı bir şekilde çalıştırmak.
- **Teknoloji:** Modern C++, ZeroMQ veya gRPC (Python ile haberleşme için).

### 2.3. C# UI Client (Kullanıcı Arayüzü)
- **Görev:** Son kullanıcıya analiz sonuçlarını sunmak, tarama kriterlerini girmesini sağlamak.
- **Teknoloji:** C# (.NET 8/9), WPF veya WinUI 3.

### 2.4. AI Entegrasyonu (Ollama)
- **Görev:** "Skills Agent" simülasyonu kapsamında, taranan verilerin finansal analizini yapmak ve kullanıcıya doğal dilde içgörüler sunmak.

## 3. GitHub Flow ve Branch Stratejisi
- `main`: Sadece kararlı sürümlerin bulunduğu, PR ile kod kabul eden ana branch.
- `feature/*`: Yeni bileşenler geliştirilirken (Örn: `feature/python-fastapi-setup`).
- `fix/*`: Hata düzeltmeleri.

## 4. Docker Mimarisi
Finalde sistem `docker-compose.yml` kullanılarak ayağa kaldırılacaktır.
- `bot-api`: Python backend konteyneri
- `ui-client`: (Gerekirse web UI'a dönüştürülürse konteyner, C# masaüstü ise local çalışır)
- `ollama-service`: Ollama'nın çalıştığı AI konteyneri
