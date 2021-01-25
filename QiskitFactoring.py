%matplotlib inline

# Importing standard Qiskit libraries and configuring account
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.jupyter import *
from qiskit.visualization import *
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram, circuit_drawer
from math import gcd
from numpy.random import randint
import pandas as pd
from fractions import Fraction
from math import gcd 
from qiskit.circuit.random import random_circuit

# Loading your IBM Q account(s)
provider = IBMQ.load_account()

#backend = provider.backends.ibmq_16_melbourne
backend = Aer.get_backend('qasm_simulator')
backend._configuration.max_shots= 10 

N = 35
np.random.seed(7) # This is to make sure we get reproduceable results
a = randint(2, N) # Random int between 2 and the designated N to act as a.
print('A: ', a)

gcd(a, N)

def qft_dagger(n):
    """n-qubit QFTdagger the first n qubits in circ"""
    qc = QuantumCircuit(n)
    # Don't forget the Swaps!
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

def c_amod35(a, power):
    #Controlled multiplication by a mod 35
    #if a not in [2,7,8,11,13]:
    #    raise ValueError("'a' must be 2,7,8,11 or 13")
    U = QuantumCircuit(4)        
    for iteration in range(power):
        if a in [2,13]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [7,8]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a == 11:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = "%i^%i mod 35" % (a, power)
    c_U = U.control()
    return c_U

#def c_amod35(a, power):
    
    
#def a2jmodN(a, j, N):
 #   """Compute a^{2^j} (mod N) by repeated squaring"""
  #  for i in range(j):
   #     a = np.mod(a**2, N)
    #return a

def qpe_amod35(a):
    n_count = 3
    qcMOD = QuantumCircuit(6+n_count, n_count) #from 4+n_count to 6+n_count
    for q in range(n_count):
        qcMOD.h(q)     # Initialise counting qubits in state |+>
    qcMOD.x(3+n_count) # And ancilla register in state |1>
    
    for q in range(n_count-1): # Do controlled-U operations        
        qcMOD.append(c_amod35(a, 2**q),                             
                 [q] + [i+n_count for i in range(4)])
        
    trans_circOne = transpile(qcMOD, backend)                    #Returns the transpiled circuit.
    trans_circOne.draw(filename='transTWO.png')                  #Draws the transpiled (larger) circuit.
    sizeOne = trans_circOne.size();                              #Returns the size of the transpiled circuit.
    depthOne = trans_circOne.depth();  
    #print("CircuitMOD size: %f" % sizeOne)                       #Prints the transpiled circuit size.
    #print("CircuitMOD Depth: %f\n\n" % depthOne) 
    
    resultOne = execute(qcMOD, backend, shots=10, memory=True).result()   #Keep if usign SIM
    readingsOne = resultOne.get_memory()                                      #Keep if using SIM
    
    #for i in readingsOne:
    #    print("Register Readings: " + i)
        
        

    #At this point, we need to run the job, grab results, and run the remainder.
    #In terms of the circuit, we are "cutting" between the modular multplications
    #and the QFT dagger.

    #qobj = assemble(transpile(qcMOD, backend=backend), backend=backend) #Keep if using real hardware.
    #job = backend.run(qobj)                                            #Keep if using real hardware.
    #retrieved_job = backend.retrieve_job(job.job_id())                 #Keep if using real hardware.
    #resultOne = retrieved_job.result()                                    #Keep if using real hardware.
    #readingsOne = resultOne.get_counts(qcMOD)                                   #Keep if using real hardware.
    
    #for i in readingsOne:
        #print("Register Readings: " + i)
    
    
    qc = QuantumCircuit(6+n_count, n_count) #changed to 6+n_count instead of 4
    
    qc.append(c_amod35(a, 2**2),                             
                 [2] + [i+n_count for i in range(4)])
    qc.append(qft_dagger(n_count), range(n_count)) # Do inverse-QFT
    qc.measure(range(n_count), range(n_count))
    
    
    #status = backend.status()                              #Checks status of the backend.
    #is_operational = status.operational                    #Checks if the backend is operational.
    #jobs_in_queue = status.pending_jobs                    #Returns the # of jobs in the backend's queue.
    
    trans_circ = transpile(qc, backend)                    #Returns the transpiled circuit.
    trans_circ.draw(filename='transTWO.png')                  #Draws the transpiled (larger) circuit.
    size = trans_circ.size();                              #Returns the size of the transpiled circuit.
    depth = trans_circ.depth();                            #Returns the depth of the transpiled circuit.

    #print("Status: %s" % status)                           #Prints the status.
    #print("Is Operational?: %s" % is_operational)          #Prints the operational status.
    #print("Jobs in Queue: %f\n\n" % jobs_in_queue)         #Prints the # of jobs in queue.
    #print("Circuit size: %f" % size)                       #Prints the transpiled circuit size.
    #print("Circuit Depth: %f\n\n" % depth)                 #Prints the transpiled circuit depth.
    
    circuit_drawer(qc)
    #qobj = assemble(transpile(qc, backend=backend), backend=backend)   #Keep if using real hardware.
   # job = backend.run(qobj)                                            #Keep if using real hardware.
   # retrieved_job = backend.retrieve_job(job.job_id())                 #Keep if using real hardware.
    #result = retrieved_job.result()                                    #Keep if using real hardware.
    #readings = result.get_counts(qc)                                   #Keep if using real hardware.
    
    result = execute(qc, backend, shots=1, memory=True).result()        #Keep if usign SIM
    readings = result.get_memory()                                      #Keep if using SIM

    #print("Register Reading: " + readings[0])
    phase = int(readings[0],2)/(2**n_count)
    #print("Corresponding Phase: %f" % phase)
    return phase

np.random.seed(3) # This is to make sure we get reproduceable results
phase = qpe_amod35(a) # Phase = s/r
Fraction(phase).limit_denominator(N) # Denominator should (hopefully!) tell us r

frac = Fraction(phase).limit_denominator(N)
s, r = frac.numerator, frac.denominator
print('R prior to while(): ', r)

guesses = [gcd(a**(r//2)-1, N), gcd(a**(r//2)+1, N)]
print(guesses)

#a = 7
factor_found = False
attempt = 0
while not factor_found:
    attempt += 1
    print("\nAttempt %i:" % attempt)
    phase = qpe_amod35(a) # Phase = s/r
    frac = Fraction(phase).limit_denominator(N) # Denominator should (hopefully!) tell us r
    r = frac.denominator
    print("Result: r = %i" % r)
    if phase != 0:
        # Guesses for factors are gcd(x^{r/2} ±1 , 15)
        guesses = [gcd(a**(r//2)-1, N), gcd(a**(r//2)+1, N)]
        print("Guessed Factors: %i and %i" % (guesses[0], guesses[1]))
        for guess in guesses:
            if guess != 1 and guess != N and (N % guess) == 0: # Check to see if guess is a factor
                print("*** Non-trivial factor found: %i ***" % guess)
                factor_found = True
