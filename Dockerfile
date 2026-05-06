# Python 3.11 tabanlı imaj
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (C++ derleme için)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm kodu kopyala
COPY . .

# C++ Motorunu derle
RUN cd cpp_core && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    cp *.so ../../python_core/ || true

# Çıkış portu
EXPOSE 8000

# Uygulamayı başlat
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
