"""
Setup for qiskit-qcgpu-provider.
"""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="qiskit-qcgpu-provider",
    version="0.2.0",
    author="Adam Kelly",
    author_email="adamkelly2201@gmail.com",
    description="An OpenCL based quantum computer simulator",
    long_description=LONG_DESCRIPTION,
    url="https://qcgpu.github.io",
    packages=setuptools.find_packages(),
    setup_requires=['qcgpu>=0.1.0'],
    license="Apache 2.0",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=['qiskit>=0.7', 'qcgpu>=0.1.0'],
    python_requires=">=3.5"
)
