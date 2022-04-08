========
pybind11
========

|CMake| |Linux Waf| |No Assertions| |Cppcheck|

.. |CMake| image:: https://github.com/steinwurf/pybind11/actions/workflows/cmake.yml/badge.svg
   :target: https://github.com/steinwurf/pybind11/actions/workflows/cmake.yml

.. |Linux Waf| image:: https://github.com/steinwurf/pybind11/actions/workflows/linux_waf.yml/badge.svg
   :target: https://github.com/steinwurf/pybind11/actions/workflows/linux_waf.yml

.. |No Assertions| image:: https://github.com/steinwurf/pybind11/actions/workflows/nodebug.yml/badge.svg
   :target: https://github.com/steinwurf/pybind11/actions/workflows/nodebug.yml
   
.. |Cppcheck| image:: https://github.com/steinwurf/pybind11/actions/workflows/cppcheck.yml/badge.svg
   :target: https://github.com/steinwurf/pybind11/actions/workflows/cppcheck.yml
   
This repository contains waf build scripts for https://github.com/pybind/pybind11
that are necessary for integration with other Steinwurf libraries.

.. contents:: Table of Contents:
   :local:

Quick Start
-----------

If you already installed a C++14 compiler, git and python on your system,
then you can clone this repository to a suitable folder::

    git clone git@github.com:steinwurf/pybind11.git

Configure and build the project::

    cd pybind11
    python waf configure
    python waf build

Run the unit tests::

    python waf --run_tests

On windows you may need to set the `MSSdk` and `DISTUTILS_USE_SDK`
environment variables to configure the project.
