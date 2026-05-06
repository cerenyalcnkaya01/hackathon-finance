const API_BASE = ""; // Same origin

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    updateTime();
    setInterval(updateTime, 1000);
    checkHealth();
    setInterval(checkHealth, 30000);

    // Navigation
    document.querySelectorAll('nav li').forEach(li => {
        li.addEventListener('click', () => {
            const page = li.dataset.page;
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(`${page}-page`).classList.add('active');
            document.querySelectorAll('nav li').forEach(l => l.classList.remove('active'));
            li.classList.add('active');
        });
    });

    // Search
    document.getElementById('btn-search').addEventListener('click', () => performSearch());
    document.getElementById('stock-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // AI Analyze
    document.getElementById('btn-ai-analyze').addEventListener('click', runAIAnalysis);

    // Screening
    document.getElementById('btn-run-screen').addEventListener('click', runScreening);

    // Load Cached Data & Start Progressive Updates
    loadFromCache();
    updateMarketOverview();
}

function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

async function checkHealth() {
    try {
        const resp = await fetch(`${API_BASE}/api/health`);
        const data = await resp.json();
        
        const apiDot = document.getElementById('api-status');
        const ollamaDot = document.getElementById('ollama-status');
        const engineSpan = document.getElementById('engine-status');

        if (data.api === "healthy") apiDot.classList.add('online');
        else apiDot.classList.remove('online');

        if (data.ollama && data.ollama.online) ollamaDot.classList.add('online');
        else ollamaDot.classList.remove('online');

        engineSpan.textContent = data.cpp_engine ? "C++ Core" : "Python";
    } catch (e) {
        console.error("Health check failed", e);
    }
}

async function performSearch(symbolOverride = null) {
    const symbol = (symbolOverride || document.getElementById('stock-search').value).toUpperCase();
    const period = document.getElementById('period-select').value;
    if (!symbol) return;

    if (!symbolOverride) showLoader('main-chart');
    
    try {
        // Fetch Stock Data
        const stockResp = await fetch(`${API_BASE}/api/stock/${symbol}?period=${period}`);
        const stockData = await stockResp.json();

        if (stockData.error) throw new Error(stockData.error);

        renderChart(stockData);
        localStorage.setItem('last_chart', JSON.stringify(stockData));
        
        // Fetch Info
        const infoResp = await fetch(`${API_BASE}/api/stock/${symbol}/info`);
        const infoData = await infoResp.json();
        renderInfo(infoData);
        localStorage.setItem('last_info', JSON.stringify(infoData));

        // Fetch Technical Analysis
        const analysisResp = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ symbol, period, ai_analysis: false })
        });
        const analysisData = await analysisResp.json();
        renderSignals(analysisData);
        localStorage.setItem('last_analysis', JSON.stringify(analysisData));

    } catch (e) {
        console.error("Search failed", e);
        if (!symbolOverride) document.getElementById('main-chart').innerHTML = `<p class="text-center" style="margin-top:20%">Hata: ${e.message}</p>`;
    }
}

function renderChart(data) {
    const trace = {
        x: data.data.map(d => d.date),
        close: data.data.map(d => d.close),
        high: data.data.map(d => d.high),
        low: data.data.map(d => d.low),
        open: data.data.map(d => d.open),
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y'
    };

    const layout = {
        dragmode: 'zoom',
        showlegend: false,
        xaxis: {
            rangeslider: { visible: false },
            color: '#9ca3af'
        },
        yaxis: {
            color: '#9ca3af',
            gridcolor: 'rgba(255,255,255,0.05)'
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 30, b: 40, l: 40, r: 10 }
    };

    Plotly.newPlot('main-chart', [trace], layout, {responsive: true});
}

function renderInfo(info) {
    const container = document.getElementById('stock-info-content');
    container.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:0.5rem">
            <h2 style="font-size:1.5rem">${info.shortName || info.symbol}</h2>
            <p style="color:var(--text-secondary)">${info.sector || 'Sektör Bilgisi Yok'}</p>
            <div style="font-size:2rem; font-weight:700; margin-top:1rem">${info.currentPrice || info.previousClose} <span style="font-size:1rem">${info.currency}</span></div>
            <p style="${(info.recommendationKey === 'buy' || info.recommendationKey === 'strong_buy') ? 'color:var(--success)' : 'color:var(--warning)'}">
                Öneri: ${info.recommendationKey ? info.recommendationKey.toUpperCase() : 'NÖTR'}
            </p>
        </div>
    `;
}

function renderSignals(data) {
    const rsi = data.indicators.RSI ? data.indicators.RSI.toFixed(2) : '--';
    const macd = data.indicators.MACD ? data.indicators.MACD.toFixed(4) : '--';
    const signal = data.signals.macd || '--';

    const rsiEl = document.getElementById('val-rsi');
    const macdEl = document.getElementById('val-macd');
    const signalEl = document.getElementById('val-signal');

    rsiEl.textContent = rsi;
    macdEl.textContent = macd;
    signalEl.textContent = signal;
    
    signalEl.className = 'value badge ' + (signal.toLowerCase().includes('al') ? 'badge-success' : signal.toLowerCase().includes('sat') ? 'badge-danger' : 'badge-warning');

    // Add highlight animation
    [rsiEl, macdEl, signalEl].forEach(el => {
        el.classList.remove('value-animate');
        void el.offsetWidth; // Trigger reflow
        el.classList.add('value-animate');
    });
}

async function runAIAnalysis() {
    const symbol = document.getElementById('stock-search').value.toUpperCase();
    if (!symbol) return;

    const container = document.getElementById('ai-commentary');
    container.innerHTML = '<div class="loader-container"><div class="loader"></div></div><p class="text-center">AI analiz yapıyor...</p>';

    try {
        const resp = await fetch(`${API_BASE}/api/ai/analyze/${symbol}`);
        const data = await resp.json();
        container.innerHTML = `<p>${data.ai}</p>`;
    } catch (e) {
        container.innerHTML = `<p>Hata: AI servisine ulaşılamadı.</p>`;
    }
}

async function runScreening() {
    const preset = document.getElementById('screen-preset').value;
    const type = document.getElementById('screen-type').value;
    const tbody = document.getElementById('screening-body');

    tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="loader"></div></td></tr>';

    try {
        const resp = await fetch(`${API_BASE}/api/screen`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ preset, screen_type: type })
        });
        const data = await resp.json();
        
        if (data.results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">Sonuç bulunamadı.</td></tr>';
            return;
        }

        tbody.innerHTML = data.results.map(r => `
            <tr>
                <td><strong>${r.symbol}</strong></td>
                <td>${r.sector || '--'}</td>
                <td>${r.close ? r.close.toFixed(2) : '--'}</td>
                <td>${r.rsi ? r.rsi.toFixed(2) : '--'}</td>
                <td>${r.macd ? r.macd.toFixed(4) : '--'}</td>
                <td><span class="badge ${r.signal && r.signal.toLowerCase().includes('al') ? 'badge-success' : r.signal && r.signal.toLowerCase().includes('sat') ? 'badge-danger' : 'badge-warning'}">${r.signal || 'Nötr'}</span></td>
                <td>${r.score ? r.score.toFixed(1) : '--'}</td>
            </tr>
        `).join('');

        localStorage.setItem('last_screen', JSON.stringify(data.results));

    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Tarama sırasında hata oluştu.</td></tr>';
    }
}

function loadFromCache() {
    const lastChart = localStorage.getItem('last_chart');
    const lastInfo = localStorage.getItem('last_info');
    const lastAnalysis = localStorage.getItem('last_analysis');
    const lastScreen = localStorage.getItem('last_screen');
    const lastMarket = localStorage.getItem('last_market');

    if (lastChart) renderChart(JSON.parse(lastChart));
    if (lastInfo) renderInfo(JSON.parse(lastInfo));
    if (lastAnalysis) renderSignals(JSON.parse(lastAnalysis));
    if (lastScreen) {
        const results = JSON.parse(lastScreen);
        document.getElementById('screening-body').innerHTML = results.map(r => `
            <tr>
                <td><strong>${r.symbol}</strong></td>
                <td>${r.sector || '--'}</td>
                <td>${r.close ? r.close.toFixed(2) : '--'}</td>
                <td>${r.rsi ? r.rsi.toFixed(2) : '--'}</td>
                <td>${r.macd ? r.macd.toFixed(4) : '--'}</td>
                <td><span class="badge ${r.signal && r.signal.toLowerCase().includes('al') ? 'badge-success' : r.signal && r.signal.toLowerCase().includes('sat') ? 'badge-danger' : 'badge-warning'}">${r.signal || 'Nötr'}</span></td>
                <td>${r.score ? r.score.toFixed(1) : '--'}</td>
            </tr>
        `).join('');
    }
    if (lastMarket) renderMarketOverview(JSON.parse(lastMarket));
}

async function updateMarketOverview() {
    const container = document.getElementById('market-overview');
    const defaultSymbols = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "SISE.IS", "TUPRS.IS"];
    let marketData = JSON.parse(localStorage.getItem('last_market') || '{}');

    // Initial render from cache or placeholders
    if (Object.keys(marketData).length === 0) {
        container.innerHTML = defaultSymbols.map(s => `
            <div class="mini-card" id="card-${s.split('.')[0]}">
                <div class="symbol">${s}</div>
                <div class="price">--</div>
                <div class="change">--%</div>
                <div class="stats">
                    <div>RSI: <span class="stat-val">--</span></div>
                    <div>MACD: <span class="stat-val">--</span></div>
                </div>
            </div>
        `).join('');
    } else {
        renderMarketOverview(marketData);
    }

    // Progressive update
    for (const symbol of defaultSymbols) {
        const cardId = `card-${symbol.split('.')[0]}`;
        const card = document.getElementById(cardId);
        if (card) card.classList.add('updating');

        try {
            const resp = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ symbol, period: "1mo", ai_analysis: false })
            });
            const data = await resp.json();
            
            marketData[symbol] = {
                symbol: symbol,
                price: data.last_price,
                change: 0, // Would need more data for real change
                rsi: data.indicators.RSI,
                macd: data.indicators.MACD
            };

            // Update specific card
            updateMiniCard(symbol, marketData[symbol]);
            localStorage.setItem('last_market', JSON.stringify(marketData));

            // Small delay to simulate "slow" update
            await new Promise(r => setTimeout(r, 800));

        } catch (e) {
            console.error(`Failed to update ${symbol}`, e);
        } finally {
            if (card) card.classList.remove('updating');
        }
    }
}

function updateMiniCard(symbol, data) {
    const cardId = `card-${symbol.split('.')[0]}`;
    const card = document.getElementById(cardId);
    if (!card) return;

    card.innerHTML = `
        <div class="symbol">${symbol}</div>
        <div class="price value-animate">${data.price ? data.price.toFixed(2) : '--'}</div>
        <div class="change up">+0.00%</div>
        <div class="stats">
            <div>RSI: <span class="stat-val">${data.rsi ? data.rsi.toFixed(1) : '--'}</span></div>
            <div>MACD: <span class="stat-val">${data.macd ? data.macd.toFixed(3) : '--'}</span></div>
        </div>
    `;
    card.addEventListener('click', () => {
        document.getElementById('stock-search').value = symbol;
        performSearch(symbol);
    });
}

function renderMarketOverview(marketData) {
    const container = document.getElementById('market-overview');
    container.innerHTML = Object.entries(marketData).map(([symbol, data]) => `
        <div class="mini-card" id="card-${symbol.split('.')[0]}" onclick="performSearch('${symbol}')">
            <div class="symbol">${symbol}</div>
            <div class="price">${data.price ? data.price.toFixed(2) : '--'}</div>
            <div class="change up">+0.00%</div>
            <div class="stats">
                <div>RSI: <span class="stat-val">${data.rsi ? data.rsi.toFixed(1) : '--'}</span></div>
                <div>MACD: <span class="stat-val">${data.macd ? data.macd.toFixed(3) : '--'}</span></div>
            </div>
        </div>
    `).join('');
}

function showLoader(id) {
    document.getElementById(id).innerHTML = '<div class="loader-container"><div class="loader"></div></div>';
}
