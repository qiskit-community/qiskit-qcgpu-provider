from qiskit_qcgpu_provider import QCGPUProvider
from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit import compile

import unittest

from .case import MyTestCase


class TestQasmSimulator(MyTestCase):
    """
    Test the QASM Simulator
    """

    def setUp(self):
        self.seed = 23423456
        self.sim = QCGPUProvider().get_backend('qasm_simulator')
        qasm_file = 'tests/example.qasm'
        circ = QuantumCircuit.from_qasm_file(qasm_file)
        self.qobj = compile(circ, backend=self.sim)

    def test_qasm_simulator_single_show(self):
        shots = 1
        self.qobj.config.shots = shots
        result = self.sim.run(self.qobj).result()
        self.assertEqual(result.success, True)

    def test_qasm_simulator(self):
        """Test data counts output for single circuit run against reference."""
        shots = 1024
        self.qobj.config.shots = shots
        result = self.sim.run(self.qobj).result()
        threshold = 0.04 * shots
        counts = result.get_counts()
        target = {'100 100': shots / 8, '011 011': shots / 8,
                  '101 101': shots / 8, '111 111': shots / 8,
                  '000 000': shots / 8, '010 010': shots / 8,
                  '110 110': shots / 8, '001 001': shots / 8}
        self.assertDictAlmostEqual(counts, target, threshold)

    def test_memory(self):
        qr = QuantumRegister(4, 'qr')
        cr0 = ClassicalRegister(2, 'cr0')
        cr1 = ClassicalRegister(2, 'cr1')
        circ = QuantumCircuit(qr, cr0, cr1)
        circ.h(qr[0])
        circ.cx(qr[0], qr[1])
        circ.x(qr[3])
        circ.measure(qr[0], cr0[0])
        circ.measure(qr[1], cr0[1])
        circ.measure(qr[2], cr1[0])
        circ.measure(qr[3], cr1[1])

        shots = 50
        qobj = compile(circ, backend=self.sim, shots=shots, memory=True)
        result = self.sim.run(qobj).result()
        memory = result.get_memory()
        self.assertEqual(len(memory), shots)
        for mem in memory:
            self.assertIn(mem, ['10 00', '10 11'])


if __name__ == '__main__':
    unittest.main()
