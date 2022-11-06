# autotracker remastered
# based on autotracker-bottomup by Ben "GreaseMonkey" Russell, 2011

import sys, struct, random, math
import numpy as np
import ConfigParser
import json

from samples import *
from key import *
from randoname import *
from itfile import *
from pattern import *
from generator import *

MIDDLE_C = 220.0 * (2.0 ** (3.0 / 12.0))

tempo = random.randint(60,120)
speed = random.randint(2,4)
itf = ITFile(tempo, speed)

# load the sample set from the config.txt file
config_parser = ConfigParser.ConfigParser()
config_parser.read('config.txt')
sections = []
for section_name in config_parser.sections():
    sections.append(section_name)

# randomly select which band to use
chosen_section = random.choice(sections)    

# load the samples into the Impulse Tracker file first           
guitar_choices = json.loads(config_parser.get(chosen_section, "SMP_GUITAR"))
bass_choices = json.loads(config_parser.get(chosen_section, "SMP_BASS"))
piano_choices = json.loads(config_parser.get(chosen_section, "SMP_PIANO"))
hoover_choices = json.loads(config_parser.get(chosen_section, "SMP_HOOVER"))
kick_choices =  json.loads(config_parser.get(chosen_section, "SMP_KICK"))        
hhc_choices =  json.loads(config_parser.get(chosen_section, "SMP_HHC"))        
hho_choices =  json.loads(config_parser.get(chosen_section, "SMP_HHO"))        
snare_choices =  json.loads(config_parser.get(chosen_section, "SMP_SNARE"))        

# each item in the config may now contain several variatins of that sample
# this will randomly select from that list
SMP_GUITAR = itf.smp_add(SampleFromFile(fname=random.choice(guitar_choices)))
SMP_BASS = itf.smp_add(SampleFromFile(fname=random.choice(bass_choices)))
SMP_PIANO = itf.smp_add(SampleFromFile(fname=random.choice(piano_choices)))
SMP_HOOVER = itf.smp_add(SampleFromFile(fname=random.choice(hoover_choices)))
SMP_KICK = itf.smp_add(SampleFromFile(fname=random.choice(kick_choices)))
SMP_HHC = itf.smp_add(SampleFromFile(fname=random.choice(hhc_choices)))
SMP_HHO = itf.smp_add(SampleFromFile(fname=random.choice(hho_choices)))
SMP_SNARE = itf.smp_add(SampleFromFile(fname=random.choice(snare_choices)))

# add all instruments here so all channels can be assigned
drums = Generator_Drums(s_kick = SMP_KICK, s_snare = SMP_SNARE, s_hhc = SMP_HHC, s_hho = SMP_HHO)
piano = Generator_AmbientMelody(smp = SMP_PIANO)
guitar = Generator_AmbientMelody(smp = SMP_GUITAR)
bass = Generator_Bass(smp = SMP_BASS)

# figure out some key parameters for the melodies generated
scale = random.choice([Key_Harmonic_Minor, Key_Minor, Key_Major, Key_Natural_Minor, Key_Major_Pentatonic, Key_Minor_Pentatonic])
strat = Strategy_Main(random.randint(50,50+12-1)+12, scale, 128, 32)
strat.gen_add(drums)
strat.gen_add(piano)
strat.gen_add(guitar)
strat.gen_add(bass)

# generate random patterns using various instruments at once
pat0 = strat.get_pattern([drums])
pat1 = strat.get_pattern([drums, bass, piano])
pat2 = strat.get_pattern([drums, bass, guitar])
pat3 = strat.get_pattern([drums, bass, piano, guitar])
pat4 = strat.get_pattern([drums, bass, piano, guitar])
pat5 = strat.get_pattern([drums, bass])
pat6 = strat.get_pattern([drums, bass, piano, guitar])

# add patterns to the song
itf.pat_add(pat0)
itf.pat_add(pat1)
itf.pat_add(pat2)
itf.pat_add(pat3)
itf.pat_add(pat4)
itf.pat_add(pat5)
itf.pat_add(pat6)

# add order to the patterns
itf.ord_add(0)
itf.ord_add(1)
itf.ord_add(2)
itf.ord_add(2)
itf.ord_add(3)
itf.ord_add(3)
itf.ord_add(4)
itf.ord_add(4)
itf.ord_add(5)
itf.ord_add(5)
itf.ord_add(6)
itf.ord_add(6)

# randomly generate the song name
name = randoname() + "-" + chosen_section
itf.name = name
fname = "%s.it" % name.replace(" ","-").replace("'","")
if len(sys.argv) > 1:
    fname = sys.argv[1]

if os.path.exists('songs/') == False:
    os.mkdir('songs/')
    
itf.save('songs/' + fname)

print "Saved as \"%s\"" % fname
