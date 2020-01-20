#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import re

class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    version = "3.4.1-20200120+gitd8eb7d5794"
    commit_sha = "d8eb7d57948ea37449bf34b1f0a43af592c98912"
    is_release = False
    description = "C++ Driver for MongoDB"
    topics = ("libmongocxx", "mongodb", "db")
    homepage = "https://github.com/mongodb/{0}".format(name)
    license = "Apache-2.0"
    url = "{0}/archive/{1}.tar.gz".format(homepage, "r" + version if is_release else commit_sha)
    exports_sources = ["cplusplus.patch"]
    generators = "cmake"

    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    requires = 'mongo-c-driver/1.16.0@3rdparty/stable'

    def source(self):
        tools.get(self.url)
        extracted_dir = "mongo-cxx-driver-{0}".format("r" + self.version if self.is_release else self.commit_sha)
        os.rename(extracted_dir, "sources")
        tools.patch(base_path="sources", patch_file="cplusplus.patch") # Needed for Visual Studio < 15.7.3

    def build(self):
        conan_magic_lines='''project(MONGO_CXX_DRIVER LANGUAGES CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''

        cmake_file = "sources/CMakeLists.txt"
        tools.replace_in_file(cmake_file, "project(MONGO_CXX_DRIVER LANGUAGES CXX)", conan_magic_lines)
        tools.replace_in_file(cmake_file, "enable_testing()", "")

        cmake = CMake(self)
        cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.definitions["CMAKE_CXX_STANDARD_REQUIRED"] = 1
        cmake.definitions["BSONCXX_POLY_USE_MNMLSTC"] = 0
        cmake.definitions["BSONCXX_POLY_USE_STD_EXPERIMENTAL"] = 0
        cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 0
        cmake.definitions["BSONCXX_POLY_USE_STD"] = 1
        cmake.definitions["BUILD_VERSION"] = self.version
        cmake.configure(source_dir="sources")

        if (self.options["shared"]):
            cmake.build(target="bsoncxx_shared")
            cmake.build(target="mongocxx_shared")
        else:
            cmake.build(target="bsoncxx_static")
            cmake.build(target="mongocxx_static")

    def purge(self, dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                os.remove(os.path.join(dir, f))

    def package(self):
        # copy headers
        self.copy(pattern="LICENSE*", dst="licenses", src="sources")
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="sources/src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="sources/src/mongocxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="src/mongocxx", keep_path=True)
        # copy libraries
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*.so*", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*.dylib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*._noabi.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        if (self.options["shared"]):
            self.cpp_info.libs = ['mongocxx-shared', 'bsoncxx-shared']
        else:
            self.cpp_info.libs = ['mongocxx-static', 'bsoncxx-static']


