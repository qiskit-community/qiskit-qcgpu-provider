import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qiskit-addon-qcgpu",
    version="0.0.1",
    author="Adam Kelly",
    author_email="adamkelly2201@gmail.com",
    description="An OpenCL based quantum computer simulator",
    long_description=long_description,
    url="https://qcgpu.github.io",
    packages=setuptools.find_packages(),
    setup_requires=['qcgpu']
)