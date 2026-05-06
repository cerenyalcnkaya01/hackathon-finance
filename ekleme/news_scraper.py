import time
import requests
import feedparser  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from newspaper import Article  # type: ignore
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
import schedule  # type: ignore
import plotly.graph_objects as go  # type: ignore
from datetime import datetime
import json
import os
import nltk  # type: ignore

# ─── Ayarlar ───────────────────────────────────────────────
analyzer = SentimentIntensityAnalyzer()
PROCESSED_URLS_FILE = "processed_urls.json"
NEWS_DATA_FILE = "news_data.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# ─── Kalıcı Veri Yönetimi ─────────────────────────────────
def load_processed_urls():
    if os.path.exists(PROCESSED_URLS_FILE):
        try:
            with open(PROCESSED_URLS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_processed_urls(urls_set):
    with open(PROCESSED_URLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(urls_set), f, ensure_ascii=False)

def load_news_data():
    if os.path.exists(NEWS_DATA_FILE):
        try:
            with open(NEWS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    item['time'] = datetime.fromisoformat(item['time'])
                return data
        except Exception:
            return []
    return []

def save_news_data(data):
    serializable = []
    for item in data:
        serializable.append({
            'time': item['time'].isoformat(),
            'source': item['source'],
            'title': item['title'],
            'compound_sentiment': item['compound_sentiment']
        })
    with open(NEWS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

processed_urls = load_processed_urls()
news_data = load_news_data()

# ─── Makale Analizi ───────────────────────────────────────
def analyze_article(url, source, title_hint=None):
    """Makaleyi indir, parse et ve sentiment analizi yap."""
    if url in processed_urls:
        return False

    try:
        article = Article(url, language='tr')
        article.download()
        article.parse()

        text = article.text
        title = article.title or title_hint or "Başlıksız"

        if not text or len(text.strip()) < 50:
            # Metin çok kısa ise sadece başlığı kullan
            text = title

        sentiment = analyzer.polarity_scores(text)

        print(f"  [+] [{source}] {title[:80]}")
        print(f"      Sentiment: pos={sentiment['pos']:.2f} neg={sentiment['neg']:.2f} compound={sentiment['compound']:.3f}")

        processed_urls.add(url)
        save_processed_urls(processed_urls)

        news_data.append({
            "time": datetime.now(),
            "source": source,
            "title": title,
            "compound_sentiment": sentiment['compound']
        })
        save_news_data(news_data)
        return True

    except Exception as e:
        print(f"  [-] Hata ({source}): {str(e)[:100]}")
        processed_urls.add(url)  # Hatalı URL'yi de kaydet, tekrar denemesin
        save_processed_urls(processed_urls)
        return False

def analyze_text_directly(text, source, title, url_key):
    """Metin doğrudan verildiğinde sentiment analizi yap (KAP için)."""
    if url_key in processed_urls:
        return False

    if not text or len(text.strip()) < 10:
        return False

    sentiment = analyzer.polarity_scores(text)

    print(f"  [+] [{source}] {title[:80]}")
    print(f"      Sentiment: pos={sentiment['pos']:.2f} neg={sentiment['neg']:.2f} compound={sentiment['compound']:.3f}")

    processed_urls.add(url_key)
    save_processed_urls(processed_urls)

    news_data.append({
        "time": datetime.now(),
        "source": source,
        "title": title,
        "compound_sentiment": sentiment['compound']
    })
    save_news_data(news_data)
    return True

# ─── Kaynak: Investing.com (RSS Feed) ────────────────────
def scrape_investing():
    print("\n[*] Investing.com taraniyor (RSS)...")
    count = 0
    try:
        feed = feedparser.parse('https://tr.investing.com/rss/news_25.rss')
        if not feed.entries:
            print("  [!] RSS feed'den haber bulunamadi.")
            return

        for entry in feed.entries:
            url = entry.get('link', '')
            title = entry.get('title', '')
            summary = entry.get('summary', '')

            if url and url not in processed_urls:
                text = f"{title}. {summary}" if summary else title
                if analyze_text_directly(text, "Investing", title, url):
                    count += 1

        print(f"  -> {count} yeni haber islendi.")
    except Exception as e:
        print(f"  [-] Investing scraping hatasi: {e}")

# ─── Kaynak: Bloomberg HT (RSS Feed + Web) ───────────────
def scrape_bloomberg():
    print("\n[*] Bloomberg HT taraniyor (RSS)...")
    count = 0
    try:
        feed = feedparser.parse('https://www.bloomberght.com/rss')
        if feed.entries:
            for entry in feed.entries:
                url = entry.get('link', '')
                title = entry.get('title', '')
                summary = entry.get('summary', '')

                if url and url not in processed_urls:
                    text = f"{title}. {summary}" if summary else title
                    if analyze_text_directly(text, "Bloomberg HT", title, url):
                        count += 1
        else:
            print("  [!] RSS bos, web sayfasi deneniyor...")

        # Ek olarak web sayfasından da haber çek
        try:
            response = requests.get('https://www.bloomberght.com/haberler', headers=HEADERS, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/') and len(href.split('-')) >= 3 and not href.startswith('/rss') and not href.startswith('/video'):
                        full_url = "https://www.bloomberght.com" + href
                        if full_url not in processed_urls:
                            title = a.get_text(strip=True)
                            if title and len(title) > 15:
                                if analyze_article(full_url, "Bloomberg HT", title):
                                    count += 1
                                    if count >= 10:  # Çok fazla makale indirmeyi sınırla
                                        break
        except Exception as e:
            print(f"  [!] Bloomberg web scraping hatasi: {e}")

        print(f"  -> {count} yeni haber islendi.")
    except Exception as e:
        print(f"  [-] Bloomberg hatasi: {e}")

# ─── Kaynak: KAP (API) ───────────────────────────────────
def scrape_kap():
    print("\n[*] KAP taraniyor (API)...")
    count = 0
    try:
        # KAP bildirim listesi sayfasindan haber cek
        kap_url = "https://www.kap.org.tr/tr/bildirim-sorgu"
        response = requests.get(kap_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Sayfadaki bildirim basliklarini topla
            for item in soup.find_all(['div', 'td', 'span'], class_=True):
                text = item.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 300:
                    url_key = f"kap_{hash(text)}"
                    if url_key not in processed_urls:
                        if analyze_text_directly(text, "KAP", text[:100], url_key):
                            count += 1
                            if count >= 15:
                                break
        else:
            print(f"  [!] KAP yanit kodu: {response.status_code}")

        print(f"  -> {count} yeni bildirim islendi.")
    except Exception as e:
        print(f"  [-] KAP hatasi: {e}")

# ─── Kaynak: Bigpara ─────────────────────────────────────
def scrape_bigpara():
    print("\n[*] Bigpara taraniyor...")
    count = 0
    try:
        response = requests.get('https://www.bigpara.com/haberler/ekonomi-haberleri', headers=HEADERS, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                # Ekonomi haberi linklerini bul
                if '/haberler/' in href and href != '/haberler/ekonomi-haberleri/' and href.count('/') >= 3:
                    full_url = href if href.startswith('http') else "https://www.bigpara.com" + href

                    if full_url not in processed_urls:
                        title = a.get_text(strip=True)
                        if title and len(title) > 10:
                            if analyze_article(full_url, "Bigpara", title):
                                count += 1
                                if count >= 10:
                                    break
        else:
            print(f"  [!] Bigpara yanit kodu: {response.status_code}")

        print(f"  -> {count} yeni haber islendi.")
    except Exception as e:
        print(f"  [-] Bigpara hatasi: {e}")

# ─── Grafik Güncelleme ────────────────────────────────────
def update_plot():
    if not news_data:
        print("\n[*] Henuz grafik icin veri yok.")
        return

    # Kaynağa göre renkler
    color_map = {
        "Investing": "#FF6B35",
        "Bloomberg HT": "#1E90FF",
        "KAP": "#32CD32",
        "Bigpara": "#FF69B4"
    }

    fig = go.Figure()

    for source in color_map:
        source_data = [d for d in news_data if d['source'] == source]
        if source_data:
            fig.add_trace(go.Scatter(
                x=[d['time'] for d in source_data],
                y=[d['compound_sentiment'] for d in source_data],
                mode='markers+lines',
                name=source,
                text=[d['title'][:60] for d in source_data],
                hovertemplate='<b>%{text}</b><br>Sentiment: %{y:.3f}<br>Zaman: %{x}<extra></extra>',
                marker=dict(size=10, color=color_map[source]),
                line=dict(width=1, color=color_map[source], dash='dot')
            ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title='Finans Haberleri Duygu Analizi (Sentiment)',
        xaxis_title='Zaman',
        yaxis_title='Sentiment Skoru (-1 Negatif / +1 Pozitif)',
        yaxis=dict(range=[-1.1, 1.1]),
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='closest'
    )

    fig.write_html("sentiment_plot.html")
    print(f"\n[*] Grafik guncellendi: sentiment_plot.html ({len(news_data)} haber)")

# ─── Ana Döngü ────────────────────────────────────────────
def job():
    print(f"\n{'='*60}")
    print(f"[*] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Haber Taramasi Basliyor")
    print(f"{'='*60}")

    scrape_investing()
    scrape_bloomberg()
    scrape_kap()
    scrape_bigpara()
    update_plot()

    print(f"\n{'='*60}")
    print(f"[OK] Tarama Tamamlandi - Toplam {len(news_data)} haber, {len(processed_urls)} URL islendi")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        print("NLTK 'punkt_tab' indiriliyor...")
        nltk.download('punkt_tab')

    # İlk çalıştırma
    job()

    # 15 dakikada bir tekrar çalıştır
    INTERVAL_MINUTES = 15
    schedule.every(INTERVAL_MINUTES).minutes.do(job)

    print(f"[BOT] Haber botu calisiyor ({INTERVAL_MINUTES} dakikada bir kontrol). Cikmak icin Ctrl+C.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Bot durduruldu.")
