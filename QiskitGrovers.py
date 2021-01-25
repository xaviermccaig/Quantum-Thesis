##############
#See:
#https://github.com/Qiskit/qiskit-terra/blob/c4254eff355a6b7f6035253ceb0b847ca8da95a2/qiskit/circuit/library/standard_gates/u3.py#L248
#https://github.com/Qiskit/qiskit-terra/blob/c4254eff355a6b7f6035253ceb0b847ca8da95a2/qiskit/circuit/library/standard_gates/u1.py#L233
#https://github.com/Qiskit/qiskit-terra/blob/master/qiskit/circuit/library/standard_gates/x.py

%matplotlib inline
# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from iqx import *
import numpy as np
from qiskit.tools.monitor import job_monitor
from qiskit.quantum_info.operators import Operator

# Loading your IBM Q account(s)
provider = IBMQ.load_account()

backend = Aer.get_backend('qasm_simulator')
#backend = provider.backends.ibmq_valencia
#backend = provider.backends.ibmq_16_melbourne

def diffuser(qb):
    qc = QuantumCircuit(qb)
    
    for qubit in range(qb):
        qc.h(qubit)
    
    for qubit in range(qb):
        qc.x(qubit)
    
    qc.h(qb-1)
    qc.mct(list(range(qb-1)), qb-1)  # multi-controlled-toffoli
    qc.h(qb-1)
    
    for qubit in range(qb):
        qc.x(qubit)
    
    for qubit in range(qb):
        qc.h(qubit)
        
    Diffuser = qc.to_gate()
    Diffuser.name = "Diffuser"
    return Diffuser

def initialize(qc, qubits):
    """Apply a H-gate to 'qubits' in qc"""
    for q in qubits:
        qc.h(q)
    return qc

def oracle_maker(qb, vals):
    m_size = 2**qb;
    m_oracle = [[0 for x in range(m_size)] for y in range(m_size)]
    for i in range(m_size):
        for j in range(m_size):
            if i == j:
                m_oracle[i][j] = 1
    for i in range(m_size):
        for j in range(m_size):      
            if i == vals:
                m_oracle[i][i] = -1
                
    print(np.matrix(m_oracle))
    oracle = Operator(m_oracle)
    return oracle

n_qb = 3
qc = QuantumCircuit(n_qb)
initialize(qc, [*range(n_qb)])

qc.unitary(oracle_maker(n_qb, 0), [*range(n_qb)], label='oracle')
qc.append(diffuser(n_qb), [*range(n_qb)])
qc.measure_all()
qc.draw(filename='testdraw.png')

trans_circOne = transpile(qc, backend)                    #Returns the transpiled circuit.
trans_circOne.draw(filename='trans.png')                  #Draws the transpiled (larger) circuit.
sizeOne = trans_circOne.size();                              #Returns the size of the transpiled circuit.
depthOne = trans_circOne.depth();  
print("CircuitMOD size: %f" % sizeOne)                       #Prints the transpiled circuit size.
print("CircuitMOD Depth: %f\n\n" % depthOne) 



#results = execute(qc, backend=backend, shots=1024).result()        #Keep if using sim
#answer = results.get_counts()                                      #Keep if using sim
#plot_histogram(answer)                                             #Keep if using sim


job = execute(qc, backend=backend, shots=2048, optimization_level=1) #Keep if using real hardware
job_monitor(job, interval = 2)
results = job.result()                                             #Keep if using real hardware
answer = results.get_counts(qc)                                    #Keep if using real hardware
plot_histogram(answer)                                             #Keep if using real hardware
