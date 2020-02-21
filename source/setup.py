# -*- coding: utf-8 -*-
from distutils.core import setup
from Cython.Build import cythonize

# setup(
#     ext_modules = cythonize("aimodel_kw.py")
# )
#
# setup(
#     ext_modules = cythonize("aimodel_fnlp.py")
# )
#
# setup(
#     ext_modules = cythonize("aimodel_cherry.py")
# )
#
# setup(
#     ext_modules = cythonize("hmai/hmai_gate_nlp.py")
# )
# setup(
#     ext_modules = cythonize("hmai/hmai_group_nlp.py")
# )
setup(
    ext_modules = cythonize("hmai/hmai_base_aimodel.py")
)


# python setup.py build_ext --inplace
