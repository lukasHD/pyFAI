pyFAI: Fast Azimuthal Integration in Python
===========================================

Main development website: https://github.com/kif/pyFAI

|Build Status| |Appveyor Status|

pyFAI is an azimuthal integration library that tries to be fast (as fast as C
and even more using OpenCL and GPU).
It is based on histogramming of the 2theta/Q positions of each (center of)
pixel weighted by the intensity of each pixel, but parallel version use a
SparseMatrix-DenseVector multiplication.
Neighboring output bins get also a contribution of pixels next to the border
thanks to pixel splitting.
Finally pyFAI provides also tools to calibrate the experimental setup using Debye-Scherrer
rings of a reference compound.

References:
-----------

* The philosophy of pyFAI is described in the proceedings of SRI2012:
  doi:10.1088/1742-6596/425/20/202012 http://iopscience.iop.org/1742-6596/425/20/202012/
* Implementation in parallel is described in the proceedings of EPDIC13:
  PyFAI: a Python library for high performance azimuthal integration on GPU.
  doi:10.1017/S0885715613000924
* Benchmarks and optimization procedure is described in the proceedings of EuroSciPy2014:
  http://conference.scipy.org/category/euroscipy.html (accepted)


Installation
------------

pyFAI can be downloaded from the http://forge.epn-campus.eu/projects/azimuthal/files.
Presently the source code has been distributed as a zip package and a compressed
tarball. Download either one and unpack it.
Developement is done on Github: https://github.com/pyFAI/pyFAI

e.g.

::
    tar xvzf pyFAI-0.11.0.tar.gz

or

::
    unzip pyFAI-0.11.0.zip

All files are unpacked into the directory pyFAI-0.11.0::

    cd pyFAI-0.10.3

Build it & test it::

    python setup.py build test

For its tests, pyFAI downloads test images from the internet.
Depending on your network connection and your local network configuration,
you may have to setup a proxy configuration like this::
   export http_proxy=http://proxy.site.org:3128
   python setup.py build test

This is especially true at ESRF, where you will have to phone the hotline
(24-24) to get this information or grab it from the intranet.

Finally, install pyFAI computer-wise if you have local root access.
This command may request your password to gain root-access::

    sudo pip install . --upgrade

If you prefer a local installation (only you will have access to the
installed version)::

    python setup.py install --user

The newest development version can be obtained by checking it out from the git repository.::

    git clone https://github.com/pyFAI/pyFAI.git
    cd pyFAI
    python setup.py build bdist_wheel
    sudo pip install .

If you want pyFAI to make use of your graphic card, please install pyopencl from:
http://mathema.tician.de/software/pyopencl

If you are using MS Windows you can also download a binary version packaged as executable
installation files (Chose the one corresponding to your python version).

For MacOSX users with MacOS version>10.7, the default compiler switched from gcc
to clang and dropped the OpenMP support. Three options for you:

* Install a version of gcc (>4.2) on MacOSX
* use the "--no-openmp" option to setup.py (depends on Cython installed)

Documentation
-------------

Documentation can be build using this command and Sphinx (installed on your computer)::

    python setup.py build_doc


Dependencies
------------

Python 2.6, 2.7, 3.2, 3.3 or 3.4.
For full functionality of pyFAI the following modules need to be installed.

    * numpy 		- 	http://www.numpy.org
    * scipy 		- 	http://www.scipy.org
    * matplotlib 	- 	http://matplotlib.sourceforge.net/
    * fabio			-	http://sourceforge.net/projects/fable/files/fabio/
    * h5py			-   http://www.h5py.org/
    * pyopencl		-	http://mathema.tician.de/software/pyopencl/
    * python-qt4	-	http://www.riverbankcomputing.co.uk/software/pyqt/intro

Those dependencies can simply be installed by::

  pip install -r requirements.txt

Ubuntu and Debian Like linux distributions:
-------------------------------------------

To use pyFAI on Ubuntu/Debian the needed python modules
can be installed either through the Synaptic Package Manager (found in System -> Administration)
or using apt-get on from the command line in a terminal.
The extra ubuntu packages needed are:

    * python-numpy
    * python-scipy
    * python-matplotlib
    * python-dev
    * python-fabio
    * python-pyopencl
    * python-fftw
    * python-qt4

using apt-get these can be installed as::

    sudo apt-get install python-numpy python-scipy python-matplotlib  python-dev python-fabio python-pyopencl python-fftw python-qt4



MacOSX
------

You are advised to build pyFAI with the GCC compiler, clang (<3.5) laking the support of OpenMP.
If you use Xcode5, append the "--no-openmp" option to deactivate multithreading in binary modules

Windows
-------

Under 32 bits windows, pyFAI can be built using The MinGW compiler. Unfortunately,
pyFAI will be limited to small images as the memory consumption, limited to 2GB
under windows, easy easily reached. The VisualStudio C++ compiler works as well.
With 64 bits windows, the Visual Studio C++ compiler is the only one known to work correctly.

Dependencies for windows have been regrouped in our wheelhouse, just use::

  pip install --trusted-host www.edna-site.org -r requirements_appveyor.txt

Getting help
------------

A mailing-list, pyfai@esrf.fr, is available to get help on the program and how to use it.
One needs to subscribe by sending an email to sympa@esrf.fr with a subject "subscribe pyfai".


Maintainer
----------

 * Jérôme Kieffer (ESRF)

Contributors
------------

 * Frédéric-Emmanuel Picca (Soleil)
 * Dimitris Karkoulis (ESRF)
 * Aurore Deschildre (ESRF)
 * Giannis Ashiotis (ESRF)
 * Zubair Nawaz (Sesame)
 * Jon Wright (ESRF)
 * Amund Hov (ESRF)
 * Dodogerstlin @github
 * Gunthard Benecke (Desy)
 * Gero Flucke (Desy)

Indirect contributors (ideas, ...):
-----------------------------------

 * Peter Boesecke
 * Manuel Sánchez del Río
 * Vicente Armando Solé
 * Brian Pauw
 * Veijo Honkimaki

.. |Build Status| image:: https://travis-ci.org/kif/pyFAI.svg?branch=master
   :target: https://travis-ci.org/kif/pyFAI
.. |Appveyor Status| image:: https://ci.appveyor.com/api/projects/status/if0fdfftdh4iigpo?svg=true
   :target: https://ci.appveyor.com/project/kif/pyfai
