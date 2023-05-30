#!/usr/bin/env python

__copyright__ = """
Copyright (C) 2011-20 Andreas Kloeckner
"""

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from skbuild import setup
import sys


def get_config_schema():
    from aksetup_helper import (ConfigSchema,
            IncludeDir, LibraryDir, Libraries,
            Switch, StringListOption)

    default_cxxflags = [
            # Required for pybind11:
            # https://pybind11.readthedocs.io/en/stable/faq.html#someclass-declared-with-greater-visibility-than-the-type-of-its-field-someclass-member-wattributes
            "-fvisibility=hidden"
            ]

    return ConfigSchema([
        Switch("USE_SHIPPED_ISL", True, "Use included copy of isl"),
        Switch("USE_SHIPPED_IMATH", True, "Use included copy of imath in isl"),
        Switch("USE_GMP", True, "Use gmp in external isl"),
        Switch("USE_BARVINOK", False, "Include wrapper for Barvinok"),
        Switch("USE_IMATH_SIO", True, "When using imath, use small-integer "
            "optimization"),

        IncludeDir("GMP", []),
        LibraryDir("GMP", []),
        Libraries("GMP", ["gmp"]),

        IncludeDir("ISL", []),
        LibraryDir("ISL", []),
        Libraries("ISL", ["isl"]),

        IncludeDir("BARVINOK", []),
        LibraryDir("BARVINOK", []),
        Libraries("BARVINOK", ["barvinok", "polylibgmp"]),

        StringListOption("CXXFLAGS", default_cxxflags,
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [],
            help="Any extra linker options to include"),
        ])


# {{{ awful monkeypatching to fix the isl (not islpy) build on Mac/clang

class Hooked_compile:  # noqa: N801
    def __init__(self, orig__compile, compiler):
        self.orig__compile = orig__compile
        self.compiler = compiler

    def __call__(self, obj, src, *args, **kwargs):
        compiler = self.compiler
        prev_compiler_so = compiler.compiler_so

        if src.endswith(".c"):
            # Some C compilers (Apple clang IIRC?) really don't like having C++
            # flags passed to them.
            options = [opt for opt in args[2]
                if "-std=gnu++" not in opt and "-std=c++" not in opt]

            import sys
            # https://github.com/inducer/islpy/issues/39
            if sys.platform == "darwin":
                options.append("-Wno-error=implicit-function-declaration")

            args = args[:2] + (options,) + args[3:]

        try:
            result = self.orig__compile(obj, src, *args, **kwargs)
        finally:
            compiler.compiler_so = prev_compiler_so
        return result


# class IslPyBuildExtCommand(PybindBuildExtCommand):
#     def __getattribute__(self, name):
#         if name == "compiler":
#             compiler = PybindBuildExtCommand.__getattribute__(self, name)
#             if compiler is not None:
#                 orig__compile = compiler._compile
#                 if not isinstance(orig__compile, Hooked_compile):
#                     compiler._compile = Hooked_compile(orig__compile, compiler)
#             return compiler
#         else:
#             return PybindBuildExtCommand.__getattribute__(self, name)

# }}}


def main():
    from skbuild import setup
    import nanobind  # noqa: F401
    from setuptools import find_packages

    # {{{ import aksetup_helper bits

    prev_path = sys.path[:]
    # FIXME skbuild seems to remove this. Why?
    sys.path.append(".")

    from aksetup_helper import get_config, check_git_submodules
    from gen_wrap import gen_wrapper

    sys.path = prev_path

    # }}}

    check_git_submodules()

    conf = get_config(get_config_schema(), warn_about_no_config=False)

    cmake_args = []

    CXXFLAGS = conf["CXXFLAGS"]  # noqa: N806

    EXTRA_OBJECTS = []  # noqa: N806
    EXTRA_DEFINES = {}  # noqa: N806

    INCLUDE_DIRS = ["src/wrapper"]  # noqa: N806
    LIBRARY_DIRS = []  # noqa: N806
    LIBRARIES = []  # noqa: N806

    LIBRARY_DIRS.extend(conf["ISL_LIB_DIR"])
    LIBRARIES.extend(conf["ISL_LIBNAME"])

    wrapper_dirs = conf["ISL_INC_DIR"][:]

    INCLUDE_DIRS.extend(conf["ISL_INC_DIR"])

    if not (conf["USE_SHIPPED_ISL"] and conf["USE_SHIPPED_IMATH"]) and \
            conf["USE_GMP"]:
        INCLUDE_DIRS.extend(conf["GMP_INC_DIR"])
        LIBRARY_DIRS.extend(conf["GMP_LIB_DIR"])
        LIBRARIES.extend(conf["GMP_LIBNAME"])

    init_filename = "islpy/version.py"
    with open(init_filename) as version_f:
        version_py = version_f.read()
    exec(compile(version_py, init_filename, "exec"), conf)

    gen_wrapper(wrapper_dirs, include_barvinok=conf["USE_BARVINOK"])

    with open("README.rst") as readme_f:
        readme = readme_f.read()

    if conf["ISL_INC_DIR"]:
        cmake_args.append(f"-DISL_INC_DIR:LIST="
                f"{';'.join(conf['ISL_INC_DIR'])}")

    if conf["ISL_LIB_DIR"]:
        cmake_args.append(f"-DISL_LIB_DIR:LIST="
                f"{';'.join(conf['ISL_LIB_DIR'])}")

    cmake_args.append(f"-DISL_LIBRARY={conf['ISL_LIBNAME'][0]}")

    print(f"{cmake_args=}")

    setup(name="islpy",
          version=conf["VERSION_TEXT"],
          description="Wrapper around isl, an integer set library",
          long_description=readme,
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          license="MIT",
          url="http://documen.tician.de/islpy",
          classifiers=[
              "Development Status :: 4 - Beta",
              "Intended Audience :: Developers",
              "Intended Audience :: Other Audience",
              "Intended Audience :: Science/Research",
              "License :: OSI Approved :: MIT License",
              "Natural Language :: English",
              "Programming Language :: C++",
              "Programming Language :: Python",
              "Programming Language :: Python :: 3",
              "Topic :: Multimedia :: Graphics :: 3D Modeling",
              "Topic :: Scientific/Engineering",
              "Topic :: Scientific/Engineering :: Mathematics",
              "Topic :: Scientific/Engineering :: Physics",
              "Topic :: Scientific/Engineering :: Visualization",
              "Topic :: Software Development :: Libraries",
              ],

          packages=find_packages(),

          python_requires="~=3.8",
          extras_require={
              "test": ["pytest>=2"],
              },
          cmake_args=cmake_args,
        #   ext_modules=[
        #       Extension(
        #           "islpy._isl",
        #           [
        #               "src/wrapper/wrap_isl.cpp",
        #               "src/wrapper/wrap_isl_part1.cpp",
        #               "src/wrapper/wrap_isl_part2.cpp",
        #               "src/wrapper/wrap_isl_part3.cpp",
        #               ] + EXTRA_OBJECTS,
        #           include_dirs=INCLUDE_DIRS + [
        #               get_pybind_include(),
        #               get_pybind_include(user=True)
        #               ],
        #           library_dirs=LIBRARY_DIRS,
        #           libraries=LIBRARIES,
        #           define_macros=list(EXTRA_DEFINES.items()),
        #           extra_compile_args=CXXFLAGS,
        #           extra_link_args=conf["LDFLAGS"],
        #           ),
        #       ],
          cmake_install_dir="islpy",
          )


if __name__ == "__main__":
    main()
