cmake_minimum_required(VERSION 3.14)
project(FinanceCoreCppWorker)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# ---------------------------------------------------------
# PyBind11 — Python'a C++ modülü olarak derleme
# CMake yapılandırıldığında (configure) otomatik indirilecektir.
# ---------------------------------------------------------

FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# ZeroMQ (Ayrı bir servis olarak C++/Python haberleşmesi için — gelecekte kullanılabilir)
# FetchContent_Declare(
#     cppzmq
#     GIT_REPOSITORY https://github.com/zeromq/cppzmq.git
#     GIT_TAG        v4.10.0
# )
# FetchContent_MakeAvailable(cppzmq)

# ─── 1. Statik Kütüphane (iç kullanım) ────────────────────────────────────────
add_library(finance_indicators STATIC
    indicators.cpp
)
target_include_directories(finance_indicators PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# ─── 2. PyBind11 Python Modülü ────────────────────────────────────────────────
# Bu hedef, 'cpp_indicators.pyd' (Windows) veya 'cpp_indicators.so' (Linux)
# dosyasını üretir. Python tarafında `import cpp_indicators` ile kullanılır.
pybind11_add_module(cpp_indicators
    bindings.cpp
    indicators.cpp
)
target_include_directories(cpp_indicators PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Derleme sonrası .pyd/.so dosyasını proje kök dizinine kopyala
# Böylece Python tarafı doğrudan import edebilir
add_custom_command(TARGET cpp_indicators POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:cpp_indicators>
        ${CMAKE_CURRENT_SOURCE_DIR}/../$<TARGET_FILE_NAME:cpp_indicators>
    COMMENT ">> cpp_indicators modülü proje köküne kopyalanıyor..."
)

# ─── 3. Opsiyonel: Bağımsız test çalıştırılabilir dosyası ─────────────────────
# Gerekirse ileride bir main.cpp eklenip çalıştırılabilir
# add_executable(worker main.cpp)
# target_link_libraries(worker finance_indicators)
