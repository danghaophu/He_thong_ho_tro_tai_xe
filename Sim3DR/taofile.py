from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("E:\do an tot nghiep\SafeDriveVision-master\SafeDriveVision-master\Sim3DR\Sim3DR.py")
)
