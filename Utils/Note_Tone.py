class Note_Tone:
    # Notes Frequency, Octave 0
    C0  = 0
    Cs0 = 0
    D0  = 0
    Ds0 = 0
    E0  = 0
    F0  = 0
    Fs0 = 0
    G0  = 0
    Gs0 = 0
    A0  = 0
    As0 = 0
    B0  = 0

    # Notes Frequency, Octave 1
    C1  = 0
    Cs1 = 0
    D1  = 37
    Ds1 = 39
    E1  = 41
    F1  = 44
    Fs1 = 46
    G1  = 49
    Gs1 = 52
    A1  = 55
    As1 = 58
    B1  = 62

    # Notes Frequency, Octave 2
    C2  = 65
    Cs2 = 69
    D2  = 73
    Ds2 = 78
    E2  = 82
    F2  = 87
    Fs2 = 93
    G2  = 98
    Gs2 = 104
    A2  = 110
    As2 = 117
    B2  = 123

    # Notes Frequency, Octave 3
    C3  = 131
    Cs3 = 139
    D3  = 147
    Ds3 = 156
    E3  = 165
    F3  = 175
    Fs3 = 185
    G3  = 196
    Gs3 = 208
    A3  = 220
    As3 = 233
    B3  = 247

    # Notes Frequency, Octave 4
    C4  = 262
    Cs4 = 277
    D4  = 294
    Ds4 = 311
    E4  = 330
    F4  = 349
    Fs4 = 370
    G4  = 392
    Gs4 = 415
    A4  = 440
    As4 = 466
    B4  = 494

    # Notes Frequency, Octave 5
    C5  = 523
    Cs5 = 554
    D5  = 587
    Ds5 = 622
    E5  = 659
    F5  = 699
    Fs5 = 740
    G5  = 784
    Gs5 = 831
    A5  = 880
    As5 = 932
    B5  = 988

    # Notes Frequency, Octave 6
    C6  = 1047
    Cs6 = 1109
    D6  = 1175
    Ds6 = 1245
    E6  = 1319
    F6  = 1397
    Fs6 = 1480
    G6  = 1568
    Gs6 = 1661
    A6  = 1760
    As6 = 1865
    B6  = 1976

    # Notes Frequency, Octave 7
    C7  = 2093
    Cs7 = 2217
    D7  = 2349
    Ds7 = 2489
    E7  = 2637
    F7  = 2794
    Fs7 = 2960
    G7  = 3136
    Gs7 = 3322
    A7  = 3520
    As7 = 3729
    B7  = 3950

    # Notes Frequency, Octave 8
    C8  = 4186
    Cs8 = 4435
    D8  = 4699
    Ds8 = 4978
    E8  = 5274
    F8  = 5588
    Fs8 = 5920
    G8  = 6272
    Gs8 = 6645
    A8  = 7040
    As8 = 7459
    B8  = 7902
    
    def __init__(self): # Store as dictionary
        self.Octave0 = [self.C0, self.Cs0, self.D0, self.Ds0, self.E0, self.F0, self.Fs0, self.G0, self.Gs0, self.A0, self.As0, self.B0]
        self.Octave1 = [self.C1, self.Cs1, self.D1, self.Ds1, self.E1, self.F1, self.Fs1, self.G1, self.Gs1, self.A1, self.As1, self.B1]
        self.Octave2 = [self.C2, self.Cs2, self.D2, self.Ds2, self.E2, self.F2, self.Fs2, self.G2, self.Gs2, self.A2, self.As2, self.B2]
        self.Octave3 = [self.C3, self.Cs3, self.D3, self.Ds3, self.E3, self.F3, self.Fs3, self.G3, self.Gs3, self.A3, self.As3, self.B3]
        self.Octave4 = [self.C4, self.Cs4, self.D4, self.Ds4, self.E4, self.F4, self.Fs4, self.G4, self.Gs4, self.A4, self.As4, self.B4]
        self.Octave5 = [self.C5, self.Cs5, self.D5, self.Ds5, self.E5, self.F5, self.Fs5, self.G5, self.Gs5, self.A5, self.As5, self.B5]
        self.Octave6 = [self.C6, self.Cs6, self.D6, self.Ds6, self.E6, self.F6, self.Fs6, self.G6, self.Gs6, self.A6, self.As6, self.B6]
        self.Octave7 = [self.C7, self.Cs7, self.D7, self.Ds7, self.E7, self.F7, self.Fs7, self.G7, self.Gs7, self.A7, self.As7, self.B7]
        self.Octave8 = [self.C8, self.Cs8, self.D8, self.Ds8, self.E8, self.F8, self.Fs8, self.G8, self.Gs8, self.A8, self.As8, self.B8]
        
        # self.Octave0 = {'C0' : self.C0,
        #                 'Db0' : self.Cs0,
        #                 'D0' : self.D0,
        #                 'Eb0' : self.Ds0,
        #                 'E0' : self.E0,
        #                 'F0' : self.F0,
        #                 'Gb0' : self.Fs0,
        #                 'G0' : self.G0,
        #                 'Ab0' : self.Gs0,
        #                 'A0' : self.A0,
        #                 'Bb0' : self.As0,
        #                 'B0' : self.B0}
        
        # self.Octave1 = {'C1' : self.C1,
        #                 'Db1' : self.Cs1,
        #                 'D1' : self.D1,
        #                 'Eb1' : self.Ds1,
        #                 'E1' : self.E1,
        #                 'F1' : self.F1,
        #                 'Gb1' : self.Fs1,
        #                 'G1' : self.G1,
        #                 'Ab1' : self.Gs1,
        #                 'A1' : self.A1,
        #                 'Bb1' : self.As1,
        #                 'B1' : self.B1}
        
        # self.Octave2 = {'C2' : self.C2,
        #                 'Db2' : self.Cs2,
        #                 'D2' : self.D2,
        #                 'Eb2' : self.Ds2,
        #                 'E2' : self.E2,
        #                 'F2' : self.F2,
        #                 'Gb2' : self.Fs2,
        #                 'G2' : self.G2,
        #                 'Ab2' : self.Gs2,
        #                 'A2' : self.A2,
        #                 'Bb2' : self.As2,
        #                 'B2' : self.B2}
        
        # self.Octave3 = {'C3' : self.C3,
        #                 'Db3' : self.Cs3,
        #                 'D3' : self.D3,
        #                 'Eb3' : self.Ds3,
        #                 'E3' : self.E3,
        #                 'F3' : self.F3,
        #                 'Gb3' : self.Fs3,
        #                 'G3' : self.G3,
        #                 'Ab3' : self.Gs3,
        #                 'A3' : self.A3,
        #                 'Bb3' : self.As3,
        #                 'B3' : self.B3}
        
        # self.Octave4 = {'C4' : self.C4,
        #                 'Db4' : self.Cs4,
        #                 'D4' : self.D4,
        #                 'Eb4' : self.Ds4,
        #                 'E4' : self.E4,
        #                 'F4' : self.F4,
        #                 'Gb4' : self.Fs4,
        #                 'G4' : self.G4,
        #                 'Ab4' : self.Gs4,
        #                 'A4' : self.A4,
        #                 'Bb4' : self.As4,
        #                 'B4' : self.B4}
        
        # self.Octave5 = {'C5' : self.C5,
        #                 'Db5' : self.Cs5,
        #                 'D5' : self.D5,
        #                 'Eb5' : self.Ds5,
        #                 'E5' : self.E5,
        #                 'F5' : self.F5,
        #                 'Gb5' : self.Fs5,
        #                 'G5' : self.G5,
        #                 'Ab5' : self.Gs5,
        #                 'A5' : self.A5,
        #                 'Bb5' : self.As5,
        #                 'B5' : self.B5}
        
        # self.Octave6 = {'C6' : self.C6,
        #                 'Db6' : self.Cs6,
        #                 'D6' : self.D6,
        #                 'Eb6' : self.Ds6,
        #                 'E6' : self.E6,
        #                 'F6' : self.F6,
        #                 'Gb6' : self.Fs6,
        #                 'G6' : self.G6,
        #                 'Ab6' : self.Gs6,
        #                 'A6' : self.A6,
        #                 'Bb6' : self.As6,
        #                 'B6' : self.B6}
        
        # self.Octave7 = {'C7' : self.C7,
        #                 'Db7' : self.Cs7,
        #                 'D7' : self.D7,
        #                 'Eb7' : self.Ds7,
        #                 'E7' : self.E7,
        #                 'F7' : self.F7,
        #                 'Gb7' : self.Fs7,
        #                 'G7' : self.G7,
        #                 'Ab7' : self.Gs7,
        #                 'A7' : self.A7,
        #                 'Bb7' : self.As7,
        #                 'B7' : self.B7}
        
        # self.Octave8 = {'C8' : self.C8,
        #                 'Db8' : self.Cs8,
        #                 'D8' : self.D8,
        #                 'Eb8' : self.Ds8,
        #                 'E8' : self.E8,
        #                 'F8' : self.F8,
        #                 'Gb8' : self.Fs8,
        #                 'G8' : self.G8,
        #                 'Ab8' : self.Gs8,
        #                 'A8' : self.A8,
        #                 'Bb8' : self.As8,
        #                 'B8' : self.B8}

    def notes(self, octave = 4):
        if octave == 0:
            return self.Octave0
        elif octave == 1:
            return self.Octave1
        elif octave == 2:
            return self.Octave2
        elif octave == 3:
            return self.Octave3
        elif octave == 4:
            return self.Octave4
        elif octave == 5:
            return self.Octave5
        elif octave == 6:
            return self.Octave6
        elif octave == 7:
            return self.Octave7
        elif octave == 8:
            return self.Octave8