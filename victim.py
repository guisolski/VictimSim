class Victim:
    def __init__(self, pos, sig) -> None:
        self.pos = pos
        self.sig = sig
    def getSig(self):
        return self.sig
    def getState(self):
        return self.sig[7]
    def getPos(self):
        return self.pos