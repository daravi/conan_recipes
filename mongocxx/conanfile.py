#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import re

class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    version = "3.4.0"
    commit_sha = "131fa1a67acd45c0eebcbdcfee42b212af8d2e80"
    git_username = "mongodb"
    description = "C++ Driver for MongoDB"
    topics = ("libmongocxx", "mongodb", "db")
    homepage = "https://github.com/mongodb/{0}".format(name)
    license = "Apache-2.0"
    url = "https://github.com/mongodb/{0}/archive/r{1}.tar.gz".format(name, version)
    commit_url = "https://github.com/{0}/{1}/archive/{2}.zip".format(git_username, name, commit_sha)
    generators = "cmake"

    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    requires = 'mongo-c-driver/1.14.0@test/test'

    def source(self):
        self.run("git clone https://github.com/mongodb/mongo-cxx-driver.git")
        self.run("cd {0} && git checkout {1}".format(self.name, self.commit_sha))
        self.run("cd ..")
        extracted_dir = self.name
        # tools.get(self.commit_url)
        # extracted_dir = "{0}-{1}".format(self.name, self.commit_sha)
        os.rename(extracted_dir, "sources")

    def build(self):
        conan_magic_lines='''project(MONGO_CXX_DRIVER LANGUAGES CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''
        
        cmake_file = "sources/CMakeLists.txt"
        # TODO PUYA: Change this to use a wrapper instead
        tools.replace_in_file(cmake_file, "project(MONGO_CXX_DRIVER LANGUAGES CXX)", conan_magic_lines)
        # tools.replace_in_file(cmake_file, "enable_testing()", "")

        cmake = CMake(self)
        # TODO PUYA: Add check to see which STD is available (use BSONCXX_POLY_USE_MNMLSTC if necessary)
        # if self.settings.compiler == 'Visual Studio':
        # 	cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 1 # required for Windows (if C++17 not available)
        cmake.definitions["BUILD_TESTING"] = 0
        cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.definitions["CMAKE_CXX_STANDARD_REQUIRED"] = 1
        cmake.definitions["BSONCXX_POLY_USE_STD"] = 1
        cmake.definitions["BUILD_VERSION"] = "3.4.0-"
        cmake.configure(source_dir="sources")

        cmake.build()

        # cmake.build(target="bsoncxx")
        # cmake.build(target="mongocxx")
        # cmake.build(target="mongocxx_mocked")

    def purge(self, dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                os.remove(os.path.join(dir, f))

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src="sources")
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="sources/src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="sources/src/mongocxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="src", keep_path=True)
        # self.copy(pattern="*.hpp", dst="include/mongocxx", src="src/mongocxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/bsoncxx/third_party/mnmlstc/core", src="src/bsoncxx/third_party/EP_mnmlstc_core-prefix/src/EP_mnmlstc_core/include/core", keep_path=False)
        self.copy(pattern="*.hpp", dst="include/mongocxx/helpers", src="sources/src/third_party/catch/include", keep_path=False)
        self.copy(pattern="*.hh", dst="include", src="src", keep_path=True)
        self.copy(pattern="*.hh", dst="include", src="sources/src", keep_path=True)

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
        self.copy(pattern="libmongocxx-mocked.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['mongocxx', 'bsoncxx']
        self.cpp_info.includedirs.append('include/bsoncxx/third_party/mnmlstc')


