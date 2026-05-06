/**
 * PyBind11 Binding — C++ İndikatör Fonksiyonlarını Python'a Açar
 *
 * Bu dosya, finance::indicators namespace'indeki tüm hesaplama
 * fonksiyonlarını Python modülü olarak dışa aktarır.
 * Derleme sonrası "cpp_indicators" isimli bir .pyd/.so dosyası oluşur
 * ve Python tarafında `import cpp_indicators` ile kullanılır.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "indicators.hpp"

namespace py = pybind11;

PYBIND11_MODULE(cpp_indicators, m) {
    m.doc() = "C++ ile yüksek performanslı finansal indikatör hesaplamaları";

    // ── SMA ──────────────────────────────────────────────────────────
    m.def("calculate_sma", &finance::indicators::calculate_sma,
          py::arg("prices"), py::arg("period"),
          R"doc(
          Basit Hareketli Ortalama (SMA) hesaplar.

          Args:
              prices: Fiyat listesi (list[float])
              period: Periyot (int)

          Returns:
              list[float]: SMA değerleri
          )doc");

    // ── EMA ──────────────────────────────────────────────────────────
    m.def("calculate_ema", &finance::indicators::calculate_ema,
          py::arg("prices"), py::arg("period"),
          R"doc(
          Üstel Hareketli Ortalama (EMA) hesaplar.

          Args:
              prices: Fiyat listesi (list[float])
              period: Periyot (int)

          Returns:
              list[float]: EMA değerleri
          )doc");

    // ── RSI ──────────────────────────────────────────────────────────
    m.def("calculate_rsi", &finance::indicators::calculate_rsi,
          py::arg("prices"), py::arg("period") = 14,
          R"doc(
          Göreceli Güç Endeksi (RSI) hesaplar.

          Args:
              prices: Fiyat listesi (list[float])
              period: Periyot (varsayılan: 14)

          Returns:
              list[float]: RSI değerleri (0-100 arası)
          )doc");

    // ── MACD ─────────────────────────────────────────────────────────
    py::class_<finance::indicators::MACDResult>(m, "MACDResult",
        "MACD hesaplama sonuçlarını içeren yapı")
        .def_readonly("macd_line", &finance::indicators::MACDResult::macd_line,
                       "MACD çizgisi değerleri")
        .def_readonly("signal_line", &finance::indicators::MACDResult::signal_line,
                       "Sinyal çizgisi değerleri")
        .def_readonly("histogram", &finance::indicators::MACDResult::histogram,
                       "MACD histogram değerleri");

    m.def("calculate_macd", &finance::indicators::calculate_macd,
          py::arg("prices"),
          py::arg("fast_period") = 12,
          py::arg("slow_period") = 26,
          py::arg("signal_period") = 9,
          R"doc(
          MACD (Moving Average Convergence Divergence) hesaplar.

          Args:
              prices: Fiyat listesi (list[float])
              fast_period: Hızlı EMA periyodu (varsayılan: 12)
              slow_period: Yavaş EMA periyodu (varsayılan: 26)
              signal_period: Sinyal çizgisi periyodu (varsayılan: 9)

          Returns:
              MACDResult: macd_line, signal_line ve histogram alanlarına sahip yapı
          )doc");
}
