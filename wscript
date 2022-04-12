#! /usr/bin/env python
# encoding: utf-8

import os
from waflib.extras.wurf.directory import remove_directory

APPNAME = "nanobind"
VERSION = "1.0.0"


def options(opt):

    if opt.is_toplevel():

        opt.load("python")

        opt.add_option(
            "--test_filter",
            default=None,
            action="store",
            help="Run all tests that include the substring specified."
            "Wildcards not allowed. (Used with --run_tests)",
        )


def configure(conf):

    # Configure Python extension flags if necessary
    # (boost-python might have already completed the Python configuration)
    error_message = "Python was not configured properly"
    if "BUILD_PYTHON" not in conf.env:
        try:
            conf.load("python")
            conf.check_python_headers()
            conf.check_python_version(minver=(3, 8))
            conf.env["BUILD_PYTHON"] = True
        except Exception as e:
            conf.env["BUILD_PYTHON"] = False
            error_message += "\n" + str(e)

    # If the Python configuration failed, then we cannot continue
    if not conf.env["BUILD_PYTHON"]:
        conf.fatal(error_message)

    os_env = dict(os.environ)

    PYTHON_ENVIRONMENT_VARIABLES = "prefix SO LDFLAGS LIBDIR LIBPL INCLUDEPY Py_ENABLE_SHARED MACOSX_DEPLOYMENT_TARGET LDSHARED CFLAGS LDVERSION".split()
    lst = conf.get_python_variables(
        ["get_config_var('%s') or ''" % x for x in PYTHON_ENVIRONMENT_VARIABLES],
        ["from distutils.sysconfig import get_config_var, get_python_lib"],
    )
    PYTHON_VERSION = lst[-1]
    python_includes = [str(x) for x in lst if str(x).startswith("/usr/include/python3")]

    if len(python_includes) > 1:
        found_include_matching = False
        for include in python_includes:
            if include.endswith(PYTHON_VERSION, -len(PYTHON_VERSION), -1):
                python_includes = include
                found_include_matching = True
                break
        if not found_include_matching:
            conf.fatal("Could not find matching python3-dev and python3 version")
    else:
        python_includes = python_includes[0]
    CXX = conf.env.get_flat("CXX")

    # Override python-config's compiler flags, because these are not
    # compatible with the common C++ flags defined in our waf-tools
    conf.env["DEFINES_PYEXT"] = []
    conf.env["CFLAGS_PYEXT"] = []
    conf.env["CXXFLAGS_PYEXT"] = []

    # Python extensions are shared libraries, so all the object files that
    # are included in the library must be compiled using the -fPIC flag
    # (position independent code). We can only guarantee this if the flag
    # is added globally in waf for compiling all C/C++ source files.
    if "g++" in CXX or "clang" in CXX:
        conf.env.append_value("CFLAGS", "-fPIC")
        conf.env.append_value("CXXFLAGS", "-fPIC")
        conf.env.append_value("CXXFLAGS", "-fno-stack-protector")

    # Add some cxxflags to suppress some compiler-specific warnings
    cxxflags = ["-I" + python_includes]
    # The deprecated "register" keyword is present in some Python 2.7 headers,
    # so the following flags are used to suppress these warnings (which are
    # treated as errors in C++17 mode)
    if "g++" in CXX or "clang" in CXX:
        cxxflags += ["-Wno-register"]
    # For MSVC, disable the C5033 warning (deprecated register keyword)
    if "CL.exe" in CXX or "cl.exe" in CXX:
        cxxflags += ["/wd5033"]
    # nanobind is explicitly invoking sized deallocation:
    # https://github.com/pybind/nanobind/issues/1604
    # So this flag is needed for clang in C++17 mode:
    if "clang" in CXX:
        cxxflags += ["-fsized-deallocation"]

    conf.env["CXXFLAGS_NB"] = cxxflags


def build(bld):

    # Path to the source repo
    dir = bld.dependency_node("nanobind-source")
    sources = dir.find_dir("src")
    includes = [dir.find_dir("include"), dir.find_dir("ext/robin_map/include")]

    bld(
        features="cxx cxxshlib",
        source=sources.ant_glob("*.cpp"),
        target="nanobind",
        export_includes=[includes],
        includes=includes,
        use=["NB"],
        install_path="${PREFIX}/lib",
    )

    if bld.is_toplevel():

        # The actual sources are stored outside this repo - so we manually
        # add them for the solution generator
        bld.msvs_extend_sources = [sources, includes]

    if bld.is_toplevel():
        bld(
            features="cxx cxxshlib pyext",
            source="example/hello_world.cpp",
            target="hello_world",
            use=[],
        )

        # bld.recurse("test")

        if bld.has_tool_option("run_tests"):
            bld.add_post_fun(exec_test_python)


def exec_test_python(ctx):

    with ctx.create_virtualenv() as venv:

        # Install pytest in the virtualenv
        # The nanobind tests are not compatible with this ExceptionInfo change:
        # https://github.com/pytest-dev/pytest/pull/5413
        # that was added in pytest 5.0.0, so we must use an earlier version
        venv.run('python -m pip install "pytest<5.0.0"')
        venv.run('python -m pip install "numpy"')

        testdir = ctx.dependency_node("nanobind-source").find_node("tests")

        # Use -B to avoid writing any .pyc files
        command = "python -B -m pytest {}".format(testdir.abspath())

        # Adds the test filter if specified
        if ctx.options.test_filter:
            command += ' -k "{}"'.format(ctx.options.test_filter)
        else:
            # By default, disable the tests are not supported by runners
            command += ' -k "not test_chrono and not test_iostream and not test_eigen and not test_cross_module_gil"'

        venv.env["PYTHONPATH"] = os.path.join(ctx.out_dir, "test")
        venv.run(command)
