# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import with_statement, print_function
"""
Setup script for python Fast Azimuthal Integration
"""

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "28/10/2015"
__status__ = "stable"

install_warning = True

import os
import time
import sys
import glob
import shutil
import platform
import subprocess
import numpy

try:
    # setuptools allows the creation of wheels
    from setuptools import setup, Command
    from setuptools.command.sdist import sdist
    from setuptools.command.build_ext import build_ext
    from setuptools.command.install_data import install_data
    from setuptools.command.install import install
except ImportError:
    from distutils.core import setup, Command
    from distutils.command.sdist import sdist
    from distutils.command.build_ext import build_ext
    from distutils.command.install_data import install_data
    from distutils.command.install import install
from numpy.distutils.core import Extension as _Extension


################################################################################
# Remove MANIFEST file ... it needs to be re-generated on the fly
################################################################################
manifest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MANIFEST")
if os.path.isfile(manifest):
    os.unlink(manifest)


def copy(infile, outfile, folder=None):
    "link or copy file according to the OS in the given folder"
    if folder:
        infile = os.path.join(folder, infile)
        outfile = os.path.join(folder, outfile)
    if os.path.exists(outfile):
        os.unlink(outfile)
    if "link" in dir(os):
        os.link(infile, outfile)
    else:
        shutil.copy(infile, outfile)


cmdclass = {}


# ################ #
# pyFAI extensions #
# ################ #

def check_cython():
    """
    Check if cython must be activated fron te command line or the environment.
    """

    if "WITH_CYTHON" in os.environ and os.environ["WITH_CYTHON"] == "False":
        print("No Cython requested by environment")
        return False

    if ("--no-cython" in sys.argv):
        sys.argv.remove("--no-cython")
        os.environ["WITH_CYTHON"] = "False"
        print("No Cython requested by command line")
        return False

    try:
        import Cython.Compiler.Version
    except ImportError:
        return False
    else:
        if Cython.Compiler.Version.version < "0.21":
            return False
    return True


def check_openmp():
    """
    Do we compile with OpenMP ?
    """
    if "WITH_OPENMP" in os.environ:
        print("OpenMP requested by environment: " + os.environ["WITH_OPENMP"])
        if os.environ["WITH_OPENMP"] == "False":
            return False
        else:
            return True
    if ("--no-openmp" in sys.argv):
        sys.argv.remove("--no-openmp")
        os.environ["WITH_OPENMP"] = "False"
        print("No OpenMP requested by command line")
        return False
    elif ("--openmp" in sys.argv):
        sys.argv.remove("--openmp")
        os.environ["WITH_OPENMP"] = "True"
        print("OpenMP requested by command line")
        return True

    if platform.system() == "Darwin":
        # By default Xcode5 & XCode6 do not support OpenMP, Xcode4 is OK.
        osx = tuple([int(i) for i in platform.mac_ver()[0].split(".")])
        if osx >= (10, 8):
            return False
    return True


USE_OPENMP = "openmp" if check_openmp() else ""
USE_CYTHON = check_cython()
if USE_CYTHON:
    from Cython.Build import cythonize


def Extension(name, source=None, can_use_openmp=False, extra_sources=None, **kwargs):
    """
    Wrapper for distutils' Extension
    """
    if source is None:
        source = name
    cython_c_ext = ".pyx" if USE_CYTHON else ".c"
    sources = [os.path.join("src", source + cython_c_ext)]
    if extra_sources:
        sources.extend(extra_sources)
    if "include_dirs" in kwargs:
        include_dirs = set(kwargs.pop("include_dirs"))
        include_dirs.add(numpy.get_include())
        include_dirs.add("src")
        include_dirs = list(include_dirs)
    else:
        include_dirs = ["src", numpy.get_include()]

    if can_use_openmp and USE_OPENMP:
        extra_compile_args = set(kwargs.pop("extra_compile_args", []))
        extra_compile_args.add(USE_OPENMP)
        kwargs["extra_compile_args"] = list(extra_compile_args)

        extra_link_args = set(kwargs.pop("extra_link_args", []))
        extra_link_args.add(USE_OPENMP)
        kwargs["extra_link_args"] = list(extra_link_args)

    ext = _Extension(name=name, sources=sources, include_dirs=include_dirs, **kwargs)

    if USE_CYTHON:
        cext = cythonize([ext], compile_time_env={"HAVE_OPENMP": bool(USE_OPENMP)})
        if cext:
            ext = cext[0]
    return ext

ext_modules = [
    Extension("_geometry", can_use_openmp=True),
    Extension("reconstruct", can_use_openmp=True),
    Extension('splitPixel'),
    Extension('splitPixelFull'),
    Extension('splitPixelFullLUT'),
    Extension('splitPixelFullLUT_double'),
    Extension('splitBBox'),
    Extension('splitBBoxLUT', can_use_openmp=True),
    Extension('splitBBoxCSR', can_use_openmp=True),
    Extension('splitPixelFullCSR', can_use_openmp=True),
    Extension('relabel'),
    Extension("bilinear", can_use_openmp=True),
    Extension('_distortion', can_use_openmp=True),
    Extension('_distortionCSR', can_use_openmp=True),
    Extension('_bispev', can_use_openmp=True),
    Extension('_convolution', can_use_openmp=True),
    Extension('_blob'),
    Extension('morphology'),
    Extension('marchingsquares'),
    Extension('watershed'),
    Extension('histogram', can_use_openmp=True)
]

if (os.name == "posix") and ("x86" in platform.machine()):
    ext_modules.append(
        Extension('fastcrc', extra_sources=[os.path.join("src", "crc32.c")])
    )


class build_ext_pyFAI(build_ext):
    """
    We subclass the build_ext class in order to handle compiler flags
    for openmp and opencl etc in a cross platform way
    """
    translator = {
        # Compiler
        # name, compileflag, linkflag
        'msvc': {
            'openmp': ('/openmp', ' '),
            'debug': ('/Zi', ' '),
            'OpenCL': 'OpenCL',
        },
        'mingw32': {
            'openmp': ('-fopenmp', '-fopenmp'),
            'debug': ('-g', '-g'),
            'stdc++': 'stdc++',
            'OpenCL': 'OpenCL'
        },
        'default': {
            'openmp': ('-fopenmp', '-fopenmp'),
            'debug': ('-g', '-g'),
            'stdc++': 'stdc++',
            'OpenCL': 'OpenCL'
        }
    }

    def build_extensions(self):
        # print("Compiler: %s" % self.compiler.compiler_type)
        if self.compiler.compiler_type in self.translator:
            trans = self.translator[self.compiler.compiler_type]
        else:
            trans = self.translator['default']

        for e in self.extensions:
            e.extra_compile_args = [trans[arg][0] if arg in trans else arg
                                    for arg in e.extra_compile_args]
            e.extra_link_args = [trans[arg][1] if arg in trans else arg
                                 for arg in e.extra_link_args]
            e.libraries = [trans[arg] for arg in e.libraries if arg in trans]
        build_ext.build_extensions(self)

cmdclass['build_ext'] = build_ext_pyFAI


# ############################# #
# scripts and data installation #
# ############################# #
def download_images():
    """
    Download all test images and
    """
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    sys.path.insert(0, test_dir)
    from utilstest import UtilsTest
    UtilsTest.download_images()
    return list(UtilsTest.ALL_DOWNLOADED_FILES)

installDir = "pyFAI"

data_files = [(os.path.join(installDir, "openCL"), glob.glob("openCL/*.cl")),
              (os.path.join(installDir, "gui"), glob.glob("gui/*.ui")),
              (os.path.join(installDir, "calibration"), glob.glob("calibration/*.D"))]

if sys.platform == "win32":
    # This is for mingw32/gomp
    if tuple.__itemsize__ == 4:
        data_files[0][1].append(os.path.join("dll", "pthreadGC2.dll"))
    root = os.path.dirname(os.path.abspath(__file__))
    tocopy_files = []
    script_files = []
    for i in os.listdir(os.path.join(root, "scripts")):
        if os.path.isfile(os.path.join(root, "scripts", i)):
            if i.endswith(".py"):
                script_files.append(os.path.join("scripts", i))
            else:
                tocopy_files.append(os.path.join("scripts", i))
    for i in tocopy_files:
        filein = os.path.join(root, i)
        if (filein + ".py") not in script_files:
            shutil.copyfile(filein, filein + ".py")
            script_files.append(filein + ".py")

else:
    script_files = glob.glob("scripts/*")


class smart_install_data(install_data):
    def run(self):
        global installDir

        install_cmd = self.get_finalized_command('install')
#        self.install_dir = join(getattr(install_cmd,'install_lib'), "data")
        self.install_dir = getattr(install_cmd, 'install_lib')
        print("DATA to be installed in %s" % self.install_dir)
        installDir = os.path.join(self.install_dir, installDir)
        return install_data.run(self)
cmdclass['install_data'] = smart_install_data


# #################################### #
# Test part and sdist with test images #
# #################################### #

def rewriteManifest(with_testimages=False):
    """
    Rewrite the "Manifest" file ... if needed

    @param with_testimages: include
    """
    base = os.path.dirname(os.path.abspath(__file__))
    manifest_in = os.path.join(base, "MANIFEST.in")
    if not os.path.isfile(manifest_in):
        print("%s file is missing !!!" % manifest_in)
        return

    with open(manifest_in) as f:
        manifest = [line.strip() for line in f]

    # get rid of all test images in the manifest_in
    manifest_new = [line for line in manifest
                    if not line.startswith("include test/testimages")]

    # add the testimages if required
    if with_testimages:
        testimages = ["include test/testimages/" + image for image in
                      os.listdir(os.path.join(base, "test", "testimages"))]
        manifest_new.extend(testimages)

    if manifest_new != manifest:
        with open(manifest_in, "w") as f:
            f.write(os.linesep.join(manifest_new))


class sdist_debian(sdist):
    """
    Tailor made sdist for debian
    * remove auto-generated doc
    * remove cython generated .c files
    * add image files from test/testimages/*
    """
    def prune_file_list(self):
        sdist.prune_file_list(self)
        to_remove = ["doc/build", "doc/pdf", "doc/html", "pylint", "epydoc"]
        print("Removing files for debian")
        for rm in to_remove:
            self.filelist.exclude_pattern(pattern="*", anchor=False, prefix=rm)
        # this is for Cython files specifically
        self.filelist.exclude_pattern(pattern="*.html", anchor=True, prefix="src")
        for pyxf in glob.glob("src/*.pyx"):
            cf = os.path.splitext(pyxf)[0] + ".c"
            if os.path.isfile(cf):
                self.filelist.exclude_pattern(pattern=cf)

#         print("Adding test_files for debian")
#         self.filelist.allfiles += [os.path.join("test", "testimages", i) \
#                                    for i in download_images()]
#         self.filelist.include_pattern(pattern="*", anchor=True,
#                                       prefix="test/testimages")

    def make_distribution(self):
        sdist.make_distribution(self)
        dest = self.archive_files[0]
        dirname, basename = os.path.split(dest)
        base, ext = os.path.splitext(basename)
        while ext in [".zip", ".tar", ".bz2", ".gz", ".Z", ".lz", ".orig"]:
            base, ext = os.path.splitext(base)
        if ext:
            dest = "".join((base, ext))
        else:
            dest = base
        sp = dest.split("-")
        base = sp[:-1]
        nr = sp[-1]
        debian_arch = os.path.join(dirname, "-".join(base) + "_" + nr + ".orig.tar.gz")
        os.rename(self.archive_files[0], debian_arch)
        self.archive_files = [debian_arch]
        print("Building debian .orig.tar.gz in %s" % self.archive_files[0])

cmdclass['debian_src'] = sdist_debian


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.chdir("test")
        errno = subprocess.call([sys.executable, 'test_all.py'])
        if errno != 0:
            raise SystemExit(errno)
        else:
            os.chdir("..")
cmdclass['test'] = PyTest

# ################### #
# build_doc commandes #
# ################### #

try:
    import sphinx
    import sphinx.util.console
    sphinx.util.console.color_terminal = lambda: False
    from sphinx.setup_command import BuildDoc
except ImportError:
    sphinx = None

if sphinx:
    class build_doc(BuildDoc):

        def run(self):

            # make sure the python path is pointing to the newly built
            # code so that the documentation is built on this and not a
            # previously installed version

            build = self.get_finalized_command('build')
            sys.path.insert(0, os.path.abspath(build.build_lib))

            # Copy gui files to the path:
            dst = os.path.join(os.path.abspath(build.build_lib), "pyFAI", "gui")
            if not os.path.isdir(dst):
                os.makedirs(dst)
            for i in os.listdir("gui"):
                if i.endswith(".ui"):
                    src = os.path.join("gui", i)
                    idst = os.path.join(dst, i)
                    if not os.path.exists(idst):
                        shutil.copy(src, idst)

            # Build the Users Guide in HTML and TeX format
            for builder in ('html', 'latex'):
                self.builder = builder
                self.builder_target_dir = os.path.join(self.build_dir, builder)
                self.mkpath(self.builder_target_dir)
                BuildDoc.run(self)
            sys.path.pop(0)
    cmdclass['build_doc'] = build_doc


if install_warning:
    class InstallWarning(install):
        def __init__(self, *arg, **kwarg):
            print("The usage of 'python setup.py is deprecated. Please use 'pip install .' instead")
            time.sleep(5)
            install.__init__(self, *arg, **kwarg)
    cmdclass['install'] = InstallWarning


def get_version():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyFAI-src"))
    import _version
    sys.path.pop(0)
    return _version.strictversion

classifiers = ["Development Status :: 5 - Production/Stable",
               "Intended Audience :: Developers",
               "Programming Language :: Python :: 2",
               "Programming Language :: Python :: 3",
               "Programming Language :: Cython",
               "Environment :: Console",
               "Environment :: X11 Applications :: Qt",
               "Intented Audience :: Science/Research",
               "License :: OSI Approved :: GNU General Public License (GPL)",
               "License :: OSI Approved :: MIT License",
               "Topic :: Software Development :: Libraries :: Python Modules",
               "Operating System :: Microsoft :: Windows",
               "Operating System :: Unix",
               "Operating System :: MacOS :: MacOS X",
               "Operating System :: POSIX",
               "Topic :: Scientific/Engineering :: Physics"
               ]

install_requires = ["numpy", "h5py", "fabio", "matplotlib", "scipy"]
setup_requires = ["numpy", "cython"]

packages = ["pyFAI", "pyFAI.test"]
package_dir = {"pyFAI": "pyFAI-src",
               "pyFAI.test": "test"}

if os.path.isdir("third_party"):
    package_dir["pyFAI.third_party"] = "third_party"
    packages.append("pyFAI.third_party")


if __name__ == "__main__":
    setup(name='pyFAI',
          version=get_version(),
          author="Jérôme Kieffer (python), \
          Peter Boesecke (geometry), Manuel Sanchez del Rio (algorithm), \
          Vicente Armando Sole (algorithm), \
          Dimitris Karkoulis (GPU), Jon Wright (adaptations) \
          and Frederic-Emmanuel Picca",
          author_email="jerome.kieffer@esrf.fr",
          description='Python implementation of fast azimuthal integration',
          url="https://github.com/pyFAI/pyFAI",
          download_url="https://github.com/pyFAI/pyFAI/releases",
          ext_package="pyFAI",
          scripts=script_files,
          ext_modules=ext_modules,
          packages=packages,
          package_dir=package_dir,
          test_suite="test",
          cmdclass=cmdclass,
          data_files=data_files,
          classifiers=classifiers,
          long_description="""PyFAI is an azimuthal integration library that tries to be fast (as fast as C
    and even more using OpenCL and GPU).
    It is based on histogramming of the 2theta/Q positions of each (center of)
    pixel weighted by the intensity of each pixel, but parallel version use a
    SparseMatrix-DenseVector multiplication.
    Neighboring output bins get also a contribution of pixels next to the border
    thanks to pixel splitting.
    Finally pyFAI provides also tools to calibrate the experimental setup using Debye-Scherrer
    rings of a reference compound.
          """,
          license="GPL",
          install_requires=install_requires,
          setup_requires=setup_requires,
          )
