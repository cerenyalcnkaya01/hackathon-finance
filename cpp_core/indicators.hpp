#pragma once

#include <vector>

namespace finance {
namespace indicators {

    // Simple Moving Average (SMA)
    std::vector<double> calculate_sma(const std::vector<double>& prices, int period);

    // Exponential Moving Average (EMA)
    std::vector<double> calculate_ema(const std::vector<double>& prices, int period);

    // Relative Strength Index (RSI)
    std::vector<double> calculate_rsi(const std::vector<double>& prices, int period = 14);

    // MACD structure
    struct MACDResult {
        std::vector<double> macd_line;
        std::vector<double> signal_line;
        std::vector<double> histogram;
    };

    // Moving Average Convergence Divergence (MACD)
    MACDResult calculate_macd(const std::vector<double>& prices, int fast_period = 12, int slow_period = 26, int signal_period = 9);

} // namespace indicators
} // namespace finance
