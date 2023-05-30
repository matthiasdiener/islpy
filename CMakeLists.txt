cmake_minimum_required(VERSION 3.18...3.22)
project(islpy)
find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

# Force Release build by default
if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING Choose the type of build. FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# Detect the installed nanobind package and import it into CMake
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE NB_DIR)
list(APPEND CMAKE_PREFIX_PATH "${NB_DIR}")
find_package(nanobind CONFIG REQUIRED)

include_directories(${ISL_INC_DIR})
link_directories(${ISL_LIB_DIR})

nanobind_add_module(
  _isl
  NB_STATIC # Build static libnanobind (the extension module itself remains a shared library)
  src/wrapper/wrap_isl.cpp
  src/wrapper/wrap_isl_part1.cpp
  src/wrapper/wrap_isl_part2.cpp
  src/wrapper/wrap_isl_part3.cpp
)

target_link_libraries(_isl PRIVATE ${ISL_LIBRARY})

install(TARGETS _isl LIBRARY DESTINATION .)
