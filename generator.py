import sys, struct, random, math
from key import *
from pattern import *


def pickpair():
    n = random.choice([0,-4,5,-2,0,-2,-4,-5,0,-5,-3,5,0,0,-7,-5,3,0,-4,-2,-4,-2,0,-2,2,0,-3,0,-3,-5,-7,-5])
    s = random.choice([Key_Major, Key_Minor, Key_Major_Pentatonic, Key_Minor_Pentatonic, Key_Harmonic_Minor, Key_Natural_Minor])
    pair = (n, s)
    pair = (0, Key_Harmonic_Minor)
    return pair

class Strategy:
    def __init__(self, *args, **kwargs):
        self.setup(*args,**kwargs)
        self.gens = []
        self.chused = 0

    def setup(self, *args, **kwargs):
        self.key = Key_GenericOctave(60)

    def gen_add(self, gen):
        self.gens.append((self.chused,gen))
        self.chused += gen.size()

    def get_key(self):
        return self.key

class Strategy_Main(Strategy):
    def setup(self, basenote, keytype, patsize, blocksize, *args, **kwargs):
        self.basenote = basenote
        self.keytype = keytype
        self.patsize = patsize
        self.blocksize = blocksize
        self.key = keytype(basenote)
        self.pats = []
        self.rspeed = 2**random.randint(2,3)

        self.rhythm = [3]+[0]*(self.rspeed-1)+[1]+[0]*(self.rspeed-1)
        self.rhythm *= (self.patsize//len(self.rhythm))

        self.pat_idx = 0

        self.newkseq()

    def newkseq(self):
        self.kseq = []
        self.kseq.append(pickpair())
        self.kseq.append(pickpair())
        self.kseq.append(pickpair())
        self.kseq.append(pickpair())
        
        self.kseq2 = []
        self.kseq2.append(pickpair())
        self.kseq2.append(pickpair())
        self.kseq2.append(pickpair())
        self.kseq2.append(pickpair())

    # takes the pattern of notes and passes it to each type of generator
    # (ambient, rhythm, lead, drums, bass)
    # to generate the notes for that channel
    def get_pattern(self, gens_used):
        pat = Pattern(self.patsize)

        # if the index / 8 remainder > 4 use kseq2 else use kseq
        kseq = self.kseq2[:] if self.pat_idx % 8 >= 4 else self.kseq[:]
        #kseq = []
        
        #k = 0
        #for idx, j in enumerate(Key_Major_Pentatonic.MASK):
        #    if (j):
        #        k += idx
        #        kseq.append([k + self.basenote, Key_Major_Pentatonic])
       
        for i in xrange(0,self.patsize,self.blocksize):
            k,kt = kseq.pop(0)
            kchord = kt(self.basenote+k)
            for chn,gen in self.gens:
                if gen in gens_used:
                    gen.apply_notes(chn, pat, self, self.rhythm, i, self.blocksize, self.key, kchord)
            
            kseq.append(k)

        self.pats.append(pat)

        self.pat_idx += 1
        
        return pat

    def get_key(self):
        return self.key

class Generator:
    def __init__(self, *args, **kwargs):
        pass

    def size(self):
        return 1

    def apply_notes(self, chn, pat, strat, rhythm, bbeg, blen, kroot, kchord):
        pass

class Generator_Bass(Generator):
    def __init__(self, smp, *args, **kwargs):
        self.smp = smp

    def size(self):
        return 1

    def apply_notes(self, chn, pat, strat, rhythm, bbeg, blen, kroot, kchord):
        base = kchord.get_base_note()

        leadin = 0

        for row in xrange(bbeg, bbeg+blen, 1):
            if rhythm[row]&1:
                n = base-12 if random.random() < 0.5 else base
                pat.data[row][chn] = [n, self.smp, 255, 0, 0]

                if leadin != 0 and random.random() < 0.4:
                    gran = 2
                    count = 1

                    #if random.random() < 0.2:
                    #   gran = 1

                    if leadin > gran*2 and random.random() < 0.4:
                        count += 1
                        if leadin > gran*3 and random.random() < 0.4:
                            count += 1

                    for j in xrange(count):
                        pat.data[row-(j+1)*gran][chn] = [
                             base+12 if random.random() < 0.5 else base
                            ,self.smp
                            ,0xFF
                            ,ord('S')-ord('A')+1
                            ,0xC0 + random.randint(1,2)
                        ]

                if random.random() < 0.2:
                    pat.data[row][chn][0] += 12
                    if random.random() < 0.4:
                        pat.data[row][chn][3] = ord('S')-ord('A')+1
                        pat.data[row][chn][4] = 0xC0 + random.randint(1,2)
                    else:
                        pat.data[row+2][chn] = [254, self.smp, 255, 0, 0]

                leadin = 0
            else:
                leadin += 1



class Generator_Drums(Generator):
    def __init__(self, s_kick, s_hhc, s_hho, s_snare, *args, **kwargs):
        self.s_kick = s_kick
        self.s_hhc = s_hhc
        self.s_hho = s_hho
        self.s_snare = s_snare
        self.beatrow = 2**random.randint(1,2)

    def size(self):
        return 3

    def apply_notes(self, chn, pat, strat, rhythm, bbeg, blen, kroot, kchord):
        for row in xrange(bbeg,bbeg+blen,self.beatrow):
            vol = 255
            smp = self.s_hhc
            if not (rhythm[row]&2):
                if (row&8):
                    vol = 48
                if (row&4):
                    vol = 32
                if (row&2):
                    vol = 16
                if (row&1):
                    vol = 8

                if random.random() < 0.2:
                    smp = self.s_hho

            pat.data[row][chn] = [60, smp, vol, 0, 0]

        for row in xrange(bbeg,bbeg+blen,2):
            if random.random() < 0.1 and not rhythm[row]&1:
                pat.data[row][chn+1] = [60,self.s_kick,255,0,0]

        did_kick = False
        for row in xrange(bbeg,bbeg+blen,1):
            if rhythm[row]&1:
                if did_kick:
                    pat.data[row][chn+2] = [60,self.s_snare,255,0,0]
                else:
                    if random.random() < 0.1:
                        pat.data[row+2][chn+1] = [60,self.s_kick,255,0,0]
                    else:
                        pat.data[row][chn+1] = [60,self.s_kick,255,0,0]

                did_kick = not did_kick

class Generator_AmbientMelody(Generator):
    MOTIF_PROSPECTS = [
        # 1-steps
        [1],
        [2],
        [3],

        # 2-steps
        [1,3],
        [2,3],
        [2,4],

        # niceties
        [5,7],
        [5,12],
        [7,12],
        [7],
        [5],
        [12],

        # 3-chords
        [3,7],
        [4,7],

        # 4-chords
        [3,7,10],
        [3,7,11],
        [4,7,10],
        [4,7,11],

        # turns and stuff
        [1,0],
        [2,0],
        [1,-1,0],
        [1,-2,0],
        [2,-1,0],
        [2,-2,0],
    ]

    def __init__(self, smp, *args, **kwargs):
        self.smp = smp
        self.beatrow = 2**random.randint(2,3)
        self.lq = 60
        self.ln = -1
        self.mq = []
        self.nq = []

    def size(self):
        return 1

    def apply_notes(self, chn, pat, strat, rhythm, bbeg, blen, kroot, kchord):
        base = kchord.get_base_note()
        if bbeg == 0:
            self.lq = base
            self.ln = -1
            self.mq = []
            self.nq = []

        pat.data[bbeg][chn] = [self.lq, self.smp, 255, 0, 0]
        self.nq.append(bbeg)
        #self.ln = self.lq

        stabbing = False

        row = bbeg
        while row < bbeg+blen:
            if pat.data[row][chn][0] != 253:
                self.nq.append(row)

                row += self.beatrow
                continue

            q = 60

            if self.mq:
                if stabbing or random.random() < 0.9:
                    n = self.mq.pop(0)
                    self.ln = n
                    pat.data[row][chn] = [n, self.smp, 255, 0, 0]
                    self.nq.append(row)

                    if not self.mq:
                        self.lq = n

                    if random.random() < 0.2 or stabbing:
                        row += self.beatrow // 2
                        stabbing = not stabbing
                    else:
                        row += self.beatrow
                else:
                    row += self.beatrow
            elif row-bbeg >= 2*self.beatrow and random.random() < 0.3:
                backstep = random.randint(3,min(10,row//(self.beatrow//2)))*(self.beatrow//2)
                #print "back", row, backstep

                for i in xrange(backstep):
                    if row-bbeg >= blen:
                        break
                    pat.data[row][chn] = pat.data[row-backstep][chn][:]
                    n = pat.data[row][chn][0]
                    if n != 253:
                        self.ln = self.lq = n
                    row += 1
            else:
                if len(self.nq) > 5:
                    self.nq = self.nq[-5:]

                while True:
                    kk = False
                    while True:
                        rbi = random.choice(self.nq)
                        rbn = pat.data[rbi][chn][0]

                        if self.ln != -1 and abs(rbn-self.ln) > 12:
                            continue

                        break

                    m = None
                    #print rbn
                    for j in xrange(20):
                        m = random.choice(self.MOTIF_PROSPECTS)

                        down = random.random() < (8.0+(self.ln-base))/8.0 if self.ln != -1 else 0.5

                        #print m,rbn,down,base
                        if down:
                            m = [rbn-v for v in m]
                        else:
                            m = [rbn+v for v in m]


                        if self.ln == m[0]:
                            continue

                        k = True
                        for v in m:
                            if not (kchord.has_note(v) and kroot.has_note(v)):
                                k = False
                                break

                        if k:
                            kk = True
                            break

                    if kk:
                        break


                if rbn != self.ln:
                    m = [rbn] + m

                #print m
                self.mq += m

                # repeat at same row

