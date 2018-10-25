
# Qiskit QCGPU Provider

This module contains [QISKit](https://www.qiskit.org/) 
simulators using the OpenCL based [QCGPU](https://qcgpu.github.io) library.

This provider adds two quantum circuit simulators, which are:

* Statevector simulator - returns the statevector of a quantum circuit applied to the |0> state
* Qasm simulator - simulates a qasm quantum circuit that has been compiled to run on the simulator.

These simulation backends take advantage of the GPU or other OpenCL devices.

## Installation

First of all, you will have to have some OpenCL installation installed already.

You can install this module from PyPI using pip:

```bash
$ pip install qiskit-qcgpu-provider
```


## Usage

The usage of this backend with QISKit is shown in the [usage example](https://github.com/Qiskit/qiskit-qcgpu-provider/tree/master/examples)

For more information on QISKit and quantum simulations, look at the QISKit tutorials and the [QISKit instructions page](https://github.com/Qiskit/qiskit-terra)

## License

This project uses the [Apache License Version 2.0 software license.](https://www.apache.org/licenses/LICENSE-2.0)
