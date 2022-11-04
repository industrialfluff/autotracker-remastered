import sys, struct, random, math

class Pattern:
    def __init__(self, rows):
        self.rows = rows
        assert rows >= 4, "too few rows" # note, this is just so modplug doesn't whinge. IT can handle 1-row patterns.
        assert rows <= 200, "too many rows" # on the other hand, IT chunders if you have more than 200 rows.
        self.data = [[[253,0,255,0,0] for j in xrange(64)] for i in xrange(rows)]

        # these are the defaults...
        # - note = 253 (0xFD)
        # - instrument = 0
        # - volume = 255 (0xFF)
        # - effect type = 0
        # - effect parameter = 0

    def write(self, fp):
        self.dopack()
        fp.write(struct.pack("<HH", len(self.packbuf), len(self.data)))
        fp.write("AtBu")
        fp.write(''.join(chr(v) for v in self.packbuf))

    def dopack(self):
        self.packbuf = []
        lc = [[253,0,255,0,0] for j in xrange(64)]
        lm = [0x00 for j in xrange(64)]
        for l in self.data:
            for i in xrange(64):
                c = l[i]
                m = 0x00
                if c[0] != 253:
                    m |= 0x10 if c[0] == lc[i][0] else 0x01
                if c[1] != 0:
                    m |= 0x20 if c[1] == lc[i][1] else 0x02
                if c[2] != 255:
                    m |= 0x40 if c[2] == lc[i][2] else 0x04
                if c[3] != 0 or c[4] != 0:
                    m |= 0x80 if c[3] == lc[i][3] and c[4] == lc[i][4] else 0x08

                v = i+1
                if m != lm[i]:
                    v |= 0x80
                self.packbuf.append(v)

                if v & 0x80:
                    self.packbuf.append(m)
                    lm[i] = m

                if m & 0x01:
                    self.packbuf.append(c[0])
                    lc[i][0] = c[0]
                if m & 0x02:
                    self.packbuf.append(c[1])
                    lc[i][1] = c[1]
                if m & 0x04:
                    self.packbuf.append(c[2])
                    lc[i][2] = c[2]
                if m & 0x08:
                    self.packbuf.append(c[3])
                    self.packbuf.append(c[4])
                    lc[i][3] = c[3]
                    lc[i][4] = c[4]

            self.packbuf.append(0)