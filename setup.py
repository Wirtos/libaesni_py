import os
import subprocess
import shutil
import sys
import json

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, cmake_target, cmake_lists_dir, name=None, cmake_options=None, cmake_install_lib_prefix='lib',
                 **kwargs):
        if cmake_options is None:
            cmake_options = []
        Extension.__init__(self, name if name else cmake_target, sources=[], **kwargs)
        self.cmake_lists_dir = os.path.abspath(cmake_lists_dir)
        self.cmake_options = cmake_options
        self.cmake_target = cmake_target
        self.cmake_install_lib_prefix = cmake_install_lib_prefix


class CMakeBuild(build_ext):
    def build_extensions(self):
        # Ensure that CMake is present and working
        try:
            v = json.loads(subprocess.check_output(['cmake', '-E', 'capabilities']))["version"]
            cmake_version = (v['major'], v['minor'], v['patch'])
            cmake_version_required = (3, 14, 7)
            if cmake_version < cmake_version:
                raise RuntimeError('Required CMake version: >={}.{}.{}, found {}.{}.{}'.format(
                    *cmake_version_required, *cmake_version)
                )
        except OSError:
            raise RuntimeError('Cannot find CMake executable')

        for ext in self.extensions:
            cfg = 'Release' if not self.debug else 'Debug'
            install_dir = os.path.join(os.pathsep, os.path.abspath(self.build_temp), "install")

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            # Config
            cmake_build_dir = '{}_build'.format(ext.name)
            print("bdir", cmake_build_dir)
            subprocess.check_call(['cmake',
                                   '-S', ext.cmake_lists_dir,
                                   '-B', cmake_build_dir,
                                   '-DCMAKE_BUILD_TYPE={}'.format(cfg),
                                   *ext.cmake_options,
                                   '-DCMAKE_INSTALL_PREFIX={}'.format(install_dir),
                                   '-DPYTHON_VERSION=' + '.'.join(str(i) for i in sys.version_info[0:2])
                                   ],

                                  cwd=self.build_temp)

            # Build
            subprocess.check_call(
                ['cmake', '--build', cmake_build_dir, '--config', cfg, "--target", "install"],
                cwd=self.build_temp)

            library_file = os.path.join(os.pathsep,
                                        install_dir, ext.cmake_install_lib_prefix, ext.cmake_target + ".pyd")
            expected_lib_file = self.get_ext_fullpath(ext.name)
            expected_lib_dir = os.path.split(expected_lib_file)[0]
            if not os.path.exists(expected_lib_dir):
                os.makedirs(expected_lib_dir)
            shutil.copy(
                library_file,
                expected_lib_file
            )


setup(
    name="libaesni_py",
    version="0.1",
    ext_modules=[
        CMakeExtension(cmake_target="libaesni_py",
                       cmake_lists_dir=".",
                       cmake_options=['-DCMAKE_ASM_NASM_COMPILER=yasm']
                       )
    ],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
)
