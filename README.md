
# Qiskit QCGPU Provider

This module contains [Qiskit](https://www.qiskit.org/) 
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

The usage of this backend with Qiskit is shown in the [usage example](https://github.com/Qiskit/qiskit-qcgpu-provider/tree/master/examples)

For more information on Qiskit and quantum simulations, look at the Qiskit tutorials and the [Qiskit instructions page](https://github.com/Qiskit/qiskit-terra)

## Benchmarking

To benchmark this simulator against the `BasicAer` `qasm_simulator`,
you can run

```bash
$ python3 benchmark.py --samples 15  --qubits 5 --single True
```

## License

This project uses the [Apache License Version 2.0 software license.](https://www.apache.org/licenses/LICENSE-2.0)
