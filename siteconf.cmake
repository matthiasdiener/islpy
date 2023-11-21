option(USE_SHIPPED_ISL   "Use ISL library shipped with islpy" ON)
option(USE_SHIPPED_IMATH "Use imath library shipped with ISL" ON)
option(USE_GMP           "Use GMP library" OFF)
option(USE_BARVINOK      "Use barvinok library" OFF)
option(USE_IMATH_SIO     "Use small integer optimizations (imath-32) with imath" ON)

# GMP-related variables, only used if USE_GMP is ON
set(GMP_INC_DIR "" CACHE STRING "GMP include directory")
set(GMP_LIB_DIR "" CACHE STRING "GMP library directory")
set(GMP_LIBNAME "gmp" CACHE STRING "GMP library name")

# ISL-related variables, only used if USE_SHIPPED_ISL is OFF
set(ISL_INC_DIR "/usr/include" CACHE STRING "ISL include directory")
set(ISL_LIB_DIR "" CACHE STRING "ISL library directory")
set(ISL_LIBNAME "isl" CACHE STRING "ISL library name")

# Barvinok-related variables, only used if USE_BARVINOK is ON
set(BARVINOK_INC_DIR "" CACHE STRING "Barvinok include directory")
set(BARVINOK_LIB_DIR "" CACHE STRING "Barvinok library directory")
set(BARVINOK_LIBNAME "barvinok;polylibgmp" CACHE STRING "Barvinok library names")

set(CXXFLAGS "" CACHE STRING "Additional C++ compiler flags")
set(LDFLAGS ""  CACHE STRING "Additional linker flags")
