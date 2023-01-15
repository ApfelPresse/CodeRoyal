import numpy
from Cython.Build import cythonize
from setuptools import setup

setup(
    ext_modules=cythonize(
        [
            'ref.pyx'
        ],
        compiler_directives={
            'language_level': "3",
            # 'cdivision': True,
            # 'binding': True,
            # 'boundscheck': False,
            # 'nonecheck': False,
            # 'wraparound': False,
            # 'overflowcheck': False,
            # 'cpp_locals': True,
        },
        annotate=True,
    ),
    include_dirs=[numpy.get_include()]
)
