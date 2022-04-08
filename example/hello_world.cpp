#include <nanobind/nanobind.h>

NANOBIND_MODULE(hello_world, m)
{
    m.def("hello", []() { return "Hello World!"; });
}
