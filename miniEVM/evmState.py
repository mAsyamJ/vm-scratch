class State:
    def __init__(self,
                 sender,
                 program,
                 gas,
                 value,
                 calldata=[]):
        self.pc      = 0
        
        self.stack   = Stack()
        self.memory  = Memory()
        self.storage = Storage()
        
        self.sender   = sender
        self.program  = program
        self.gas      = gas
        self.value    = value
        self.calldata = calldata
        
        self.stop_flag   = False
        self.revert_flag = False
        
        self.returndata = []
        self.logs       = []

# Max EVM capacity
# NOTE: The EVM stack has a maximum capacity of 1024 items. Every item on the stack is at max a 256-bit value (32 bytes).
MAXIMUM_STACK_SIZE = 1024

# Throw an exeption if try to pop a value form stack that is empty
class Stack:
    # nyimpen array stack init di self
    def __init__(self): self.items = [] 

    def __str__ (self):
        ws = [] # write stack
        for i, item in enumerate(self.items[::-1]): # array from behind
            if (i == 0) : # if no stack than write
                ws.append(f"{item} < first")
            elif (i == len(self.items)-1) :
                ws.append(f"{item} < last") # add stack on top
            else :
                ws.append(str(item)) # add stack on mifdle 
        return "\n".join(ws) # from middle then join ws
            
    def push(self, value):
        # check if it's still not overflow than append/add new value
        if len(self.items) == MAXIMUM_STACK_SIZE-1 : 
            raise Exception("Stack overflow")
        self.items.append(value)

    def pop(self, value):
        # check if the data is there or not 
        if len(self.items) == 0:
            raise Exception("Stack underflow")
        return self.items.pop()
    
    @property
    def stack(self):
        return self.items.copy()

    class KeyValue:
    # NOTE : '{}' is value - key, it doesnt matter what is on the order
    def __init__(self): self.storage = {}

    def load (self, key) :
        return self.storage[key]
    def store (self, key, value) :
        self.storage[key] = value
    
    # NOTE: Warm / Cold
    # Warm = the storage is already accessed
    # Cold = teh storage hasn'r been accessed (more expensive)
class Storage(KeyValue):
    def __init__(self):
        super().__init__()
        self.cache = []
        
    def load(self, key):
        warm = True if key in self.cache else False
        if not warm: self.cache.append(key)
        if key not in self.storage: return 0x00
        return warm, super().load(key)

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