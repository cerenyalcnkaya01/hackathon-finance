# Borsa AI Botu - SolveX Hackathon 2026

![Hackathon Banner](https://nocodearea.com/wp-content/uploads/2024/01/nocodearea-logo-dark.png)

## 1. AMAÇ VE KAPSAM
Bu proje, **SolveX AI Hackathon 2026** kapsamında geliştirilmiş olup, Modern AI-Augmented Development metodolojisini temel alır. Sadece kod yazmayı değil, tüm yazılım geliştirme sürecini bir mühendislik disiplini ve yapay zeka entegrasyonu ile yönetmeyi amaçlamaktadır.

## 2. PROJE KONUSU VE BEKLENEN ÇIKTI
**Problem:** Finansal piyasalarda manuel veri analizi ve hisse tarama süreçlerinin yavaşlığı ve hata payının yüksekliği.
**Çözüm:** Masaüstü Yazılımı (C# WPF) + Python Backend + C++ Optimizasyon Katmanı.
**Temel Kriter:** Geliştirilen ürün, manuel finansal analizi minimize ederek AI ajanlarının (Ollama) otomasyon sürecindeki verimliliğini kanıtlar.

## 3. TAKIM YAPILANDIRMASI VE ROL DAĞILIMI
Proje süreci aşağıdaki rollerle yönetilmektedir:
- **Lead Developer / Maintainer:** GitHub Repository yönetimi, kod standartları denetimi ve PR onay süreçlerinden sorumludur.
- **Feature Developers (2 Kişi):** Belirlenen Issue’lar doğrultusunda modüler geliştirme, birim testleri ve kod iletiminden sorumludur.

## 4. VERSİYON KONTROL SİSTEMİ (GITHUB) STANDARTLARI
Proje geliştirme sürecinde **GitHub Flow** mimarisi benimsenmiştir.

- **Branching Strategy:** 
  - `main` dalı projenin dağıtıma hazır sürümünü temsil eder (Doğrudan push yapılamaz).
  - Her yeni özellik için `feature/görev-adi`, hata düzeltmeleri için `fix/hata-adi` dalları açılır.
- **Commit Mesajları:** Teknik ifadeler içeren, şimdiki zaman kipiyle yazılmış mesajlar (Örn: `feat: add user authentication layer`).
- **Merge:** Tüm birleştirme işlemleri Pull Request (PR) üzerinden, Code Review onayından sonra gerçekleştirilir.

## 5. AI-AUGMENTED DEVELOPMENT
Bu projede **Google Antigravity** ekosistemi tercih edilmiştir.

### 5.1. Agent Yapıları
- **Plan Agent:** Projenin mimari planı ([ARCHITECTURE.md](ARCHITECTURE.md)) ve yol haritası ([ROADMAP.md](ROADMAP.md)) bu ajan tarafından oluşturulmuştur.
- **Skills Agent:** Karmaşık algoritmalar ve veritabanı optimizasyonları gibi uzmanlık gerektiren kısımlarda AI, "Uzman Yazılımcı" rolüyle kullanılmıştır.

## 6. İŞ TAKİBİ VE DOKÜMANTASYON
- **GitHub Issues:** Her görev bir Issue olarak tanımlanmış ve ilgili geliştiriciye atanmıştır.
- **AI Traceability:** Kod dosyalarının başında veya PR açıklamalarında, AI ajanları (Plan/Skills) tarafından optimize edilen kısımlar not edilmiştir.
- **Final Review:** Proje tesliminden önce kodun tamamı Refactoring ve Optimization taramasından geçirilmiştir.

---

## Yazılım Geliştirme ve AI-Agentic Süreç Terimleri Sözlüğü

| Kategori | Terim | Teknik Açıklama |
| :--- | :--- | :--- |
| Versiyon Kontrol | Repository (Repo) | Proje dosyalarının ve geçmişinin saklandığı merkezi depo. |
| Versiyon Kontrol | Main | Projenin çalışan, stabil ve dağıtıma hazır en güncel ana dalı. |
| Versiyon Kontrol | Feature Branch | Yeni bir özellik geliştirmek için açılan bağımsız çalışma dalı. |
| Versiyon Kontrol | Pull Request (PR) | Kodun incelenmesi ve main’e dahil edilmesi için yapılan resmi talep. |
| Versiyon Kontrol | Code Review | Kodun kalite ve standartlar açısından ekip arkadaşı tarafından denetlenmesi. |
| AI Geliştirme | AI-Native IDE | Yapay zekanın editörün çekirdeğine entegre olduğu yeni nesil ortam (Antigravity vb.). |
| AI Geliştirme | Context-Aware | Yapay zekanın tüm proje mimarisini ve bağımlılıklarını bilmesi. |
| AI Geliştirme | .cursorrules | AI'ın uyacağı kodlama standartlarını belirleyen kurallar dosyası. |
| Agentic Workflow | Plan Agent | Teknik yol haritası ve görev dağılımı oluşturan üst akıl. |
| Agentic Workflow | Skills Agent | Belirli bir uzmanlık alanında (Finans, Güvenlik) özelleşmiş AI birimi. |
| Mühendislik | Refactoring | Kodun işlevini değiştirmeden temiz ve okunabilir hale getirilmesi. |
| Mühendislik | Traceability | Bir özelliğin hangi ihtiyaçla başladığının takip edilebilirliği. |

---
*Bu proje SolveX AI Hackathon 2026 teknik şartnamesine (nocodearea.com) tam uyumlulukla geliştirilmektedir.*
