#!/usr/bin/env python
# coding: utf-8

# In[7]:


#General Imports
get_ipython().magic('matplotlib inline')
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


# In[11]:


#############################################
# The general diffusion operator.
#############################################
def diffuser(qb, controls, targets): 
    qc = Circuit()
    
    for qubit in controls:#from range(len(controls))
        qc.h(qubit)
    
    for qubit in controls:
        qc.x(qubit)
    
    qc.x(qb-1)
    qc.h(qb-1)   
    qc.mcx(qc, controls, targets)
    qc.h(qb-1)
    qc.x(qb-1)
    
    for qubit in controls:
        qc.x(qubit)
    
    for qubit in controls:
        qc.h(qubit)

    return qc#mct_mat

Circuit.register_subroutine(diffuser)

#############################################
# Initializes the gates into superposition.
#############################################
def initialize(qc, qubits):
    for q in qubits:
        qc.h(q)
    return qc

Circuit.register_subroutine(initialize)

#############################################
# Creates the oracles needed
#############################################
def oracle_maker(qb, controls, anc):
    qc = Circuit()
    ###11011
    qc.ccnot(0,1,5)
    qc.x(7)
    qc.ccnot(3,4,6)
    qc.cnot(2,7)
    qc.mcx(qb,[5,6,7],8)
    qc.z(8)
    qc.mcx(qb,[5,6,7],8)
    qc.cnot(2,7)
    qc.ccnot(3,4,6)
    qc.ccnot(0,1,5)
    qc.x(7)
    ###11011
        
    return qc

Circuit.register_subroutine(oracle_maker)

#############################################
# The multi-controlled-x gate implementation
#############################################
def mcx(qb, controls, target):
    n = len(controls) #number of control qubits
    print(f'n is {n}')
    #explicitly define # of qubits for control, target, and ancilla
    qb = Circuit().x(range(4*n)).x(range(4*n)) 
    anc = controls.copy()
    anc=anc[:-1]
    print(f'controls are {controls} and anc is {anc}')
    for i in range(len(anc)):
        anc[i] = anc[i] + 2*n
        
        
    print(f'controls are {controls} and anc is {anc}')
    
    #Toffoli the first two control bits, result in ancillary 0
    qb.ccnot(controls[0],controls[1],anc[0]) 
    x = 0
    for i in controls[2:]: #i.e. for num of control qubits-1
        #print(f'Cascading: {i}')
        #continue with cascaded Toffolis, i.e. creating |c0*c1*...*cn>
        qb.ccnot(i,anc[x],anc[x+1]) 
        x = x+1
    
    print(f'anc is {anc[-1]}')
    #apply cx on target where the last ancilla bit acts as control
    qb.cnot(anc[-1], target) 
    
    y = 0
    #i.e. Toffolis cascading upward after unitary x was applied to target
    for i in controls[:1:-1]: 
        #print(f'Descending: {i}')
        qb.ccnot(i, anc[-2-y], anc[-1-y])
        y = y+1
    #Toffoli the first two control bits, result in ancillary 0
    qb.ccnot(controls[0],controls[1],anc[0]) 
    
    return qb

Circuit.register_subroutine(mcx)

#############################################
# The multi-controlled-x gate implementation
#############################################
aws_account_id = boto3.client("sts").get_caller_identity()["Account"]
print('Account ', aws_account_id)

n_qb = 5
total = 4+n_qb
val = '11011'
sim = True
if sim is True:
    #device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")
    device = LocalSimulator()
    print(f'Running on {device}\n')
else:
    #s3_folder =(f"amazon-braket-85c4d5026af4", "tests")
    #device = AwsDevice("arn:aws:braket:::device/qpu/rigetti/Aspen-9")
    print(f'Running on {device}\n')
    
qc = Circuit()
initialize(qc, [*range(n_qb)]) #Initialize circuit

#Append oracles
qc.oracle_maker(n_qb, [0,1,2,3,4], [5,6,7,8])


#Append diffuser
qc.diffuser(n_qb, [0,1,2,3,4], 8)


#qc.reset([5,6,7,8])
print(qc)

if sim is True:
    result = device.run(qc,shots=1000).result()
if sim is False:
        result = device.run(qc,s3_folder,shots=1000).result()

#Display results
print('Counts for collapsed states:\n',result.measurement_counts)
plt.bar(result.measurement_counts.keys(), result.measurement_counts.values());
plt.xlabel('bitstrings');
plt.ylabel('counts');
 


# In[ ]:




