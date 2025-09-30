## MEMORY is a list of each bytes that can be accessed individually
class SimpleMemory: 
    # make memorys storage
    def __init__(self): self.memory = [] 

    def access(self, offset, size):
        return self.memory[offset:offset+size]
    def load(self, offse, size):
        return self.access(offset, 32)
