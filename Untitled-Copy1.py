#!/usr/bin/env python
# coding: utf-8

# In[1]:


# General Imports
get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
import numpy as np
import boto3
from math import gcd
from numpy.random import randint
from fractions import Fraction

# AWS imports
from braket.circuits import Circuit, Gate, Observable, Instruction, circuit_diagram
from braket.devices import LocalSimulator
from braket.aws import AwsDevice


# In[14]:


############################################################################
# Performs the inverse Quantum Fourier Transform
# Purpose built for N=15 by the Qiskit team, adapted
# for usage in Braket
############################################################################ 
def qft_dagger(n):
    qcQ = Circuit()
    for qubit in range(n//2):
        qcQ.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            # Induces a phase given control=1
            qcQ.cphaseshift(m, j, -np.pi/float(2**(j-m)))
        qcQ.h(j)
    return qcQ

Circuit.register_subroutine(qft_dagger)     # Makes the circuit into a gate

############################################################################
# Performs controlled unitary operation.
# Purpose-built for factoring 15 by the Qiskit team, adapted
# for usage in Braket
############################################################################ 
def c_amod15(a, power, t0, t1, t2, t3):
    #print('A and Power in c_amod is:', a, power)
    if a not in [2,7,8,11,13]:
        # Or else it would share factors with N=15.
        print("ERROR: 'a' must be 2,7,8,11 or 13")
    U = Circuit()        
    for iteration in range(power):
        if a in [2,13]:
            U.swap(t0,t1)
            U.swap(t1,t2)
            U.swap(t2,t3)
        if a in [7,8]:
            U.swap(t2,t3)
            U.swap(t1,t2)
            U.swap(t0,t1)
        if a == 11:
            U.swap(t1,t3)
            U.swap(t0,t2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
                
    return U

Circuit.register_subroutine(c_amod15)          # Makes the circuit into a gate
                
############################################################################
# Performs quantum phase estimation routine for order finding
############################################################################              
def qpe_amod15(a, sim):
    n_count = 8 #was 3
    qc = Circuit() 
    for q in range(n_count):
        qc.h(q)    # Place counting qubits into superposition
    #print('A in QPE is:', a )
    for q in range(n_count):    # Do controlled unitaries in doubling powers of 2   was ncount-1 
        qc.c_amod15(a, 2**q, 8, 9, 10, 11)#was 3456
            
    qc.qft_dagger(n_count)   # Apply inverse quantum fourier transform
    sourceFile = open('demo.txt', 'w')
    print(qc, file=sourceFile)
    sourceFile.close()

    print('Total circuit depth:', qc.depth)
    #print('Total circuit size:', qc.size)
    

    
    if sim is True:
        result = device.run(qc,shots=100).result() 
    elif sim is False:
        #add "s3_folder" before shots if running on nonlocal device
        result = device.run(qc,s3_folder,shots=100).result()
    
    #print('Measurement results:\n',result.measurements)
    print(f'Counts for collapsed states: {result.measurement_counts}\n')
    print(f'Probabilities for collapsed states: {result.measurement_probabilities}\n')
    
    counter_res = result.measurement_counts
    p_val = 0;
    for i in counter_res:
        if counter_res[i] != 0: p_val = counter_res[i]
    phase = p_val/(2**n_count)#phase = int(result[0],2)/(2**n_count)
    print("Corresponding Phase: %f" % phase)
    return phase

############################################################################
# Performs factoring operations until 
# nontrivial factors are found
############################################################################
def factorLoop(a,N, sim):
    factor_found = False
    attempt = 0
    while not factor_found:
        attempt += 1
        print("\nAttempt %i:" % attempt)
        phase = qpe_amod15(a,sim) # Phase = s/r
        # Denominator should (hopefully!) tell us r
        frac = Fraction(phase).limit_denominator(N)    
        r = frac.denominator
        print("Result: r = %i" % r)
        if phase != 0:
            # Guesses for factors are gcd(x^{r/2} ±1 , 15)
            guesses = [gcd(a**(r//2)-1, N), gcd(a**(r//2)+1, N)]
            print("Guessed Factors: %i and %i" % (guesses[0], guesses[1]))
            for guess in guesses:
                # Check to see if guess is a factor
                if guess != 1 and guess != N and (N % guess) == 0: 
                    print("*** Non-trivial factor found: %i ***" % guess)
                    factor_found = True
############################################################################
# Main section
############################################################################
aws_account_id = boto3.client("sts").get_caller_identity()["Account"] 
# Boolean for whether to run the circuit on simulator or hardware
print('Account ', aws_account_id) 
sim = True                                             
if sim is True:
    device = LocalSimulator()
    print("Running on local simulator.\n")
else:
    # Nonlocal Simulator
    device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")     
    # Rigetti Aspen 9       
    #device = AwsDevice("arn:aws:braket:::device/qpu/rigetti/Aspen-9")
    # Use s3_folder with nonlocal systems only
    s3_folder =(f"amazon-braket-73bd8ad2475d", "tests")                               
    print(f'Running on {device}\n')
    #arn:aws:s3:::amazon-braket-85c4d5026af4

N = 15
a = 7    # a = 7 for this example. Will work for other values as well.


phase = qpe_amod15(a,sim)   # Phase = s/r
Fraction(phase).limit_denominator(N) # Denominator should (hopefully!) tell us r
frac = Fraction(phase).limit_denominator(N) 
s, r = frac.numerator, frac.denominator
print(r)
# Taking initial guesses given GCD
guesses = [gcd(a**(r//2)-1, N), gcd(a**(r//2)+1, N)]   
print(guesses)

factorLoop(a,N, sim)   # Run the loop to calculate nontrivial factors.


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




