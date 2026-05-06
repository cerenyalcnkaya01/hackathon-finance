# Proje Bağımlılıkları ve Kurulum Rehberi (DEPENDENCIES)

Bu belge, projenin farklı modülleri (Python, C++, C# ve AI) için gereken tüm kütüphaneleri, araçları ve yapay zeka modellerini listeler. İlerleyen aşamalarda `Dockerfile` ve `docker-compose.yml` hazırlanırken bu belge referans alınacaktır.

## 1. Python (Core Service) Bağımlılıkları
Aşağıdaki paketler Python ortamı için gereklidir:

```text
# Veri çekme ve analiz
yfinance>=0.2.0
pandas>=2.0.0
numpy>=1.24.0

# Grafik oluşturma
matplotlib>=3.7.0

# API sunucusu (Aşama 3: Ollama entegrasyonu ile birlikte kullanılacak)
fastapi>=0.100.0
uvicorn>=0.22.0

# Ollama ve HTTP istekleri
requests>=2.31.0

# C++ entegrasyonu (Aşama 4: pybind11 ile C++ modülleri bağlanacak)
pybind11>=2.11.0
```

**Kurulum:** `pip install -r requirements.txt` (İleride Docker içerisinde otomatik kurulacaktır)


## 2. C++ (Optimization Worker) Bağımlılıkları
C++ tarafı yüksek performanslı hesaplamalar (indikatör taramaları) yapacaktır.
- `CMake` (Derleme yapılandırması için - minimum v3.10)
- Modern bir C++ Derleyicisi (GCC, Clang veya MSVC - C++17 veya üzeri destekli)
- *Gerekirse:* `ZeroMQ` veya `gRPC` kütüphaneleri (Eğer pybind11 yerine mikroservis arası TCP/UDP haberleşmesi yapılacaksa)

## 3. C# (Kullanıcı Arayüzü - UI) Bağımlılıkları
Masaüstü arayüzü (.NET) için gerekenler:
- `.NET 8.0 SDK` veya daha güncel bir sürüm.
- **NuGet Paketleri:** 
  - `Newtonsoft.Json` veya `System.Text.Json` (Python'dan gelen verileri ayrıştırmak için)
  - Uygulama görselleştirmesi için (Örn: `LiveChartsCore` veya `OxyPlot` - Borsa grafikleri çizmek için).

## 4. Yapay Zeka Modeli (Ollama & LLM)
Sistem tamamen lokalde çalışacak şekilde tasarlandığı için aşağıdaki kurulumlar şarttır:

### A. Ollama Kurulumu (Motor)
1. [ollama.com](https://ollama.com/) adresinden Ollama yüklenmeli veya Docker üzerinden (`ollama/ollama` imajı ile) çalıştırılmalıdır.
2. Ollama servisi varsayılan olarak `http://localhost:11434` portundan hizmet verecektir.

### B. Dil Modeli (LLM) İndirme İşlemi
Analiz ve akıl yürütme (Reasoning) yeteneği yüksek, finansal mantığa yatkın bir model indirilmelidir. Terminalden şu komut çalıştırılarak model otomatik indirilebilir:
- `ollama pull llama3` (Genel kullanım için 8B model)
- *veya* `ollama pull mistral` 

### C. GGUF Modelleri (Manuel Yükleme)
Eğer internetten manuel olarak (örneğin HuggingFace üzerinden) özel bir `.gguf` modeli (örneğin finans üzerine fine-tune edilmiş bir model) indirilecekse:
1. İndirilen `.gguf` dosyası projedeki `models/` klasörü içerisine atılmalıdır (Bu klasör git tarafından yoksayılmaktadır).
2. Bu modeli Ollama içine aktarmak için bir `Modelfile` oluşturulup `FROM ./models/finans_modeli.gguf` yazılarak Ollama'ya entegre edilmelidir.

---
> **AI Traceability:** Bu doküman *Plan Agent* tarafından projenin altyapı gereksinimlerini haritalandırmak ve Dockerize sürecine ön hazırlık yapmak amacıyla oluşturulmuştur.
