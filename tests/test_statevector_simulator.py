import unittest
import math

from qiskit_qcgpu_provider import QCGPUProvider
from qiskit import execute, QuantumRegister, QuantumCircuit, BasicAer
from qiskit.quantum_info import state_fidelity

from .case import MyTestCase


class TestStatevectorSimulator(MyTestCase):
    """Test the state vector simulator"""

    def test_computations(self):
        for n in range(2, 10):
            circ = self.random_circuit(n, 5)
            self._compare_outcomes(circ)

    def _compare_outcomes(self, circ):
        Provider = QCGPUProvider()
        backend_qcgpu = Provider.get_backend('statevector_simulator')
        statevector_qcgpu = execute(circ, backend_qcgpu).result().get_statevector()

        backend_qiskit = BasicAer.get_backend('statevector_simulator')
        statevector_qiskit = execute(circ, backend_qiskit).result().get_statevector()

        self.assertAlmostEqual(state_fidelity(statevector_qcgpu, statevector_qiskit), 1, 5)


if __name__ == '__main__':
    unittest.main()
