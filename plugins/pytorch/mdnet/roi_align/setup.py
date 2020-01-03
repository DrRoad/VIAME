import os
import torch

from setuptools import setup, find_packages

from torch.utils.cpp_extension import BuildExtension, CUDAExtension, CppExtension

modules = []

if torch.cuda.is_available():
    modules.append(
        CUDAExtension(
            'roi_align._ext.roi_align',
            ['roi_align/src/roi_align_cuda.c',
             'roi_align/src/roi_align_kernel.cu'],
            extra_compile_args={'cxx': ['-g'],
                                'nvcc': ['-O2']}
        )
    )

setup(
    name='roi_align',
    version='1.0.0',
    description='PyTorch version of RoIAlign specific to MDNet',
    author='VIAME',
    author_email='viame.developers@gmail.com',
    url='https://github.com/VIAME/VIAME/tree/master/plugins/pytorch/mdnet',
    packages=find_packages(exclude=('tests',)),
    ext_modules=modules,
    cmdclass={'build_ext': BuildExtension},
    install_requires=['torch>=1.0.0']
)
