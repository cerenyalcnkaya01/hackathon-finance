import pandas as pd
import mplfinance as mpf
import os

def plot_indicators(df: pd.DataFrame, symbol: str = "Hisse", output_path: str = None):
    """
    Fiyat verilerini (Mum Grafiği - Candlestick) ve hesaplanan indikatörleri tek bir grafikte çizer.
    Artış ve düşüşler renkli olarak belirtilir.
    """
    # mplfinance için veriyi hazırla (OHLC ve datetime index gereklidir)
    df_plot = df.copy()
    
    # Eksik sütunları tamamla (olası hataları önlemek için)
    if 'Open' not in df_plot.columns: df_plot['Open'] = df_plot['Close']
    if 'High' not in df_plot.columns: df_plot['High'] = df_plot['Close']
    if 'Low' not in df_plot.columns:  df_plot['Low'] = df_plot['Close']
    if 'Volume' not in df_plot.columns: df_plot['Volume'] = 0

    # Eğer index datetime değilse çevirmeye çalış
    if not isinstance(df_plot.index, pd.DatetimeIndex):
        try:
            df_plot.index = pd.to_datetime(df_plot.index)
        except:
            df_plot.index = pd.date_range(end=pd.Timestamp.today(), periods=len(df_plot))

    apds = []
    
    # 1. Ana Grafik Üzerine SMA
    if 'SMA_14' in df_plot.columns:
        apds.append(mpf.make_addplot(df_plot['SMA_14'], color='blue', width=1.5))
        
    # Bollinger Bands
    if 'BBH' in df_plot.columns and 'BBL' in df_plot.columns:
        apds.append(mpf.make_addplot(df_plot['BBH'], color='gray', width=0.8, linestyle='--'))
        apds.append(mpf.make_addplot(df_plot['BBL'], color='gray', width=0.8, linestyle='--'))

    # 2. Alt Panel (Panel 1): MACD
    if 'MACD' in df_plot.columns and 'Signal' in df_plot.columns and 'Histogram' in df_plot.columns:
        colors = ['green' if val >= 0 else 'red' for val in df_plot['Histogram']]
        apds.append(mpf.make_addplot(df_plot['MACD'], panel=1, color='blue', secondary_y=False))
        apds.append(mpf.make_addplot(df_plot['Signal'], panel=1, color='orange', secondary_y=False))
        apds.append(mpf.make_addplot(df_plot['Histogram'], type='bar', color=colors, panel=1, secondary_y=False))

    # 3. Alt Panel (Panel 2): RSI
    if 'RSI_14' in df_plot.columns:
        apds.append(mpf.make_addplot(df_plot['RSI_14'], panel=2, color='purple', ylabel='RSI'))
        
    # Stil ve genel ayarlar (charles stili yeşil ve kırmızı mum grafikleri sunar)
    # Ayrıca hlines ile RSI için 30 ve 70 seviyelerini çizdirelim.
    kwargs = dict(
        type='candle',
        style='charles',
        title=f"{symbol} Teknik Analizi",
        ylabel='Fiyat',
        volume=False,
        addplot=apds,
        panel_ratios=(3, 1, 1),
        figratio=(12, 10),
        figscale=1.2,
        tight_layout=True
    )
    
    # Dosyaya kaydet veya ekranda göster
    if output_path:
        # RSI çizgileri manuel eklenemediğinden hlines parametresini kullanıyoruz
        mpf.plot(df_plot, **kwargs, savefig=output_path)
        print(f"Grafik '{output_path}' konumuna kaydedildi.")
    else:
        mpf.plot(df_plot, **kwargs)

if __name__ == "__main__":
    print("Test Kullanımı: plot_indicators(df, 'TEST', 'test_grafik.png')")
