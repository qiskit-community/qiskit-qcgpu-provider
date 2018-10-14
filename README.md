# QCGPU simulator backend for QISKit

> Pluggable [QCGPU](https://qcgpu.github.io) simulator backend for QISKit Core 

This module contains a [QISKit](https://www.qiskit.org/) simulator whose backend is based on the OpenCL based [QCGPU](https://qcgpu.github.io) library.
This simulates a quantum circuit on a classical computer.

## Installation

First of all, you will have to have some OpenCL installation installed already.

You can install this module from PyPI using pip:

```bash
pip install qiskit-addon-qcgpu
```


## Usage

The usage of this backend with QISKit is shown in the [usage example](https://github.com/QCGPU/qiskit-addon-qcgpu/blob/master/examples/qcgpu_backend.py).

For more information on QISKit and quantum simulations, look at the QISKit tutorials and the [QISKit instructions page](https://github.com/QISKit/qiskit-core)

## License

Licensed under the [MIT license](https://opensource.org/licenses/MIT), see `LICENSE.md`
