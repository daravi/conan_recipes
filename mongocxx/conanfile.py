#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import re

class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    version = "3.4.0"
    description = "C++ Driver for MongoDB"
    topics = ("libmongocxx", "mongodb", "db")
    homepage = "https://github.com/mongodb/{0}".format(name)
    license = "Apache-2.0"
    url = "https://github.com/mongodb/{0}/archive/r{1}.tar.gz".format(name, version)
    generators = "cmake"

    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    requires = 'mongo-c-driver/1.14.0@3rdparty/stable'

    def source(self):
        tools.get(self.url)
        extracted_dir = "mongo-cxx-driver-r{0}".format(self.version)
        os.rename(extracted_dir, "sources")

    def build(self):
        conan_magic_lines='''project(MONGO_CXX_DRIVER LANGUAGES CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        # include(CheckCXXCompilerFlag)
        # check_cxx_compiler_flag(-std=c++17 HAVE_FLAG_STD_CXX17)
        # if(HAVE_FLAG_STD_CXX17)
        #     message(STATUS USING C++17!)
        #     set(CMAKE_CXX_STANDARD 17)
        #     set(BSONCXX_POLY_USE_MNMLSTC 0)
        #     set(BSONCXX_POLY_USE_STD_EXPERIMENTAL 0)
        #     set(BSONCXX_POLY_USE_BOOST 0)
        #     set(BSONCXX_POLY_USE_STD 1)
        # else()
        #     check_cxx_compiler_flag(-std=c++14 HAVE_FLAG_STD_CXX14)
        #     if(HAVE_FLAG_STD_CXX14)
        #         message(STATUS USING C++14!)
        #         set(CMAKE_CXX_STANDARD 14)
        #         set(BSONCXX_POLY_USE_MNMLSTC 0)
        #         set(BSONCXX_POLY_USE_STD_EXPERIMENTAL 1)
        #         set(BSONCXX_POLY_USE_BOOST 0)
        #         set(BSONCXX_POLY_USE_STD 0)
        #     else()
        #         message(FATAL_ERROR "MongoCXX requires at least C++14")
        #     endif()
        # endif()
        # set(CMAKE_CXX_STANDARD_REQUIRED ON)
        # set(CMAKE_CXX_EXTENSIONS OFF)
        set(BSONCXX_POLY_USE_MNMLSTC 1)
        set(BSONCXX_POLY_USE_STD_EXPERIMENTAL 0)
        set(BSONCXX_POLY_USE_BOOST 0)
        set(BSONCXX_POLY_USE_STD 0)

        set(CMAKE_CXX_STANDARD 17)
        set(CMAKE_CXX_STANDARD_REQUIRED ON)
        '''
        
        cmake_file = "sources/CMakeLists.txt"
        tools.replace_in_file(cmake_file, "project(MONGO_CXX_DRIVER LANGUAGES CXX)", conan_magic_lines)
        tools.replace_in_file(cmake_file, "enable_testing()", "")

        cmake = CMake(self)
        # if self.settings.compiler == 'Visual Studio':
        # 	cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 1 # required for Windows.
        cmake.definitions["BUILD_TESTING"] = 0
        cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.definitions["CMAKE_CXX_STANDARD_REQUIRED"] = 1
        cmake.definitions["BSONCXX_POLY_USE_MNMLSTC"] = 1
        cmake.definitions["BSONCXX_POLY_USE_STD_EXPERIMENTAL"] = 0
        cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 0
        cmake.definitions["BSONCXX_POLY_USE_STD"] = 0
        cmake.configure(source_dir="sources")

        cmake.build(target="bsoncxx")
        cmake.build(target="mongocxx")
        cmake.build(target="mongocxx_mocked")

    def purge(self, dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                os.remove(os.path.join(dir, f))

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src="sources")
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="sources/src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="sources/src/mongocxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="src/mongocxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/bsoncxx/third_party/mnmlstc/core", src="src/bsoncxx/third_party/EP_mnmlstc_core-prefix/src/EP_mnmlstc_core/include/core", keep_path=False)

        try:
            os.rename("lib/libmongocxx-static.a", "lib/libmongocxx.a")
        except:
            pass
        try:
            os.rename("lib/libbsoncxx-static.a", "lib/libbsoncxx.a")
        except:
            pass
        try:
            os.rename("lib/libmongocxx-static.lib", "lib/libmongocxx.lib")
        except:
            pass
        try:
            os.rename("lib/libbsoncxx-static.lib", "lib/libbsoncxx.lib")
        except:
            pass
        self.copy(pattern="lib*cxx.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx.so*", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx.dylib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx._noabi.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['mongocxx', 'bsoncxx']
        self.cpp_info.includedirs.append('include/bsoncxx/third_party/mnmlstc')


