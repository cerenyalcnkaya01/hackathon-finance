import pandas as pd
import matplotlib.pyplot as plt

# AÇIKLAMA:
# Bu modül, veri çekme (yfinance vb.) modülü tamamlandığında onunla birleştirilecektir.
# Şimdilik hazır indikatörleri içeren bir pandas DataFrame'i bekleyecek şekilde tasarlanmıştır.
# İlerleyen aşamalarda bu grafikler; ya resim dosyası olarak (PNG) kaydedilip C# arayüzüne gönderilebilir,
# ya da C# arayüzü kendi grafik kütüphanelerini kullanmak isterse sadece JSON verisi dönülecek şekilde revize edilebilir.

def plot_indicators(df: pd.DataFrame, symbol: str = "Hisse", output_path: str = None):
    """
    Fiyat verilerini ve hesaplanan indikatörleri (RSI, MACD, MA) tek bir grafikte çizer.
    Veri çekme scripti hazır olduğunda bu fonksiyon entegre edilerek canlı veya geçmiş veri üzerinden çalıştırılacaktır.
    
    Args:
        df (pd.DataFrame): 'Close', 'SMA_14', 'RSI_14', 'MACD', 'Signal', 'Histogram' 
                           sütunlarını içeren veri çerçevesi.
        symbol (str): Grafiği çizilecek hissenin sembolü (Örn: "AAPL", "THYAO.IS").
        output_path (str, optional): Grafik dosyaya kaydedilmek istenirse dosya yolu (Örn: 'chart.png').
                                     Belirtilmezse ekranda gösterilir.
    """
    # Gerekli sütunların varlığını kontrol et
    required_columns = ['Close', 'SMA_14', 'RSI_14', 'MACD', 'Signal']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Eksik sütun: {col}. Lütfen grafiği çizmeden önce indikatörleri hesaplayın.")
            
    # Figür ve alt grafikleri (subplots) oluştur
    # 3 satır: 1. Fiyat ve MA, 2. RSI, 3. MACD
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
    fig.suptitle(f"{symbol} Teknik Analiz Grafiği", fontsize=16)
    
    # 1. Fiyat ve Hareketli Ortalama (SMA)
    ax1.plot(df.index, df['Close'], label='Kapanış Fiyatı', color='black', linewidth=1.5)
    ax1.plot(df.index, df['SMA_14'], label='SMA (14)', color='blue', linestyle='--')
    ax1.set_title("Fiyat ve Hareketli Ortalama")
    ax1.set_ylabel("Fiyat")
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 2. RSI (Göreceli Güç Endeksi)
    ax2.plot(df.index, df['RSI_14'], label='RSI (14)', color='purple')
    ax2.axhline(70, color='red', linestyle='--', alpha=0.5)  # Aşırı alım bölgesi
    ax2.axhline(30, color='green', linestyle='--', alpha=0.5) # Aşırı satım bölgesi
    ax2.set_title("RSI (Relative Strength Index)")
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # 3. MACD
    ax3.plot(df.index, df['MACD'], label='MACD Line', color='blue')
    ax3.plot(df.index, df['Signal'], label='Signal Line', color='orange')
    
    # Histogram için renk belirleme: pozitifler yeşil, negatifler kırmızı
    colors = ['green' if val >= 0 else 'red' for val in df['Histogram']]
    ax3.bar(df.index, df['Histogram'], color=colors, alpha=0.5, label='Histogram')
    
    ax3.set_title("MACD (Moving Average Convergence Divergence)")
    ax3.set_ylabel("MACD")
    ax3.set_xlabel("Tarih")
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    
    # Grafiği düzenle ve sıkıştır
    plt.tight_layout()
    
    # Ekranda göster veya dosyaya kaydet
    if output_path:
        plt.savefig(output_path)
        print(f"Grafik '{output_path}' konumuna kaydedildi.")
    else:
        plt.show()
        
    plt.close()

# TEST KULLANIMI İÇİN ÖRNEK (Çalıştırıldığında)
if __name__ == "__main__":
    print("Bu modül, veri çekme modülü hazırlandığında dışarıdan çağrılmak üzere tasarlanmıştır.")
    print("Örnek kullanım: plot_indicators(df_with_indicators, 'THYAO.IS', 'test_grafik.png')")
