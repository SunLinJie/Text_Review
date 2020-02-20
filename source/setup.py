# -*- coding: utf-8 -*-
from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("aimodel_kw.py")
)

setup(
    ext_modules = cythonize("aimodel_fnlp.py")
)

# setup(
#     ext_modules = cythonize("hmai/hmai_gate_nlp.pyx")
# )
# setup(
#     ext_modules = cythonize("hmai/hmai_group_nlp.pyx")
# )



# python setup.py build_ext --inplace
