#include "indicators.hpp"
#include <cmath>
#include <stdexcept>
#include <algorithm>

namespace finance {
namespace indicators {

std::vector<double> calculate_sma(const std::vector<double>& prices, int period) {
    std::vector<double> sma(prices.size(), 0.0);
    if (period <= 0 || prices.size() < static_cast<size_t>(period)) return sma;

    double sum = 0.0;
    for (int i = 0; i < period; ++i) {
        sum += prices[i];
    }
    sma[period - 1] = sum / period;

    for (size_t i = period; i < prices.size(); ++i) {
        sum += prices[i] - prices[i - period];
        sma[i] = sum / period;
    }

    return sma;
}

std::vector<double> calculate_ema(const std::vector<double>& prices, int period) {
    std::vector<double> ema(prices.size(), 0.0);
    if (period <= 0 || prices.size() < static_cast<size_t>(period)) return ema;

    double multiplier = 2.0 / (period + 1.0);
    
    // Initial EMA is SMA
    double sum = 0.0;
    for (int i = 0; i < period; ++i) {
        sum += prices[i];
    }
    ema[period - 1] = sum / period;

    for (size_t i = period; i < prices.size(); ++i) {
        ema[i] = ((prices[i] - ema[i - 1]) * multiplier) + ema[i - 1];
    }

    return ema;
}

std::vector<double> calculate_rsi(const std::vector<double>& prices, int period) {
    std::vector<double> rsi(prices.size(), 0.0);
    if (period <= 0 || prices.size() < static_cast<size_t>(period + 1)) return rsi;

    double gain = 0.0;
    double loss = 0.0;

    // First average gain/loss
    for (int i = 1; i <= period; ++i) {
        double diff = prices[i] - prices[i - 1];
        if (diff > 0) gain += diff;
        else loss -= diff;
    }

    gain /= period;
    loss /= period;

    if (loss == 0.0) rsi[period] = 100.0;
    else rsi[period] = 100.0 - (100.0 / (1.0 + gain / loss));

    // Smoothed subsequent values
    for (size_t i = period + 1; i < prices.size(); ++i) {
        double diff = prices[i] - prices[i - 1];
        double current_gain = (diff > 0) ? diff : 0.0;
        double current_loss = (diff < 0) ? -diff : 0.0;

        gain = ((gain * (period - 1)) + current_gain) / period;
        loss = ((loss * (period - 1)) + current_loss) / period;

        if (loss == 0.0) {
            rsi[i] = 100.0;
        } else {
            rsi[i] = 100.0 - (100.0 / (1.0 + gain / loss));
        }
    }

    return rsi;
}

MACDResult calculate_macd(const std::vector<double>& prices, int fast_period, int slow_period, int signal_period) {
    MACDResult result;
    result.macd_line.resize(prices.size(), 0.0);
    result.signal_line.resize(prices.size(), 0.0);
    result.histogram.resize(prices.size(), 0.0);

    if (prices.size() < static_cast<size_t>(std::max(fast_period, slow_period))) return result;

    std::vector<double> fast_ema = calculate_ema(prices, fast_period);
    std::vector<double> slow_ema = calculate_ema(prices, slow_period);

    // Calculate MACD line
    for (size_t i = 0; i < prices.size(); ++i) {
        if (i >= static_cast<size_t>(slow_period - 1)) {
            result.macd_line[i] = fast_ema[i] - slow_ema[i];
        }
    }

    // Prepare non-zero macd values for signal line calculation
    // Start of MACD is slow_period - 1
    std::vector<double> valid_macd;
    valid_macd.reserve(prices.size());
    for(size_t i = slow_period - 1; i < prices.size(); ++i) {
        valid_macd.push_back(result.macd_line[i]);
    }

    if(valid_macd.size() >= static_cast<size_t>(signal_period)) {
        std::vector<double> signal_ema = calculate_ema(valid_macd, signal_period);
        for(size_t i = 0; i < signal_ema.size(); ++i) {
            result.signal_line[i + slow_period - 1] = signal_ema[i];
        }
    }

    // Calculate Histogram
    for (size_t i = 0; i < prices.size(); ++i) {
        result.histogram[i] = result.macd_line[i] - result.signal_line[i];
    }

    return result;
}

} // namespace indicators
} // namespace finance
