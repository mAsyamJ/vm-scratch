# NOTE: 
class BaseMemory:
    def store(self, offset, value):
        self.memory[offset:offset+len(value)] = value

class Memory(BaseMemory):
    def __init__(self): self.memory = []
    # access memory from offset to size
    def access(self, offset, size): 
        return self.memory[offset:offset+size]
    # load 32 bytes from offset and consistently return 32 bytes
    def load (self, offset):
        return self.access(offset, 32)

    # Calculate memory cost
    def calc_memory_expansion_gas(self, memory_byte_size):
        memory_size_word = (memory_byte_size + 31) // 32  # integer division
        memory_cost = (memory_size_word ** 2) / 512 + (3 * memory_size_word)
        return round(memory_cost)

    # store value at offset, extend memory if needed
    def store(self, offset, value):
        memory_expansion_cost = 0
        # NOTE: value is a bytes-like object that can be of any length
        # NOTE: this is if expansion is needed and it costs gas and it is 
        #       calculated through last offset devided by new storage 
        #       so we can conclude that this is infinity storage
        if len(self.memory) <= offset + len(value):
            expansion_size = 0
        
            # initialize memory with 32 zeros if empty
            if len(self.memory) == 0:
                expansion_size = 32
                self.memory = [0x00 for _ in range(32)]

            # Extend memory if needed
            #       `             last       `value ` 32
            # NOTE: it is set to '<' to make sure there is always 32 bytes already enough, no need expansion
            if len(self.memory) < offset + len(value):
                expansion_size += offset + len(value) - len(self.memory)
                self.memory.extend([0x00] * expansion_size) # 32 bytes of 0x00

        # --- calculate gas cost based on total memory size after expansion ---
        new_memory_size = len(self.memory)
        memory_expansion_cost = self.calc_memory_expansion_gas(new_memory_size)

        super().store(offset, value)
        return memory_expansion_cost

memory = Memory()

# Store 4 bytes at offset 1
cost1 = memory.store(1, [0x01, 0x02, 0x03, 0x04])
print("Memory at offset 1:", memory.load(1))
print("Memory expansion cost for first store:", cost1)

# Store 4 bytes at offset 22
cost2 = memory.store(22, [0x01, 0x02, 0x03, 0x04])
print("Memory at offset 22:", memory.load(22))
print("Memory at offset 1 after second store:", memory.load(1))
print("Memory expansion cost for second store:", cost2)

# Store 4 bytes at offset 22
cost3 = memory.store(99, [0x01, 0x02, 0x03, 0x04])
print("Memory at offset 100:", memory.load(100))
print("Memory at offset 98:", memory.load(98))
print("Memory at offset 1 after second store:", memory.load(1))
print("Memory expansion cost for second store:", cost3)