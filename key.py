#Harmonic C Minor Scale = C, D, Eb, F, G, Ab, B, C
#Natural C Minor Scale = C, D, Eb, F, G, Ab, Bb, C
##########################
#                        #
#   RANDOCHORD FACTORY   #
#                        #
##########################

class Key:
    def __init__(self):
        pass

    def get_base_note(self):
        return 60

    def has_note(self, n):
        return True

class Key_GenericOctave(Key):
    MASK = [True]*12
    def __init__(self, basenote):
        self.basenote = basenote

    def get_base_note(self):
        return self.basenote

    def has_note(self, n):
        return self.MASK[(n-self.basenote)%12]


class Key_Harmonic_Minor(Key_GenericOctave):
    MASK = [
        True,False,True,True,False,True,False,True,True,False,True,True,
    ]
class Key_Natural_Minor(Key_GenericOctave):
    MASK = [
        True,False,True,True,False,True,False,True,True,True,False,True,
    ]
class Key_Major(Key_GenericOctave):
    MASK = [
        True,False,True,False,True,True,False,True,False,True,False,True,
    ]
	
class Key_Minor(Key_GenericOctave):
    MASK = [
        True,False,True,True,False,True,False,True,True,False,True,False,
    ]
	
class Key_Major_Pentatonic(Key_GenericOctave):
    MASK = [
        True,False,True,False,True,False,False,True,False,True,False,False,
    ]

class Key_Minor_Pentatonic(Key_GenericOctave):
    MASK = [
        True,False,False,True,False,True,False,True,False,False,True,False,
    ]
