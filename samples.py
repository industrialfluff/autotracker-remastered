import sys, struct, random, math
import io
import numpy as np
import soundfile as sf
import wave
import os

# IT_CONVERT_* refers to the sample conversion flags.
# this is a VERY internal feature and not widely implemented.
# please ensure you ONLY use IT_CONVERT_SIGNED for normal samples.
# EXCEPTION: IT_CONVERT_DELTA + IT_SAMPLE_IT214 = IT215 compression.
IT_CONVERT_SIGNED = 0x01
IT_CONVERT_BIGEND = 0x02
IT_CONVERT_DELTA = 0x04
IT_CONVERT_BYTEDELT = 0x08
IT_CONVERT_TXWAVE = 0x10
IT_CONVERT_STEREO = 0x20

IT_SAMPLE_EXISTS = 0x01
IT_SAMPLE_16BIT = 0x02
IT_SAMPLE_STEREO = 0x04 # don't use, it's a modplugism.
IT_SAMPLE_IT214 = 0x08 # not supported yet - don't use.
IT_SAMPLE_LOOP = 0x10
IT_SAMPLE_SUS = 0x20 # mikmod doesn't like this, so be wary.
IT_SAMPLE_LOOPBIDI = 0x40
IT_SAMPLE_SUSBIDI = 0x80

# tunables.
SMP_FREQ = 44100
SMP_16BIT = True

IT_BASEFLG_SAMPLE = (
       IT_SAMPLE_EXISTS
    | (IT_SAMPLE_16BIT if SMP_16BIT else 0)
)

class Sample:
    name = "Your sample goes here"
    flags = 0
    boost = 1.0

    fname = "DOSFILE.WAV"
    gvol = 64
    vol = 64
    defpan = 32 # NOTE: set top bit (0x80) to actually use default pan
    convert = IT_CONVERT_SIGNED
    lpbeg = 0
    lpend = 0
    freq = SMP_FREQ
    susbeg = 0
    susend = 0
    vibspeed = 0
    vibdepth = 0
    vibrate = 0
    vibtype = 0

    def __init__(self, name = None, gvol = None, fname = None, *args, **kwargs):
        if name != None:
            self.name = name
        if gvol != None:
            self.gvol = gvol
        
        if fname != None:
            self.fname = fname
            self.name = os.path.basename(fname)
            self.data = self.load_from_file(self.fname)
            self.fname = os.path.basename(fname)
        else:
            self.data = self.generate(*args, **kwargs)
        
        self.length = len(self.data)
        self.amplify()

    def load_from_file(self, fname):
        ifile = wave.open(fname)
        samples = ifile.getnframes()
        audio = ifile.readframes(samples)

        # Convert buffer to float32 using NumPy                                                                                 
        audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
        audio_as_np_float32 = audio_as_np_int16.astype(np.float32)

        # Normalise float32 array so that values are between -1.0 and +1.0                                                      
        max_int16 = 2**15
        audio_normalised = audio_as_np_float32 / max_int16
        return audio_normalised
        
    def write(self, fp):
        fp.write("IMPS")
        fp.write_padded(12, self.fname)
        fp.write(struct.pack("<BBB", self.gvol, self.flags, self.vol))
        fp.write_padded(25, self.name)
        fp.write(struct.pack("<BB", self.convert, self.defpan))
        fp.write(struct.pack("<IIIIII"
            ,self.length, self.lpbeg, self.lpend, self.freq
            ,self.susbeg, self.susend))
        fp.enqueue_ptr(self.write_data)
        fp.write(struct.pack("<BBBB", self.vibspeed, self.vibdepth, self.vibrate, self.vibtype))

    def write_data(self, fp):
        fp.write_sample_array(self.data)

    def amplify(self):
        l = -0.0000000001
        h = 0.0000000001
        for v in self.data:#[len(self.data)//32:]:
            if v < l:
                l = v
            if v > h:
                h = v

        amp = self.boost / max(-l,h)
        ##print amp

        for i in xrange(len(self.data)):
            self.data[i] *= amp

    def generate(self, *args, **kwargs):
        return []

class SampleFromFile(Sample):
    flags = IT_BASEFLG_SAMPLE
    boost = 1.0
    def generate(self, *args, **kwargs):
        return []
        
# YES! We actually have an almost decent sample synth!
class Sample_KS(Sample):
    name = "Karplus-Strong synth"
    flags = IT_BASEFLG_SAMPLE | IT_SAMPLE_LOOP
    boost = 1.0
    def generate(self, freq, decay, filtn, length_sec, nfrqmul = 1.0, filt0 = 1.0, filtf = 1.0, filtdc = 0.01):
        # generate waveform
        delay = int(SMP_FREQ/freq)
        noise = [0 for i in xrange(delay)]

        nfrqctr = 1.0
        nfrqval = 0.0

        intlen = int(SMP_FREQ*length_sec)
        assert intlen >= delay, "KS sample length cannot be less than its period"

        # DC filter
        dq = 0.0

        # prefilter with filt0
        qn = 0.0
        q = 0.0
        dl = -0.001
        dh = 0.001

        nvolcur = 1.0
        nvoldec = 1.0 / (decay * SMP_FREQ)

        nlfsr = random.randint(1,0x7FFF)

        # generate up to "length" samples
        qf = 0.0 #noise[-1]
        l = []
        i = 0
        for j in xrange(intlen):
            #ov = noise[i]
            if nvolcur > 0.0:
                if nfrqctr >= 1.0:
                    #nfrqval = random.random()*2.0-1.0
                    nfrqval = (1.0 if (nlfsr & 1) else -1.0) * 1.0

                    # skip a value to balance it a bit better
                    if nlfsr == 1:
                        nlfsr = 0x4000

                    if nlfsr & 1:
                        nlfsr = (nlfsr>>1) ^ 0x6000
                    else:
                        nlfsr >>= 1
                    nfrqctr -= 1.0
                nfrqctr += nfrqmul
                qn = (nfrqval * nvolcur - qn) * filt0 + qn
                nvolcur -= nvoldec
                noise[i] += qn

            ov = q = noise[i] = (noise[i] - q) * filtn + q
            qf = (ov - qf) * filtf + qf
            dq += (qf - dq) * filtdc
            l.append(qf - dq)
            i = (i+1) % delay

        # set stuff
        self.lpend = intlen
        self.lpbeg = intlen - delay

        # return
        return l

class Sample_Kicker(Sample):
    name = "Kicker"
    flags = IT_BASEFLG_SAMPLE
    boost = 1.8
    def generate(self):
        vol_noise = 0.8
        vol_sine = 1.2
        vol_noise_decay = 1.0 / (SMP_FREQ * 0.01)
        vol_sine_decay = 1.0 / (SMP_FREQ * 0.2)

        q_noise = 0.0

        kickmul = math.pi*2.0*150.0/SMP_FREQ
        offs_sine = 0.0
        offs_sine_speed = kickmul
        offs_sine_decay = 0.9995

        intlen = int(SMP_FREQ*0.25)
        l = []
        for j in xrange(intlen):
            sv = max(-0.7,min(0.7,math.sin(offs_sine)))
            offs_sine += offs_sine_speed
            offs_sine_speed *= offs_sine_decay

            nv = (random.random()*2.0-1.0)
            q_noise += (nv - q_noise) * 0.1
            nv = q_noise

            l.append(nv*vol_noise + sv*vol_sine)
            vol_noise -= vol_noise_decay
            if vol_noise < 0.0:
                vol_noise = 0.0
            vol_sine -= vol_sine_decay
            if vol_sine < 0.0:
                vol_sine = 0.0


        return l

class Sample_NoiseHit(Sample):
    name = "Noise hit generator"
    flags = IT_BASEFLG_SAMPLE
    boost = 1.0
    def generate(self, decay, filtl = 1.0, filth = 0.0):
        vol_noise = 1.0
        vol_noise_decay = 1.0 / (SMP_FREQ * decay)

        ql = 0.0
        qh = 0.0

        intlen = int(SMP_FREQ*decay)
        l = []
        for j in xrange(intlen):
            nv = (random.random()*2.0-1.0)
            ql += (nv - ql) * filtl
            qh += (nv - qh) * filth
            nv = ql - qh

            l.append(nv*vol_noise)
            vol_noise -= vol_noise_decay
            if vol_noise < 0.0:
                vol_noise = 0.0

        return l

class Sample_Hoover(Sample):
    name = "Hoover"
    flags = IT_BASEFLG_SAMPLE | IT_SAMPLE_LOOP
    boost = 1.0

    def generate(self, freq):
        oscfrq = [
            int(freq*(v + v*(random.random()*2.0-1.0)*0.002))/float(SMP_FREQ)
            for v in [0.25, 0.5, 1.0, 2.0]
        ]

        oscvibspeed = [float(random.randint(1,5))*2.0*math.pi/SMP_FREQ for i in xrange(4)]
        oscvibdepth = [0.5,0.4,0.2,0.2]
        oscoffs = [random.random() for i in xrange(4)]
        oscviboffs = [random.random() for i in xrange(4)]
        oscvol = [1.0, 1.0, 1.0, 0.55]

        attack = 0.03
        atkvol = 0.0
        atkspd = 1.0/(attack*SMP_FREQ)

        intlen = int(SMP_FREQ*(attack+1.0))

        l = []
        for i in xrange(intlen):
            v = 0.0
            for j in xrange(4):
                ov = oscoffs[j]*2.0-1.0
                vib = math.sin(oscviboffs[j])*oscvibdepth[j]
                oscoffs[j] += oscfrq[j] * (2.0**(vib/12.0))
                if oscoffs[j] > 1.0:
                    oscoffs[j] %= 1.0
                oscviboffs[j] += oscvibspeed[j]
                v += oscvol[j]*ov

            atkvol += atkspd
            if atkvol > 1.0:
                atkvol = 1.0
            l.append(v*atkvol)

        self.lpend = intlen
        self.lpbeg = int(intlen - SMP_FREQ*1.0 + 0.5)

        return l
    
def karplus_strong(wavetable, n_samples):
    #Synthesizes a new waveform 
    #from an existing wavetable, 
    #modifies last sample by averaging.
    samples = []
    current_sample = 0
    previous_value = 0
    while len(samples) < n_samples:
        wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
        samples.append(wavetable[current_sample])
        previous_value = samples[-1]
        current_sample += 1
        current_sample = current_sample % wavetable.size
    return samples