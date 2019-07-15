#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import importlib.util
import subprocess
import sys

class FSeamConan(ConanFile):
    name = "FSeam"
    version = "v1.0.1"
    commit_sha = "a1a41667c76489f64c93c9a979aad88d865ac768"
    git_username = "FreeYourSoul"
    description = "Cpp header only library to manage compile time mock class generated via Python script"
    topics = ("unit-test", "mocking")
    homepage = "https://github.com/{0}/{1}".format(git_username, name)
    license = "MIT"
    url = "https://github.com/{0}/{1}/archive/{2}.tar.gz".format(git_username, name, version)
    commit_url = "https://github.com/{0}/{1}/archive/{2}.zip".format(git_username, name, commit_sha)
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings =  "os", "compiler", "arch", "build_type"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "Googletest/1.8.1@3rdparty/stable",
        "CMakeCommon/1.1.6@mmi/dev"
    )

    def _check_dependencies(self):
        package_name = "ply"
        spec = importlib.util.find_spec(package_name)
        if (spec is None):
            print("Could not find module PLY (dependency of FSeam). Attempting to install it...")
            subprocess.call([sys.executable, "-m", "pip", "install", package_name])
        else:
            print("Module PLY is already installed.")
            return
        spec = importlib.util.find_spec(package_name)
        if (spec is None):
            raise ModuleNotFoundError("Could not install module PLY")

    def source(self):
        self._check_dependencies()
        tools.get(self.commit_url)
        extracted_dir = "{0}-{1}".format(self.name, self.commit_sha)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self): # why can't I change this to configure?
        cmake = CMake(self)
        cmake.definitions["FSEAM_BUILD_TESTS"] = False
        cmake.configure(build_folder=self._build_subfolder)

    def package(self):
        cmake_scripts_folder = self.deps_cpp_info["CMakeCommon"].rootpath + "/cmake-tools/FSeam"
        python_bin_folder = os.path.dirname(sys.executable)
        self.copy(pattern=r'*FSeam*.cmake', dst=cmake_scripts_folder, src=self._build_subfolder, keep_path=False, excludes=r'*CMakeFiles*')
        self.copy(pattern=r'FSeam*.cmake', dst=cmake_scripts_folder, src=(self._source_subfolder + "/cmake"), keep_path=False)
        self.copy(pattern=r'LICENSE', dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy(pattern=r'Versioner.hh', dst="include", src=(self._source_subfolder + "/FSeam"))
        self.copy(pattern=r'FSeam.hpp', dst="include", src=(self._source_subfolder + "/FSeam"))
        self.copy(pattern=r'*.py', dst=python_bin_folder, src=(self._source_subfolder + "/Generator"), keep_path=False, excludes=r'__init__.py')

    def package_id(self):
        self.info.header_only()
