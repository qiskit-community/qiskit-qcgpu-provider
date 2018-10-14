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

import qcgpu

from qiskit.qobj import QobjItem
from qiskit.backends import BaseBackend
from qiskit.result._utils import result_from_old_style_dict

from .job import QCGPUJob
from .simulatorerror import QCGPUSimulatorError

logger = logging.getLogger(__name__)

class QCGPUStatevectorSimulator(BaseBackend):

    DEFAULT_CONFIGURATION = {
        'name': 'statevector_simulator',
        'url': 'https://qcgpu.github.io',
        'simulator': True,
        'local': True,
        'description': 'An OpenCL based statevector simulator',
        'coupling_map': 'all-to-all',
        'basis_gates': 'u,u1,u2,u3,cx,id,h,x,y,z,s,t'
    }

    def __init__(self, configuration=None, provider=None):
        """Initialize the QCGPUStatevectorSimulator object.

        Args:
            configuration (dict): backend configuration
            provider (QCGPUProvider): parent provider
        """

        super().__init__(configuration or self.DEFAULT_CONFIGURATION.copy(), provider=provider)

        self._number_of_qubits = None
        self._statevector = None

    def run(self, qobj):
        """Run qobj asynchronously.

        Args:
            qobj(dict): job description

        Returns: 
            LocalJob: derived from BaseJob
        """

        job_id = str(uuid.uuid4())
        job = QCGPUJob(self, job_id, self._run_job, qobj)
        job.submit()
        return job

    def _run_job(self, job_id, qobj):
        """Run circuits in qobj and return the result

        Args:
            job_id (str): A job id
            qobj (Qobj): Qobj structure
        
        Returns:
            Result: Result is a class including the information to be returned to users.
                Specifically, result_list in the return contains the information such as::

                    [{'data':
                    { 
                        'statevector': array([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j], dtype=complex64)
                    },
                    'status': 'DONE'
                    }]
        """
        self._validate(qobj)
        result_list = []
        start = time.time()
        for circuit in qobj.experiments:
            result_list.append(self.run_circuit(circuit))
        end = time.time()
        result = {
            'backend': self.name,
            'id': qobj.qobj_id,
            'job_id': job_id,
            'result': result_list,
            'status': 'COMPLETED',
            'success': True,
            'time_taken': (end-start)
        }

        return result_from_old_style_dict(result, [circuit.header.name for circuit in qobj.experiments])


    def run_circuit(self, circuit):
        """Run a circuit and return object.

        Args:
            circuit (QobjExperiement): Qobj experiment
        
        Returns:
            dict
        """
        self._number_of_qubits = circuit.header.number_of_qubits
        self._statevector = 0
        
        try:
            sim = qcgpu.State(self._number_of_qubits)
        except OverflowError:
            raise QCGPUSimulatorError('cannot simulate this many qubits')

        
        
        start = time.time()
        for op in circuit.instructions:
            if getattr(op, 'conditional', None):
                raise QCGPUSimulatorError('conditional operations are not supported '
                                        'in statevector simulators')
            elif op.name == 'measure':
                raise QCGPUSimulatorError(
                    'measurements are not supported by statevector simulators')
            elif op.name == 'id':
                logger.info('Identity gates are ignored.')
                pass
            elif op.name == 'barrier':
                # The simulation performs no gate level optimizations
                # thus the barrier statement can be ignored with no
                # difference to the outcome
                logger.info('Barrier gates are ignored.')
                pass
            elif op.name == 'reset':
                raise QCGPUSimulatorError(
                    'reset operation not supported by statevector simulators')
            elif op.name not in ['CX', 'U', 'cx', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z', 's', 't', 'measure']:
                err_msg = 'encountered unrecognized operation "{1}"'
                raise QCGPUSimulatorError(err_msg.format(op.name))
            # At this point the operation is valid, and the applications can happen
            elif op.name in ['u', 'U', 'u3']:
                target = op.qubits[0]
                sim.u(target, op.params[0],
                        op.params[1], op.params[2])
            elif op.name == 'u2':
                target = op.qubits[0]
                sim.u2(target, op.params[0], op.params[1])
            elif op.name == 'u1':
                target = op.qubits[0]
                sim.u1(target, op.params[0])
            elif op.name == 'h':
                target = op.qubits[0]
                sim.h(target)
            elif op.name == 'x':
                target = op.qubits[0]
                sim.x(target)
            elif op.name == 'y':
                target = op.qubits[0]
                sim.y(target)
            elif op.name == 'z':
                target = op.qubits[0]
                sim.z(target)
            elif op.name == 's':
                target = op.qubits[0]
                sim.s(target)
            elif op.name == 't':
                target = op.qubits[0]
                sim.t(target)
            elif op.name in ['CX', 'cx']:
                control = op.qubits[0]
                target = op.qubits[1]
                sim.cx(control, target)
        
        end = time.time()

        data = {'statevector': sim.amplitudes(),
                'time': end-start}
        
        return {'name': circuit.header.name,
                'data': data,
                'status': 'DONE',
                'success': True,
                'shots': circuit.config.shots,
                'time_taken': (end-start)}

    def _validate(self, qobj):
        """Semantic validations of the qobj which cannot be done via schemas.
        Some of these may later move to backend schemas.
        1. No shots
        2. No measurements in the middle
        Args:
            qobj (Qobj): Qobj structure.
        Raises:
            QCGPUSimulatorError: if unsupported operations passed
        """
        self._set_shots_to_1(qobj, False)
        for circuit in qobj.experiments:
            self._set_shots_to_1(circuit, True)
            for operator in circuit.instructions:
                if operator.name in ('measure', 'reset'):
                    raise QCGPUSimulatorError(
                        "In circuit {}: statevector simulator does not support measure or "
                        "reset.".format(circuit.header.name))

    def _set_shots_to_1(self, qobj_item, include_name):
        """Set the number of shots to 1.
        Args:
            qobj_item (QobjItem): QobjItem structure
            include_name (bool): include the name of the item in the log entry
        """
        if not getattr(qobj_item, 'config', None):
            qobj_item.config = QobjItem(shots=1)

        if getattr(qobj_item.config, 'shots', None) != 1:
            warn = 'statevector simulator only supports 1 shot. Setting shots=1'
            if include_name:
                try:
                    warn += 'Setting shots=1 for circuit' + qobj_item.header.name
                except AttributeError:
                    pass
            warn += '.'
            logger.info(warn)
        qobj_item.config.shots = 1