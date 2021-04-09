namespace Grovers11011 {
    //General imports
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Random;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Arrays;
  
    //Entry point should include qubit assignment. From here,
    //operate on qubits sent to each operation. 
    //This is the "union" to Qiskit, so to speak.
    //From here, ensure that each operation accepts the qubit array. 
    //You may or may not have to set output
    //to return an array of qubits.
    
    @EntryPoint()
    operation Run(): Unit{
        //mutable final = new Int[][];
        mutable x = [0];
        for i in 0..100{
            //set final w/= i <- GroversMain();
            set x = GroversMain();
            Message($"{x}");
        }  
    }
    operation GroversMain() : Int[] {
        let n_qb = 9; //5 for the qubits, 4 for ancillae
        use qubits = Qubit[n_qb] {
            for i in 0..4{
                //initialize qubits into superposition
                H(qubits[i]);       
            }

            for i in 0..1{
                //Append the oracle
                oracleMaker(n_qb, qubits);
                //Append the diffuser
                diffuser(5, qubits);
            }

            //Reset ancilla qubits to |0> state
            Reset(qubits[5]);
            Reset(qubits[6]);
            Reset(qubits[7]);
            Reset(qubits[8]);

            //Measure
            mutable bitRes = new Int[9];
            for i in 0 .. n_qb-1{
                let res = M(qubits[i]);
                let y = res == Zero ? 0 | 1;
                set bitRes w/= i <- y;
            }
            
            return bitRes;
        }
    }

    //This function acts as the phase shift component of the Grover iteration.
    //A general diffuser, it needs only the number of index and total qubits.
    operation diffuser(n: Int, qubits: Qubit[]): Unit{
        for i in 0 .. n-1{
            H(qubits[i]);
        }

        for i in 0 .. n-1{
            X(qubits[i]);
        }
        
        X(qubits[8]);
        H(qubits[8]);
        Controlled X(qubits[0..n-1], qubits[8]);
        H(qubits[8]);
        X(qubits[8]);

        for i in 0..n-1{
            X(qubits[i]);
        }
        for i in 0..n-1{
            H(qubits[i]);
        }
    }
    //This function creates an oracle for detecting `11011'
    operation oracleMaker(n: Int, qubits: Qubit[]): Unit{
        Controlled X(qubits[0 .. 1], qubits[5]);
        X(qubits[7]);
        Controlled X(qubits[3 .. 4], qubits[6]);
        CNOT(qubits[2], qubits[7]);
        Controlled X(qubits[5 .. 7],qubits[8]);
        Z(qubits[8]);
        Controlled X(qubits[5 .. 7],qubits[8]);
        CNOT(qubits[2], qubits[7]);
        Controlled X(qubits[3 .. 4], qubits[6]);
        X(qubits[7]);
        Controlled X(qubits[0 .. 1], qubits[5]);
    }
}

