# Borsa AI Bot — Çalıştırma Kılavuzu

Bu proje artık tamamen Dockerize edilmiştir ve tek bir EXE dosyası ile yönetilebilir.

## Gereksinimler
- **Docker Desktop**: Bilgisayarınızda Docker yüklü ve çalışır durumda olmalıdır.
- **Internet Bağlantısı**: İlk çalıştırmada Docker imajlarının indirilmesi için gereklidir.

## Nasıl Çalıştırılır?

### Yöntem 1: Tek Tıkla (Önerilen)
1. Ana dizindeki `dist/BorsaAI_Launcher.exe` dosyasını çalıştırın.
2. Launcher şunları yapacaktır:
   - Docker servislerini (`api` ve `ollama`) arka planda başlatır.
   - API hazır olana kadar bekler.
   - Varsayılan tarayıcınızda Dashboard'u açar (`http://localhost:8000`).

### Yöntem 2: Docker Compose (Manuel)
Eğer terminal kullanmak isterseniz:
```bash
docker-compose up -d
```
Ardından tarayıcıdan `http://localhost:8000` adresine gidin.

## Mimari Hakkında
- **Backend**: FastAPI (Python), C++ Core (hesaplama motoru).
- **Frontend**: Premium Web Dashboard (HTML5/JS/CSS).
- **AI**: Ollama (Llama 3.1).
- **Konteynerizasyon**: Docker & Docker Compose.

---
*SolveX AI Hackathon 2026 Projesidir.*
