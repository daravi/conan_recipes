#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class MongoCDriverConan(ConanFile):
	name = "mongo-c-driver"
	version = "1.16.0"
	description = "A high-performance MongoDB driver for C"
	topics = ("libmongoc", "mongodb", "db")
	homepage = "https://github.com/mongodb/{0}".format(name)
	license = "Apache-2.0"
	url = "https://github.com/mongodb/{0}/releases/download/{1}/{0}-{1}.tar.gz".format(name, version)
	exports_sources = ["Find*.cmake", "header_path.patch", "CMakeLists.txt"]
	generators = "cmake"

	settings = "os", "compiler", "arch", "build_type"
	options = {"shared": [True, False], "fPIC": [True, False]}
	default_options = {'shared': False, 'fPIC': True}

	_source_subfolder = "source_subfolder"
	_build_subfolder = "build_subfolder"

	requires = "Zlib/1.2.11@3rdparty/stable"

	def configure(self):
		# Because this is pure C
		del self.settings.compiler.libcxx

	def config_options(self):
		if self.settings.os == "Windows":
			del self.options.fPIC

	def requirements(self):
		if not tools.os_info.is_macos and not tools.os_info.is_windows:
			self.requires.add("OpenSSL/1.0.2o@3rdparty/stable")

	def source(self):
		tools.get(self.url)
		extracted_dir = self.name + "-" + self.version
		os.rename(extracted_dir, self._source_subfolder)
		tools.patch(base_path=self._source_subfolder, patch_file="header_path.patch")

	def _configure_cmake(self):
		cmake = CMake(self)
		cmake.definitions["ENABLE_TESTS"] = False
		cmake.definitions["ENABLE_EXAMPLES"] = False
		cmake.definitions["ENABLE_AUTOMATIC_INIT_AND_CLEANUP"] = False
		cmake.definitions["ENABLE_BSON"] = "ON"
		cmake.definitions["ENABLE_SASL"] = "OFF"
		cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
		cmake.definitions["ENABLE_EXTRA_ALIGNMENT"] = "OFF"

		cmake.configure(build_folder=self._build_subfolder)

		return cmake

	def build(self):
		cmake = self._configure_cmake()
		cmake.build()

	def package(self):
		self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
		self.copy("Find*.cmake", ".", ".")

		# cmake installs all the files
		cmake = self._configure_cmake()
		cmake.install()

	def package_info(self):
		self.cpp_info.libs = ['mongoc-1.0', 'bson-1.0'] if self.options.shared \
			else ['mongoc-static-1.0', 'bson-static-1.0']

		if tools.os_info.is_macos:
			self.cpp_info.exelinkflags = [
				'-framework CoreFoundation', '-framework Security']
			self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

		if tools.os_info.is_linux:
			self.cpp_info.libs.extend(["rt", "pthread"])

		if not self.options.shared:
			self.cpp_info.defines.extend(['BSON_STATIC=1', 'MONGOC_STATIC=1'])

			if tools.os_info.is_linux or tools.os_info.is_macos:
				self.cpp_info.libs.append('resolv')

			if tools.os_info.is_windows:
				self.cpp_info.libs.extend(
					['ws2_32.lib', 'secur32.lib', 'crypt32.lib', 'BCrypt.lib', 'Dnsapi.lib'])
