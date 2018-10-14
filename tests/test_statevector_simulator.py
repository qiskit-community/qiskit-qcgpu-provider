import unittest
import math

from qiskit_qcgpu_provider import QCGPUProvider
from qiskit import execute, QuantumRegister, QuantumCircuit


class TestStatevectorSimulator(unittest.TestCase):
    """Test the state vector simulator"""

    def setUp(self):
        q = QuantumRegister(2)
        circ = QuantumCircuit(q)

        circ.h(q[0])
        circ.cx(q[0], q[1])

        self.circ = circ

    def test_statevector_simulator(self):
        Provider = QCGPUProvider()
        backend = Provider.get_backend('statevector_simulator')
        result = execute(self.circ, backend).result()
        statevector = result.get_statevector()

        self.assertEqual(result.get_status(), 'COMPLETED')
        self.assertAlmostEqual(statevector[0], math.sqrt(2) / 2)
        self.assertEqual(statevector[1], 0)
        self.assertEqual(statevector[2], 0)
        self.assertAlmostEqual(statevector[3], math.sqrt(2) / 2)


if __name__ == '__main__':
    unittest.main()
