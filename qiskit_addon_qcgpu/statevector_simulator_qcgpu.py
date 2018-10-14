"""Backend for the QCGPU OpenCL based simulator."""

import uuid
import time

import qcgpu

from qiskit.backends import BaseBackend
from qiskit.backends.aer import AerJob
from qiskit.backends.aer._simulatorerror import SimulatorError
from qiskit.qobj import qobj_to_dict
from qiskit.result._utils import result_from_old_style_dict

RUN_MESSAGE = """An OpenCL based simulator.
Developer: Adam Kelly.
For more information see https://qcgpu.github.io"""


def run_qobj_circuit(qobj):
    ccircuit = qobj['compiled_circuit']
    num_qubits = ccircuit['header']['number_of_qubits']

    sim = qcgpu.State(num_qubits)

    for op in ccircuit['operations']:
        if 'conditional' in op:
            raise SimulatorError('conditional operations are not supported '
                                    'in statevector simulators')
        elif op['name'] == 'measure':
            raise SimulatorError(
                'measurements are not supported by statevector simulators')
        elif op['name'] == 'id':
            # logger.info('Identity gates are ignored.')
            pass
        elif op['name'] == 'barrier':
            # The simulation performs no gate level optimizations
            # thus the barrier statement can be ignored with no
            # difference to the outcome
            # logger.info('Barrier gates are ignored.')
            pass
        elif op['name'] == 'reset':
            raise SimulatorError(
                'reset operation not supported by statevector simulators')
        elif op['name'] not in ['CX', 'U', 'cx', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z', 's', 't', 'measure']:
            err_msg = 'encountered unrecognized operation "{1}"'
            raise SimulatorError(err_msg.format(op['name']))
        # At this point the operation is valid, and the applications can happen
        elif op['name'] in ['u', 'U', 'u3']:
            target = op['qubits'][0]
            sim.u(target, op['params'][0],
                    op['params'][1], op['params'][2])
        elif op['name'] == 'u2':
            target = op['qubits'][0]
            sim.u2(target, op['params'][0], op['params'][1])
        elif op['name'] == 'u1':
            target = op['qubits'][0]
            sim.u1(target, op['params'][0])
        elif op['name'] == 'h':
            target = op['qubits'][0]
            sim.h(target)
        elif op['name'] == 'x':
            target = op['qubits'][0]
            sim.x(target)
        elif op['name'] == 'y':
            target = op['qubits'][0]
            sim.y(target)
        elif op['name'] == 'z':
            target = op['qubits'][0]
            sim.z(target)
        elif op['name'] == 's':
            target = op['qubits'][0]
            sim.s(target)
        elif op['name'] == 't':
            target = op['qubits'][0]
            sim.t(target)
        elif op['name'] in ['CX', 'cx']:
            control = op['qubits'][0]
            target = op['qubits'][1]
            sim.cx(control, target)

    return {
        'data': {
            'statevector': sim.amplitudes()
        }, 
        'status': 'DONE', 
        'success': True, 
        'shots': 1 
    }



class StatevectorSimulatorQCGPU(BaseBackend):
    """Qiskit backend interface to QCGPU"""

    DEFAULT_CONFIGURATION = {
        'name': 'statevector_simulator_qcgpu',
        'url': 'https://qcgpu.github.io',
        'simulator': True,
        'local': True,
        'description': 'OpenCL based statevector simulator',
        'coupling_map': 'all-to-all',
        'basis_gates': 'u,u1,u2,u3,cx,id,h,x,y,z,s,t'
        # 'basis_gates': 'u,cx,id'
    }

    def __init__(self, config=None):
        """
        Args:
            configuration (dict): backend configuration
        """

        super().__init__(config or self.DEFAULT_CONFIGURATION.copy())

    def run(self, qobj):
        job_id = str(uuid.uuid4())
        local_job = AerJob(self, job_id, self._run_job, qobj)
        local_job.submit()
        return local_job
    
    def _run_job(self, job_id, qobj):
        """Run circuits in q_job"""
        result_list = []

        job_dict = qobj_to_dict(qobj, version="0.0.1")

        # # print(job_dict['config']['n_qubits'])
        # state = qcgpu.State(job_dict['config']['n_qubits'])

        start = time.time()

        for circuit in job_dict['circuits']:
            result_list.append(run_qobj_circuit(circuit))

        end = time.time()

        result = {
            'backend': self.DEFAULT_CONFIGURATION['name'],
            'id': job_dict['id'],
            'result': result_list,
            'status': 'COMPLETED',
            'success': True,
            'time_taken': (end - start)
        }

        return result_from_old_style_dict(result, [circuit.header.name for circuit in qobj.experiments])

# def _get_register_specs(bit_labels):
#     """
#     Get the number and size of unique registers from bit_labels list with an
#     iterator of register_name:size pairs.
#     Args:
#         bit_labels (list): this list is of the form::
#             [['reg1', 0], ['reg1', 1], ['reg2', 0]]
#             which indicates a register named "reg1" of size 2
#             and a register named "reg2" of size 1. This is the
#             format of classic and quantum bit labels in qobj
#             header.
#     Yields:
#         tuple: pairs of (register_name, size)
#     """
#     iterator = itertools.groupby(bit_labels, operator.itemgetter(0))
#     for register_name, sub_it in iterator:
#         yield register_name, max(ind[1] for ind in sub_it) + 1


# def _format_result(counts, cl_reg_index, cl_reg_nbits):
#     """Format the result bit string.
#     This formats the result bit strings such that spaces are inserted
#     at register divisions.
#     Args:
#         counts (dict): dictionary of counts e.g. {'1111': 1000, '0000':5}
#         cl_reg_index (list): starting bit index of classical register
#         cl_reg_nbits (list): total amount of bits in classical register
#     Returns:
#         dict: spaces inserted into dictionary keys at register boundaries.
#     """
#     fcounts = {}
#     for key, value in counts.items():
#         new_key = [key[-cl_reg_nbits[0]:]]
#         for index, nbits in zip(cl_reg_index[1:],
#                                 cl_reg_nbits[1:]):
#             new_key.insert(0, key[-(index+nbits):-index])
#         fcounts[' '.join(new_key)] = value
#     return fcounts