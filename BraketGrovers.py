#General Imports
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import boto3
import pdb
from math import gcd
from numpy.random import randint
from fractions import Fraction
from math import gcd

#AWS imports
from braket.circuits import Circuit, Gate, Observable, Instruction, circuit_diagram
from braket.devices import LocalSimulator
from braket.aws import AwsDevice

aws_account_id = boto3.client("sts").get_caller_identity()["Account"]
print('Account ', aws_account_id)
#device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")
#device = AwsDevice("arn:aws:braket:::device/qpu/rigetti/Aspen-8")
s3_folder =(f"amazon-braket-85c4d5026af4", "tests")
device = LocalSimulator()
#arn:aws:s3:::amazon-braket-85c4d5026af4

#Creation of custom MCT gate with c control qubits and 1<=p<=c-2 ancillary lines. See Rivest
def diffuser(qb): 
    qc = Circuit()
    
    
    for qubit in range(qb):
        qc.h(qubit)
    
    for qubit in range(qb):
        qc.x(qubit)
    
    qc.h(qb-1)
        
    ############################################
    qc.mcxGrey(qb-1)#qc.mcxGrey(qc, qb-1 )
    #############################################
    
    qc.h(qb-1)
    
    for qubit in range(qb):
        qc.x(qubit)
    
    for qubit in range(qb):
        qc.h(qubit)

    return qc#mct_mat

Circuit.register_subroutine(diffuser)

def initialize(qc, qubits):
    """Apply a H-gate to 'qubits' in qc"""
    for q in qubits:
        qc.h(q)
    return qc

Circuit.register_subroutine(initialize)

def oracle_maker(qb, vals):
    m_size = 2**qb;
    m_oracle = np.array([[0 for x in range(m_size)] for y in range(m_size)])
    for i in range(m_size):
        for j in range(m_size):
            if i == j:
                m_oracle[i][j] = 1
    for i in range(m_size):
        for j in range(m_size):      
            if i == vals:
                m_oracle[i][i] = -1
                
    print(m_oracle)
    #print(type(m_oracle))  
    #m_oracle = np.shape(m_oracle)
    return m_oracle

Circuit.register_subroutine(oracle_maker)



def greyCodeMaker(bitNum):
    res = [0]
    for i in range(bitNum):
        res += [j + 2**i for j in reversed(res)]# reversed(res)
        
    #print([format(j, '0%sb' % bitNum) for j in res])
    return [format(j, '0%sb' % bitNum) for j in res]

def mcxGrey(numControlBits):
    qc = Circuit()
    #controls = qc[list(:numControlBits)]
    #targets = qc[numControlBits]
    grey = greyCodeMaker(numControlBits)
    lastPattern = None
    #print(grey)
    #pdb.set_trace()
    for pattern in grey:
        if '1' not in pattern:
            continue
        if lastPattern is None:
            lastPattern = pattern
        leftmost = list(pattern).index('1')
        #print(leftmost)
        #print(tuple(zip(pattern, lastPattern)))
        comp = [i != j for i,j in zip(pattern, lastPattern)]
        #print(type(comp))
        if True in comp:
            pos = comp.index(True)
        else:
            pos = None
        if pos is not None:
            if pos != leftmost:
                qc.cnot(pos, leftmost)
            else:
                indices = [i for i, x in enumerate(pattern) if x == '1']
                for id in indices[1:]:
                    qc.cnot(id, leftmost)
                    
                    
        if pattern.count('1') % 2 == 0:
            #print("even")
            #print(pattern)
            qc.cnot(numControlBits,leftmost)
            #qc.cnot(leftmost, numControlBits)
           
            
        else:
            #print("odd")
            #print(pattern)
            qc.cnot(leftmost, numControlBits)
            
                    
        lastPattern = pattern
        
    return qc
Circuit.register_subroutine(mcxGrey)

n_qb = 3
qc = Circuit()
initialize(qc, [*range(n_qb)])

qc.unitary(matrix=oracle_maker(n_qb, 5), targets=[*range(n_qb)])
#qc.unitary(matrix=diffuser(n_qb, qc), targets=[*range(n_qb)])
qc.diffuser(n_qb)
print(qc)

result = device.run(qc,shots=1000).result()#add "s3_folder" before shots if running on real
#print('Measurement results:\n',result.measurements)
#print('Counts for collapsed states:\n',result.measurement_counts)
#print('\nProbabilities for collapsed states:\n', result.measurement_probabilities)

plt.bar(result.measurement_counts.keys(), result.measurement_counts.values());
plt.xlabel('bitstrings');
plt.ylabel('counts');
