import sys, struct, random, math
from samples import *

# IT format constants. leave these alone.
IT_FLAG_STEREO = 0x01
IT_FLAG_VOL0MIX = 0x02 # absolutely useless since 1.04.
IT_FLAG_INSTR = 0x04
IT_FLAG_LINEAR = 0x08
IT_FLAG_OLDEFF = 0x10 # don't enable this, it's not well documented.
IT_FLAG_COMPATGXX = 0x20 # don't enable this, it's not well documented.
IT_FLAG_PWHEEL = 0x40 # MIDI-related, don't use
IT_FLAG_USEMIDI = 0x80 # undocumented MIDI crap, don't use
IT_SPECIAL_MESSAGE = 0x01 # MIDI-related, don't use
IT_SPECIAL_UNK1 = 0x02 # undocumented MIDI crap, don't use
IT_SPECIAL_UNK2 = 0x04 # undocumented MIDI crap, don't use
IT_SPECIAL_HASMIDI = 0x08 # undocumented MIDI crap, don't use

class ITFile:
    def __init__(self, tempo, speed):
        self.name = "autotracker-remastered module"
        self.flags = IT_FLAG_STEREO
        self.highlight = 0x1004
        self.ordlist = []
        self.inslist = []
        self.smplist = []
        self.patlist = []
        self.chnpan = [32 for i in xrange(64)]
        self.chnvol = [64 for i in xrange(64)]
        self.version = 0x0217
        self.vercompat = 0x0200
        self.flags = (
              IT_FLAG_STEREO
            | IT_FLAG_VOL0MIX # in the exceptionally rare case it may help...
            | IT_FLAG_LINEAR
        )
        self.special = (
              IT_SPECIAL_MESSAGE
        )
        self.gvol = 128
        self.mvol = 48
        self.tempo = tempo
        self.speed = speed # ticks per row, higher = slower
        self.pitchwheel = 0
        self.pansep = 128
        self.message = (
              "Generated with Autotracker-Remastered"
        )

    def enqueue_ptr(self, call):
        self.ptrq.append((self.fp.tell(),call))
        self.write("00PS")

    def save(self, fname):
        self.fp = open(fname,"wb")

        self.message_fixed = self.message.replace("\n\r","\n").replace("\n","\r") + "\x00\x00"

        self.ptrq = []
        self.doheader(self)

        while self.ptrq:
            pos, f = self.ptrq.pop(0)
            t = self.fp.tell()
            self.fp.seek(pos)
            self.write(struct.pack("<I",t))
            self.fp.seek(t)
            f(self)

        self.fp.close()

    def w_msg(self, fp):
        fp.write(self.message_fixed)

    def doheader(self, fp):
        ordlist = self.ordlist[:]
        if (not ordlist) or ordlist[-1] != 0xFF:
            ordlist.append(0xFF)

        fp.write("IMPM")
        fp.write_padded(25, self.name)
        fp.write(struct.pack("<HHHHHHHHH"
            ,self.highlight
            ,len(ordlist),len(self.inslist),len(self.smplist),len(self.patlist)
            ,self.version,self.vercompat,self.flags,self.special
        ))
        fp.write(struct.pack("<BBBBBBH"
            ,self.gvol,self.mvol,self.speed,self.tempo
            ,self.pansep,self.pitchwheel,len(self.message_fixed)
        ))
        fp.enqueue_ptr(self.w_msg)
        fp.write("AtBu")
        fp.write(''.join(chr(v) for v in self.chnpan))
        fp.write(''.join(chr(v) for v in self.chnvol))

        fp.write(''.join(chr(v) for v in ordlist))

        l = self.inslist + self.smplist + self.patlist
        for i in xrange(len(l)):
            self.enqueue_ptr(l[i].write)

        fp.write(struct.pack("<HI",0,0))

    def write(self, data):
        self.fp.write(data)

    def write_padded(self, length, s, addnull = True):
        if len(s) < length:
            s += "\x00"*(length-len(s))
        else:
            s = s[:length]

        assert len(s) == length, "STUPID! write_padded gave wrong length!"

        self.write(s)

        if addnull:
            self.write("\x00")

    def write_sample_array(self, data):
        # TODO: allow for a compressor / proper saturator
        if SMP_16BIT:
            for v in data:
                d = max(-0x8000,min(0x7FFF,int(v * 0x7FFF)))
                self.write(struct.pack("<h", d))
        else:
            for v in data:
                d = max(-0x80,min(0x7F,int(v * 0x7F)))
                self.write(struct.pack("<b",d))

    def smp_add(self, smp):
        self.smplist.append(smp)
        idx = len(self.smplist)
        return idx

    def pat_add(self, pat):
        idx = len(self.patlist)
        self.patlist.append(pat)
        return idx

    def ord_add(self, order):
        self.ordlist.append(order)
