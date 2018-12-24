"""
Contains an OpenCL based simulator.

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
import numpy as np

from qiskit.providers import BaseBackend
from qiskit.result import Result
from qiskit.providers.models import BackendConfiguration

import qcgpu

from .job import QCGPUJob
from .simulatorerror import QCGPUSimulatorError

logger = logging.getLogger(__name__)


class QCGPUStatevectorSimulator(BaseBackend):
    """Contains an OpenCL based backend"""

    MAX_QUBITS_MEMORY = 30  # Should do something smarter here,
    # but needs to be implemented on the QCGPU side.
    # Will also depend on choosing the optimal backend.

    DEFAULT_CONFIGURATION = {'backend_name': 'statevector_simulator',
                             'backend_version': '1.0.0',
                             'n_qubits': MAX_QUBITS_MEMORY,
                             'url': 'https://qcgpu.github.io',
                             'simulator': True,
                             'local': True,
                             'conditional': False,
                             'open_pulse': False,
                             'memory': True,
                             'max_shots': 65536,
                             'description': 'An OpenCL based statevector simulator',
                             'basis_gates': ['u1',
                                             'u2',
                                             'u3',
                                             'cx',
                                             'id',
                                             'x',
                                             'y',
                                             'z',
                                             'h',
                                             's',
                                             't'],
                             'gates': [{'name': 'u1',
                                        'parameters': ['lambda'],
                                        'qasm_def': 'gate u1(lambda) q { U(0,0,lambda) q; }'},
                                       {'name': 'u2',
                                        'parameters': ['phi',
                                                       'lambda'],
                                        'qasm_def': 'gate u2(phi,lambda) q { U(pi/2,phi,lambda) q; }'},
                                       {'name': 'u3',
                                        'parameters': ['theta',
                                                       'phi',
                                                       'lambda'],
                                        'qasm_def': 'gate u3(theta,phi,lambda) q { U(theta,phi,lambda) q; }'},
                                       {'name': 'cx',
                                        'parameters': ['c',
                                                       't'],
                                        'qasm_def': 'gate cx c,t { CX c,t; }'},
                                       {'name': 'id',
                                        'parameters': ['a'],
                                        'qasm_def': 'gate id a { U(0,0,0) a; }'},
                                       {'name': 'x',
                                        'parameters': ['a'],
                                        'qasm_def': 'gate x a { u3(pi,0,pi) a; }'},
                                       {'name': 'y',
                                        'parameters': ['a'],
                                        'qasm_def': 'gate y a { u3(pi,pi/2,pi/2) a; }'},
                                       {'name': 'z',
                                        'parameters': ['z'],
                                        'qasm_def': 'gate z a { u1(pi) a; }'},
                                       {'name': 'h',
                                        'parameters': ['a'],
                                        'qasm_def': 'gate h a { u2(0,pi) a; }'},
                                       {'name': 's',
                                        'parameters': ['a'],
                                        'qasm_def': 'gate s a { u1(pi/2) a; }'},
                                       {'name': 't',
                                        'parameters': ['a'],
                                        'qasm_def': 'gate t a { u1(pi/4) a; }'},
                                       ]}

    def __init__(self, configuration=None, provider=None):
        configuration = configuration or BackendConfiguration.from_dict(
            self.DEFAULT_CONFIGURATION)
        super().__init__(configuration=configuration, provider=provider)

        self._configuration = configuration
        self._number_of_qubits = None
        self._statevector = None
        self._results = {}
        self._chop_threshold = 15  # chop to 10^-15

    def run(self, qobj):
        """Run qobj asynchronously.

        Args:
            qobj (Qobj): payload of the experiment

        Returns:
            QCGPUJob: derived from BaseJob
        """
        
        qcgpu.backend._create_context()

        job_id = str(uuid.uuid4())
        job = QCGPUJob(self, job_id, self._run_job(job_id, qobj), qobj)
        return job

    #@profile
    def _run_job(self, job_id, qobj):
        """Run experiments in qobj

        Args:
            job_id (str): unique id for the job.
            qobj (Qobj): job description

        Returns:
            Result: Result object
        """
        self._validate(qobj)
        results = []

        start = time.time()
        for experiment in qobj.experiments:
            results.append(self.run_experiment(experiment))
        end = time.time()

        result = {
            'backend_name': self.name(),
            'backend_version': self._configuration.backend_version,
            'qobj_id': qobj.qobj_id,
            'job_id': job_id,
            'results': results,
            'status': 'COMPLETED',
            'success': True,
            'time_taken': (end - start),
            'header': qobj.header.as_dict()
        }

        return Result.from_dict(result) # This can be sped up

    #@profile
    def run_experiment(self, experiment):
        """Run an experiment (circuit) and return a single experiment result.

        Args:
            experiment (QobjExperiment): experiment from qobj experiments list

        Returns:
            dict: A dictionary of results.
            dict: A result dictionary

        Raises:
            QCGPUSimulatorError: If the number of qubits is too large, or another
                error occurs during execution.
        """
        self._number_of_qubits = experiment.header.n_qubits
        self._statevector = 0
        experiment = experiment.as_dict()

        start = time.time()

        try:
            sim = qcgpu.State(self._number_of_qubits)
        except OverflowError:
            raise QCGPUSimulatorError('too many qubits')

        for operation in experiment['instructions']:
            params = operation['params']
            name = operation['name']

            if name == 'id':
                logger.info('Identity gates are ignored.')
            elif name == 'barrier':
                logger.info('Barrier gates are ignored.')
            elif name == 'u3':
                sim.u(operation['qubits'][0], *params)
            elif name == 'u2':
                sim.u2(operation['qubits'][0], *params)
            elif name == 'u1':
                sim.u1(operation['qubits'][0], *params)
            elif name == 'cx':
                sim.cx(*operation['qubits'])
            elif name == 'h':
                sim.h(operation['qubits'][0])
            elif name == 'x':
                sim.x(operation['qubits'][0])
            elif name == 'y':
                sim.y(operation['qubits'][0])
            elif name == 'z':
                sim.z(operation['qubits'][0])
            elif name == 's':
                sim.s(operation['qubits'][0])
            elif name == 't':
                sim.t(operation['qubits'][0])

        end = time.time()

        amps = sim.amplitudes().round(self._chop_threshold)
        amps = np.stack((amps.real, amps.imag), axis=-1)
        return {
            'name': experiment['header']['name'],
            'shots': 1,
            'data': {'statevector': amps},
            'status': 'DONE',
            'success': True,
            'time_taken': (end - start),
            'header': experiment['header']
        }

    #@profile
    def _validate(self, qobj):
        """
        Make sure that there is:
        1. No shots
        2. No measurements until the end
        """
        if qobj.config.shots != 1:
            logger.info('"%s" only supports 1 shot. Setting shots=1.',
                        self.name())
            qobj.config.shots = 1

        for experiment in qobj.experiments:
            name = experiment.header.name

            if getattr(experiment.config, 'shots', 1) != 1:
                logger.info(
                    '"%s" only supports 1 shot. Setting shots=1 for circuit "%s".',
                    self.name(), name)
                experiment.config.shots = 1

            for operation in experiment.instructions:
                if operation.name in ['measure', 'reset']:
                    raise QCGPUSimulatorError(
                        'Unsupported "{}" instruction "{}" in circuit "{}"'.format(
                            self.name(),
                            operation.name,
                            name))

    @staticmethod
    def name():
        return 'statevector_simulator'