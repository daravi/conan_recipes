#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import re

class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    version = "r3.4.0"
    commit_sha = "131fa1a67acd45c0eebcbdcfee42b212af8d2e80"
    git_username = "mongodb"
    description = "C++ Driver for MongoDB"
    topics = ("libmongocxx", "mongodb", "db")
    homepage = "https://github.com/{0}/{1}".format(git_username, name)
    license = "Apache-2.0"
    url = "https://github.com/{0}/{1}/archive/{2}.tar.gz".format(git_username, name, version)
    commit_url = "https://github.com/{0}/{1}/archive/{2}.zip".format(git_username, name, commit_sha)
    generators = "cmake"

    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    requires = 'mongo-c-driver/1.14.0@3rdparty/stable'

    def source(self):
        tools.get(self.commit_url)
        extracted_dir = "{0}-{1}".format(self.name, self.commit_sha)
        os.rename(extracted_dir, "sources")

    def build(self):
        conan_magic_lines='''project(MONGO_CXX_DRIVER LANGUAGES CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''
        
        cmake_file = "sources/CMakeLists.txt"
        # TODO PUYA: Change this to use a wrapper instead
        tools.replace_in_file(cmake_file, "project(MONGO_CXX_DRIVER LANGUAGES CXX)", conan_magic_lines)
        tools.replace_in_file(cmake_file, "enable_testing()", "")

        cmake = CMake(self)
        # TODO PUYA: Add check to see which STD is available (use BSONCXX_POLY_USE_MNMLSTC if necessary)
        # if self.settings.compiler == 'Visual Studio':
        # 	cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 1 # required for Windows (if C++17 not available)
        cmake.definitions["BUILD_TESTING"] = 0
        cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.definitions["CMAKE_CXX_STANDARD_REQUIRED"] = 1
        cmake.definitions["BSONCXX_POLY_USE_STD"] = 1
        cmake.definitions["BUILD_VERSION"] = "3.4.0"
        cmake.configure(source_dir="sources")

        # cmake.build()
        cmake.build(target="bsoncxx_static")
        cmake.build(target="mongocxx_static")
        # cmake.build(target="mongocxx_mocked")

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src="sources")
        self.copy(pattern="*.hh", dst="include", src="src", keep_path=True)
        self.copy(pattern="*.hh", dst="include", src="sources/src", keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="src", keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="sources/src", keep_path=True)
        self.copy(pattern="*.h", dst="include", src="src", keep_path=True)
        self.copy(pattern="*.h", dst="include", src="sources/src", keep_path=True)

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
        self.cpp_info.libs = tools.collect_libs(self)


