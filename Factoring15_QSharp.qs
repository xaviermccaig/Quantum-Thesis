namespace ShorsAzure {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Random;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Measurement;
  
    //Entry point should include qubit assignment. From here,
    //operate on qubits sent to each operation. This is the "union" to Qiskit, so to speak.
    //From here, ensure that each operation accepts the qubit array. You may or may not have to set output
    //to return an array of qubits.
    @EntryPoint()
    operation ShorsFactor() : Unit {
        let N = 15;
        //let a = DrawRandomInt(2, N);                   
        let a = 7;
        mutable topPhase = 0.0;
        mutable r = 0;
        mutable factor_found = false;
        mutable guessOne = 0;
        mutable guessTwo = 0;
        //Message("A: " + IntAsString(a));
        let gcd = GreatestCommonDivisorI(a, N);
        //Message("GCD: "+ IntAsString(gcd));
         using (Qubits = Qubit[7]) { //THE "circuit". All operations below should be done in here.
            set factor_found = false;
            repeat{
                set topPhase = qpe(a, Qubits);
                set r = phaseFrac(topPhase);
                Message("Result: r = " + IntAsString(r) + "\n");

                if (topPhase != IntAsDouble(0)){
                    set guessOne = GreatestCommonDivisorI(a^(r/2)-1, 15);
                    set guessTwo = GreatestCommonDivisorI(a^(r/2)+1, 15);
                    Message("Guessed Factors: " + IntAsString(guessOne) + " and " + IntAsString(guessTwo) + "\n");

                    if (guessOne != 1 and (15 % guessOne) == 0){
                        Message("***** Factor: " + IntAsString(guessOne) + " *****\n");
                        set factor_found = true;
                    }
                    if (guessTwo != 1 and (15 % guessTwo) == 0){
                        Message("***** Factor: " + IntAsString(guessTwo) + " *****\n");
                        set factor_found = true;
                    }
                }
            }until(factor_found == true);
         }
    }

    //Quantum phase estimation
    operation qpe(a: Int, ShorsQubits: Qubit[]): Double {
        let n_count = 3;
        for (i in 0 .. n_count-1){
            H(ShorsQubits[i]);
        }

        X(ShorsQubits[3+n_count]);

        for (i in 0 .. n_count-1){
            c_amod15(a, 2^i, ShorsQubits[3], ShorsQubits[4], ShorsQubits[5], ShorsQubits[6]);
        }

        qft_dagger(n_count, ShorsQubits);
        let meas = MultiM(ShorsQubits);
        let q0 =  meas[0];
        let q1 =  meas[1];
        let q2 =  meas[2];
        let q3 =  meas[3];
        let q4 =  meas[4];
        let q5 =  meas[5];
        let q6 =  meas[6];

        mutable q0m = 0;
        mutable q1m = 0;
        mutable q2m = 0;
        mutable q3m = 0;
        mutable q4m = 0;
        mutable q5m = 0;
        mutable q6m = 0;
        mutable p = 0;

        if (IsResultOne(q0)){
            set q0m = 1;
        }
        if (IsResultOne(q1)){
            set q1m = 1;
        }
        if (IsResultOne(q2)){
            set q2m = 1;
        }
        if (IsResultOne(q3)){
            set q3m = 1;
        }
        if (IsResultOne(q4)){
            set q4m = 1;
        }
        if (IsResultOne(q5)){
            set q5m = 1;
        }
        if (IsResultOne(q6)){
            set q6m = 1;
        }  
        Message("Measure: " + IntAsString(q0m) + IntAsString(q1m) + IntAsString(q2m) + IntAsString(q3m) + IntAsString(q4m) + IntAsString(q5m) + IntAsString(q6m));
        if (q3m == 1 and q4m == 1 and q5m == 0){//110, 6
            set p = 6;
        }
        elif (q3m == 1 and q4m == 0 and q5m == 0){//100, 4
            set p = 4;
        }
        elif (q3m == 0 and q4m == 1 and q5m == 0){//010, 2
            set p = 2;
        }
        elif (q3m == 0 and q4m == 0 and q5m == 0){//000, 0
            set p = 0;
        }

        ResetAll(ShorsQubits);

        mutable phase = 0.0;
        set phase = IntAsDouble(p)/IntAsDouble((2^n_count));
        //Message("P: " + IntAsString(p));
        Message("Phase: " + DoubleAsString(phase));

        return (phase);
    }

    //Implements an n-qubit inverse quantum Fourier transform
    operation qft_dagger(n: Int, nQubits : Qubit[]) : Unit {                         
            for (qubit in 0 .. (n/2 - 1)) {
                SWAP (nQubits[qubit], nQubits[n-qubit-1]);
            }
            for (i in 0 .. n-1) {
                for (j in 0 .. i-1) {
                    Controlled R([nQubits[j]], (PauliZ, -PI()/IntAsDouble(2^(i-j)), nQubits[i])); //where j is control
                }
                H(nQubits[i]);
            }
    }//end of qft_dagger

    //implementing a controlled multiplication by "a mod 15"
    operation c_amod15(a : Int, power : Int, modQZero: Qubit, modQOne: Qubit, modQTwo: Qubit, modQThree: Qubit) : Unit {  
        if (a != 2 and a != 7 and a != 8 and a != 11 and a != 13) {
            Message("ERROR ERROR ERROR : \"a\" MUST BE 2,7,8,11, OR 13\n");
        }
            for (i in 0 .. power-1) {
                if ( a == 2 or a == 13){
                    SWAP (modQZero, modQOne);
                    SWAP (modQOne, modQTwo);
                    SWAP (modQTwo, modQThree);
                }
                if ( a == 7 or a == 8){
                    SWAP (modQTwo, modQThree);
                    SWAP (modQOne, modQTwo);
                    SWAP (modQZero, modQOne);
                }
                if ( a == 11){
                    SWAP (modQOne, modQThree);
                    SWAP (modQZero, modQTwo);
                }
                if ( a == 7 or a == 11 or a == 13){
                    X(modQZero);
                    X(modQOne);
                    X(modQTwo);
                    X(modQThree);
                }
        }
    }// end of c_amod15

    //calculating phase with continued fractions
    operation phaseFrac(phase : Double) : Int {
        let integ = Floor(phase);
        // Message("Integ: " + IntAsString(integ));
        let floatval = phase - IntAsDouble(integ);
        //Message("Floatval: " + DoubleAsString(floatval));
        let bigval = 1000000000;

        let gcdval = GreatestCommonDivisorI(Round(floatval * IntAsDouble(bigval)), bigval);
        //Message("GCDval: " + IntAsString(gcdval));
        let numer = Round(floatval * IntAsDouble(bigval)) / gcdval;
        //Message("Numer: " + IntAsString(numer));
        let denom = bigval / gcdval;
        //Message("Denom: " + IntAsString(denom));
        let frac = Fraction(numer, denom);
        //Message("Frac: " + IntAsString(frac::Numerator) +" / " + IntAsString(frac::Denominator));
        let fracTwo = ContinuedFractionConvergentI(frac, 15);
        //Message("FracTwo: " + IntAsString(fracTwo::Numerator) +" / " + IntAsString(fracTwo::Denominator));
        let denomFinal = AbsI(fracTwo::Denominator);
        //Message("denomFinal: " + IntAsString(denomFinal));
        return(denomFinal);
    }
}//end of namespace ShorsAzure
