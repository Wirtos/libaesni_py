cmake_minimum_required(VERSION 3.14.7 FATAL_ERROR)
project(libaesni_py C)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_subdirectory(libaesni)

find_package(Python COMPONENTS Development REQUIRED)

include(GNUInstallDirs)

add_library(libaesni_py SHARED libaesni_py.c)

get_target_property(aesni_includes libaesni INCLUDE_DIRECTORIES)
target_include_directories(libaesni_py PRIVATE ${aesni_includes})

target_link_libraries(libaesni_py PRIVATE
        Python::Python
        $<TARGET_OBJECTS:libaesni_asm>
        $<TARGET_OBJECTS:libaesni>
        )

set_target_properties(libaesni_py PROPERTIES SUFFIX ".pyd" PREFIX "")

add_dependencies(libaesni_py libaesni)

install(TARGETS libaesni_py RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR})
