namespace SimpleCardGame {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Diagnostics;

    function TranslateGate(gate : String) : (Qubit => Unit is Adj + Ctl) {
        if (gate == "X") {
            return X;
        }
        elif (gate == "H") {
            return H;
        }
        elif (gate == "Y") {
            return Y;
        }
        elif (gate == "Z") {
            return Z;
        }
        else {
            return I;
        }
    }

    operation ApplyGates(QReg : Qubit[], gates : String[]) : Unit {
        if (gates[0] == "C") {
            let g = TranslateGate(gates[1]);
            Controlled g([QReg[0]], QReg[1]);
        }
        elif (gates[1] == "C") {
            let g = TranslateGate(gates[0]);
            Controlled g([QReg[1]], QReg[0]);
        }
        elif (gates[0] == "SWAP") {
            SWAP(QReg[0], QReg[1]);
        }
        else {
            let g1 = TranslateGate(gates[0]);
            g1(QReg[0]);
            let g2 = TranslateGate(gates[1]);
            g2(QReg[1]);
        }
    }

    operation PlayAndMeasure(gates : String[], pastGatesQ1 : String[], pastGatesQ2 : String[]) : Result[] {
        using (QReg = Qubit[2])  { // Allocate 2 qubits.
            
            for (idx in 0 .. Length(pastGatesQ1) - 1) {
                 ApplyGates(QReg, [pastGatesQ1[idx], pastGatesQ2[idx]]);
            }
            ApplyGates(QReg, gates);
            DumpMachine();    // Python driver will collect stdout.
            
            let r1 = M(QReg[0]);     // Measure the qubit value.
            let r2 = M(QReg[1]);     // Measure the qubit value.
            
            Reset(QReg[0]);
            Reset(QReg[1]);
            return [r1, r2];
        }
    }
}

// ['X', 'H', 'Y', 'Z', 'I']