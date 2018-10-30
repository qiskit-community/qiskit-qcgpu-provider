"""
Contains an OpenCL based QASM simulator.

How to use this simulator:
see examples/qcgpu_backends.py

Advantages:
1. This backend takes advantage of the speedup that GPUs can give
   to parallel computation.
2. This backend works on every device that has an OpenCL implementation,
   which includes Macbooks, gaming computers, Nvidia and AMD cards etc.
3. Supports u gates.

Limitations:
1. Memory on the GPU is usually a lot less than that of a full machine,
   which can limit the number of qubits simulated. However, you can use
   the program on the CPU.
2. As with all simulators, there is a limit to how accurate your results are.
3. Many OpenCL devices don't support doubles, thus the simulator is limited to
   using floats.
"""

import uuid
import logging
import time
import random
from collections import Counter

from qiskit.qobj import QobjItem
from qiskit.backends import BaseBackend
from qiskit.result._utils import result_from_old_style_dict, copy_qasm_from_qobj_into_result
import qcgpu

from .job import QCGPUJob
from .simulatorerror import QCGPUSimulatorError

logger = logging.getLogger(__name__)

class QCGPUQasmSimulator(BaseBackend):
    """Contains an OpenCL based backend"""

    DEFAULT_CONFIGURATION = {
        'name': 'qasm_simulator',
        'url': 'https://qcgpu.github.io',
        'simulator': True,
        'local': True,
        'description': 'An OpenCL based QASM simulator',
        'coupling_map': 'all-to-all',
        'basis_gates': 'u,u1,u2,u3,cx,id,snapshot'
    }

    def __init__(self, configuration=None, provider=None):
        """Initialize the QCGPUQasmSimulator object.

        Args:
            configuration (dict): backend configuration
            provider (QCGPUProvider): parent provider
        """

        super().__init__(configuration or self.DEFAULT_CONFIGURATION.copy(), provider=provider)

        self._local_random = random.Random()

        # Define attributes in __init__.
        self._classical_state = 0
        self._statevector = 0
        self._snapshots = {}
        self._number_of_cbits = 0
        self._number_of_qubits = 0
        self._shots = 0
        self._qobj_config = None

    def run(self, qobj):
        """Run qobj asynchronously.

        Args: 
            qobj (dict): job description

        Returns: 
            LocalJob: derived from BaseJob
        """

        job_id = str(uuid.uuid4())
        job = QCGPUJob(self, job_id, self._run_job, qobj)
        job.submit()
        return job

    def _run_job(self, job_id, qobj):
        """Run circuits in qobj"""
        self._validate(qobj)
        result_list = []
        self._shots = qobj.config.shots
        self._qobj_config = qobj.config
        start = time.time()

        for circuit in qobj.experiments:
            result_list.append(self.run_circuit(circuit))
        
        end = time.time()
        result = {'backend': self._configuration['name'],
                    'id': qobj.qobj_id,
                    'result': result_list,
                    'status': 'COMPLETED',
                    'success': True,
                    'time_taken': (end - start)}

        copy_qasm_from_qobj_into_result(qobj, result)

        return result_from_old_style_dict(result, [circuit.header.name for circuit in qobj.experiments])

    def run_circuit(self, circuit):
        """Run a circuit and return object.

        Args: circuit (QobjExperiment): Qobj experiment

        Raises:
            QCGPUSimulatorError: If there are any issues with the simulation
        
        Returns:
            dict: The results of running the circuit
        """
        self._number_of_qubits = circuit.header.number_of_qubits
        self._number_of_cbits = circuit.header.number_of_clbits
        self._statevector = 0
        self._classical_state = 0
        self._snapshots = {}
        cl_reg_index = [] # starting bit index of classical register
        cl_reg_nbits = [] # number of bits in classical register
        cbit_index = 0
        for cl_reg in circuit.header.clbit_labels:
            cl_reg_nbits.append(cl_reg[1])
            cl_reg_index.append(cbit_index)
            cbit_index += cl_reg[1]
        
        # Get the seed looking in circuit, qobj, and then random.
        seed = getattr(circuit.config, 'seed', getattr(self._qobj_config, 'seed', random.getrandbits(32)))
        
        # Seed the simulator
        self._local_random.seed(seed)
        outcomes = []

        start = time.time()
        print(circuit)
        for i in range(self._shots):
            print(i/self._shots)
            self._classical_state = 0

            state = qcgpu.State(self._number_of_qubits)
            # state.backend.seed(seed)
            for operation in circuit.instructions:
                if getattr(operation, 'conditional', None):
                    mask = int(operation.conditional.mask, 16)
                    if mask > 0:
                        value = self._classical_state & mask
                        while (mask & 0x1) == 0:
                            mask >>= 1
                            value >>= 1
                        if value != int(operation.conditional.val, 16):
                            continue
                elif operation.name in ('u', 'U', 'u3'):
                    target = operation.qubits[0]
                    state.u(target, operation.params[0],
                            operation.params[1], operation.params[2])
                elif operation.name == 'u2':
                    target = operation.qubits[0]
                    state.u2(target, operation.params[0], operation.params[1])
                elif operation.name == 'u1':
                    target = operation.qubits[0]
                    state.u1(target, operation.params[0])
                elif operation.name in ('id', 'u0', 'barrier'):
                    pass
                elif operation.name in ('CX', 'cx'):
                    qubit0 = operation.qubits[0]
                    qubit1 = operation.qubits[1]
                    state.cx(qubit0, qubit1)
                elif operation.name == 'reset':
                    out = state.measure_collapse(operation.qubits[0])
                    if (out == '1'):
                        state.x(operation.qubits[0])
                elif operation.name == 'measure':
                    qubit = operation.qubits[0]
                    cbit = operation.clbits[0]

                    outcome = state.measure_collapse(qubit)
                    
                    bit = 1 << cbit
                    self._classical_state = (self._classical_state & (~bit)) | (int(outcome) << cbit)
                elif operation.name == 'snapshot':
                    self._snapshots.setdefault(str(int(operation.params[0])),
                                {}).setdefault("statevector",
                                                []).append(state.amplitudes())
                else:
                    backend = self._configuration['name']
                    err_msg = '{0} encountered unrecognized operation "{1}"'
                    raise QCGPUSimulatorError(err_msg.format(backend, operation.name))

            outcomes.append(bin(self._classical_state)[2:].zfill(self._number_of_cbits))
        
        counts = dict(Counter(outcomes))
        data = {
            'counts': self._format_result(counts, cl_reg_index, cl_reg_nbits),
            'snapshots': self._snapshots
        }
        end = time.time()

        return {
            'name': circuit.header.name,
            'seed': seed,
            'shots': self._shots,
            'data': data,
            'status': 'DONE',
            'success': True,
            'time_taken': (end-start)}

    def _validate(self, qobj):
        for experiment in qobj.experiments:
            if 'measure' not in [op.name for op in experiment.instructions]:
                logger.warning("no measurements in circuit '%s', "
                                "classical register will remain all zeros.",
                                experiment.header.name)

    def _format_result(self, counts, cl_reg_index, cl_reg_nbits):
        fcounts = {}
        for key, value in counts.items():
            if cl_reg_nbits:
                new_key = [key[-cl_reg_nbits[0]:]]
                for index, nbits in zip(cl_reg_index[1:],
                                        cl_reg_nbits[1:]):
                    new_key.insert(0, key[-(index+nbits):-index])
                fcounts[' '.join(new_key)] = value
        return fcounts