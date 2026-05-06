# Borsa AI Botu - SolveX Hackathon 2026

Bu proje, SolveX AI Hackathon 2026 şartnamesine uygun olarak geliştirilen, "AI-Augmented Development" yaklaşımlarını benimseyen bir finansal analiz ve borsa tarama botudur.

## Proje Hakkında
Sistem;
1. Finansal verileri çeker (Python),
2. Yoğun hesaplamaları gerçekleştirir (C++),
3. Yapay Zeka (Ollama) ile karar destek yorumları üretir,
4. Modern bir kullanıcı arayüzünde (C#) bunları sunar.

## Kurulum ve Çalıştırma
*Not: Bu bölüm Docker entegrasyonu tamamlandığında güncellenecektir.*
Projeyi ayağa kaldırmak için `docker-compose up --build` komutu kullanılacaktır.

## Geliştirme Süreci
Lütfen geliştirmeye başlamadan önce [ARCHITECTURE.md](ARCHITECTURE.md) ve [ROADMAP.md](ROADMAP.md) dosyalarını okuyun.

### AI Ajanı Notları
Bu proje Google Antigravity kullanılarak **Plan Agent** ve **Skills Agent** mimarileriyle simüle edilmektedir. Lütfen yazdığınız kod bloklarına AI kullanımınıza dair `// AI Traceability: ...` yorumlarını eklemeyi unutmayın.
