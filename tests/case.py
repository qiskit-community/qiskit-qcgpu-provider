"""This file contains a test case wrapper using mostly methods from the main qiskit repo"""

import unittest

import math
from numpy import random
from scipy import linalg
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.mapper import two_qubit_kak


def random_SU(n):
    """Return an n x n Haar distributed unitary matrix,
    using QR-decomposition on a random n x n.
    """
    X = (random.randn(n, n) + 1j * random.randn(n, n))
    Q, R = linalg.qr(X)           # Q is a unitary matrix
    Q /= pow(linalg.det(Q), 1 / n)  # make Q a special unitary
    return Q


def build_model_circuits(n, depth):
    """Create a quantum program containing model circuits.
    The model circuits consist of layers of Haar random
    elements of SU(4) applied between corresponding pairs
    of qubits in a random bipartition.
    Args:
        n (int): number of qubits
        depth (int): ideal depth of each model circuit (over SU(4))
        num_circ (int): number of model circuits to construct
    Returns:
        list(QuantumCircuit): list of quantum volume circuits
    """
    # Create quantum/classical registers of size n
    q = QuantumRegister(n)
    c = ClassicalRegister(n)
    # For each sample number, build the model circuits

    # Initialize empty circuit
    circuit = QuantumCircuit(q, c)
    # For each layer
    for j in range(depth):
        # Generate uniformly random permutation Pj of [0...n-1]
        perm = random.permutation(n)
        # For each consecutive pair in Pj, generate Haar random SU(4)
        # Decompose each SU(4) into CNOT + SU(2) and add to Ci
        for k in range(math.floor(n / 2)):
            qubits = [int(perm[2 * k]), int(perm[2 * k + 1])]
            SU = random_SU(4)
            decomposed_SU = two_qubit_kak(SU)
            for gate in decomposed_SU:
                i0 = qubits[gate["args"][0]]
                if gate["name"] == "cx":
                    i1 = qubits[gate["args"][1]]
                    circuit.cx(q[i0], q[i1])
                elif gate["name"] == "u1":
                    circuit.u1(gate["params"][2], q[i0])
                elif gate["name"] == "u2":
                    circuit.u2(gate["params"][1], gate["params"][2], q[i0])
                elif gate["name"] == "u3":
                    circuit.u3(gate["params"][0], gate["params"][1],
                               gate["params"][2], q[i0])
                elif gate["name"] == "id":
                    pass
    # # Barrier before measurement to prevent reordering, then measure
    # circuit.barrier(q)
    # circuit.measure(q, c)
    return circuit

# See the QISKIT Source Code


class MyTestCase(unittest.TestCase):
    def random_circuit(self, n, depth):
        return build_model_circuits(n, depth)

    def assertDictAlmostEqual(self, dict1, dict2, delta=None, msg=None,
                              places=None, default_value=0):
        """
        Assert two dictionaries with numeric values are almost equal.

        Fail if the two dictionaries are unequal as determined by
        comparing that the difference between values with the same key are
        not greater than delta (default 1e-8), or that difference rounded
        to the given number of decimal places is not zero. If a key in one
        dictionary is not in the other the default_value keyword argument
        will be used for the missing value (default 0). If the two objects
        compare equal then they will automatically compare almost equal.

        Args:
            dict1 (dict): a dictionary.
            dict2 (dict): a dictionary.
            delta (number): threshold for comparison (defaults to 1e-8).
            msg (str): return a custom message on failure.
            places (int): number of decimal places for comparison.
            default_value (number): default value for missing keys.

        Raises:
            TypeError: raises TestCase failureException if the test fails.
        """
        if dict1 == dict2:
            # Shortcut
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if places is not None:
            success = True
            standard_msg = ''
            # check value for keys in target
            keys1 = set(dict1.keys())
            for key in keys1:
                val1 = dict1.get(key, default_value)
                val2 = dict2.get(key, default_value)
                if round(abs(val1 - val2), places) != 0:
                    success = False
                    standard_msg += '(%s: %s != %s), ' % (safe_repr(key),
                                                          safe_repr(val1),
                                                          safe_repr(val2))
            # check values for keys in counts, not in target
            keys2 = set(dict2.keys()) - keys1
            for key in keys2:
                val1 = dict1.get(key, default_value)
                val2 = dict2.get(key, default_value)
                if round(abs(val1 - val2), places) != 0:
                    success = False
                    standard_msg += '(%s: %s != %s), ' % (safe_repr(key),
                                                          safe_repr(val1),
                                                          safe_repr(val2))
            if success is True:
                return
            standard_msg = standard_msg[:-2] + ' within %s places' % places

        else:
            if delta is None:
                delta = 1e-8  # default delta value
            success = True
            standard_msg = ''
            # check value for keys in target
            keys1 = set(dict1.keys())
            for key in keys1:
                val1 = dict1.get(key, default_value)
                val2 = dict2.get(key, default_value)
                if abs(val1 - val2) > delta:
                    success = False
                    standard_msg += '(%s: %s != %s), ' % (safe_repr(key),
                                                          safe_repr(val1),
                                                          safe_repr(val2))
            # check values for keys in counts, not in target
            keys2 = set(dict2.keys()) - keys1
            for key in keys2:
                val1 = dict1.get(key, default_value)
                val2 = dict2.get(key, default_value)
                if abs(val1 - val2) > delta:
                    success = False
                    standard_msg += '(%s: %s != %s), ' % (safe_repr(key),
                                                          safe_repr(val1),
                                                          safe_repr(val2))
            if success is True:
                return
            standard_msg = standard_msg[:-2] + ' within %s delta' % delta

        msg = self._formatMessage(msg, standard_msg)
        raise self.failureException(msg)
