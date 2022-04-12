#include <nanobind/nanobind.h>

NB_MODULE(hello_world, m)
{
    m.def("hello", []() { return "Hello World!"; });
}
