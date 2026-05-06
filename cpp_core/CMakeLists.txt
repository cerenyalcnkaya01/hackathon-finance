cmake_minimum_required(VERSION 3.14)
project(FinanceCoreCppWorker)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# ---------------------------------------------------------
# Entegrasyon Kütüphaneleri (PyBind11 & ZeroMQ)
# CMake yapılandırıldığında (configure) otomatik indirilecektir.
# ---------------------------------------------------------

# PyBind11 (Python'a direkt C++ modülü derlemek için)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# ZeroMQ (Ayrı bir servis olarak C++/Python haberleşmesi için)
FetchContent_Declare(
    cppzmq
    GIT_REPOSITORY https://github.com/zeromq/cppzmq.git
    GIT_TAG        v4.10.0
)
# Not: cppzmq'nun MakeAvailable'ı sistemde libzmq (C kütüphanesi) gerektirebilir,
# şu an pasif olarak hazır tutuluyor.
# FetchContent_MakeAvailable(cppzmq) 

# Sadece temel gösterge hesaplamaları
add_library(finance_indicators STATIC
    indicators.cpp
)

# Gerekirse ileride bir main.cpp eklenip çalıştırılabilir veya Python/C# ile bağlanabilir
# add_executable(worker main.cpp)
# target_link_libraries(worker finance_indicators)
