class SimpleMemory:
    def __init__(self): self.memory = []
    # access memory from offset to size
    def access(self, offset, size): 
        return self.memory[offset:offset+size]
    # load 32 bytes from offset and consistently return 32 bytes
    def load (self, offset):
        return self.access(offset, 32)
    # store value at offset, extend memory if needed
    def store(self, offset, value):
        self.memory[offset:offset+len(value)] = value