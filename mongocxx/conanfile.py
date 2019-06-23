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
    license = "Apache-2.0"
    homepage = "https://github.com/mongodb/{0}".format(name)
    url = "https://github.com/mongodb/{0}/archive/r{1}.tar.gz".format(name, version)

    settings =  "os", "compiler", "arch", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = "mongo-c-driver/1.14.0@test2/test2"

    def source(self):
        # tools.get(self.url)
        # extracted_dir = "mongo-cxx-driver-r{0}".format(self.version)
        # os.rename(extracted_dir, "sources")
        tools.get(self.url)
        extracted_dir = self.name + "-r" + self.version
        os.rename(extracted_dir, self._source_subfolder)
    
    def _configure_cmake(self):
        cmake = CMake(self)
        # If C++17 not available:
        # if self.settings.compiler == 'Visual Studio':
        # 	cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 1 # required for Windows.
        # else:
        #     cmake.definitions["BSONCXX_POLY_USE_MNMLSTC"] = 1
        cmake.definitions["CMAKE_CXX_STANDARD_REQUIRED"] = 1
        cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.definitions["BSONCXX_POLY_USE_STD"] = 1
		# BSONCXX_POLY_USE_STD
        cmake.definitions["BUILD_TESTING"] = 0
        cmake.definitions["BUILD_SHARED_LIBS"] = "OFF" if self.options.shared else "ON"

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="bsoncxx")
        cmake.build(target="mongocxx")
        cmake.build(target="mongocxx_mocked")
        # cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        # self.copy(pattern="*.hpp", dst="include/bsoncxx", src=self._source_subfolder + "/src/bsoncxx", keep_path=True)
        # self.copy(pattern="*.hpp", dst="include/mongocxx", src=self._source_subfolder + "/src/mongocxx", keep_path=True)
        # self.copy(pattern="*.hpp", dst="include/bsoncxx", src="src/bsoncxx", keep_path=True)
        # self.copy(pattern="*.hpp", dst="include/mongocxx", src="src/mongocxx", keep_path=True)
        # self.copy(pattern="*.hpp", dst="include/bsoncxx/third_party/mnmlstc/core", src="src/bsoncxx/third_party/EP_mnmlstc_core-prefix/src/EP_mnmlstc_core/include/core", keep_path=False)

        # try:
        #     os.rename("lib/libmongocxx-static.a", "lib/libmongocxx.a")
        # except:
        #     pass
        # try:
        #     os.rename("lib/libbsoncxx-static.a", "lib/libbsoncxx.a")
        # except:
        #     pass
        # try:
        #     os.rename("lib/libmongocxx-static.lib", "lib/libmongocxx.lib")
        # except:
        #     pass
        # try:
        #     os.rename("lib/libbsoncxx-static.lib", "lib/libbsoncxx.lib")
        # except:
        #     pass
        # self.copy(pattern="lib*cxx.lib", dst="lib", src="lib", keep_path=False)
        # self.copy(pattern="lib*cxx.a", dst="lib", src="lib", keep_path=False)
        # self.copy(pattern="lib*cxx.so*", dst="lib", src="lib", keep_path=False)
        # self.copy(pattern="lib*cxx.dylib", dst="lib", src="lib", keep_path=False)
        # self.copy(pattern="lib*cxx._noabi.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ['libmongocxx', 'libbsoncxx']
        else:
            self.cpp_info.libs = ['libmongocxx-static', 'libbsoncxx-static']
        # self.cpp_info.includedirs.append('include/bsoncxx/third_party/mnmlstc')


