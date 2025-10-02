MAXIMUM_STACK_SIZE = 1024


class Stack:
    def __init__(self):
        self.items = []

    def __str__(self):
        ws = []
        for i, item in enumerate(self.items[::-1]):
            if i == 0:
                ws.append(f"{item} < first")
            elif i == len(self.items) - 1:
                ws.append(f"{item} < last")
            else:
                ws.append(str(item))
        return "\n".join(ws)

    def push(self, value):
        if len(self.items) >= MAXIMUM_STACK_SIZE:
            raise Exception("Stack overflow")
        self.items.append(value)

    def pop(self):
        if len(self.items) == 0:
            raise Exception("Stack underflow")
        return self.items.pop()

    @property
    def stack(self):
        return self.items.copy()


class KeyValue:
    def __init__(self):
        self.storage = {}

    def load(self, key):
        return self.storage[key]

    def store(self, key, value):
        self.storage[key] = value


class Storage(KeyValue):
    def __init__(self):
        super().__init__()
        self.cache = []

    def load(self, key):
        warm = key in self.cache
        if not warm:
            self.cache.append(key)
        if key not in self.storage:
            return warm, 0x00
        return warm, super().load(key)


class BaseMemory:
    def store(self, offset, value):
        self.memory[offset:offset+len(value)] = value


class Memory(BaseMemory):
    def __init__(self):
        self.memory = bytearray()

    def access(self, offset, size):
        return self.memory[offset:offset+size]

    def load(self, offset):
        return self.access(offset, 32)

    def calc_memory_expansion_gas(self, memory_byte_size):
        memory_size_word = (memory_byte_size + 31) // 32
        memory_cost = (memory_size_word ** 2) / 512 + (3 * memory_size_word)
        return round(memory_cost)

    def store(self, offset, value: bytes):
        if len(self.memory) < offset + len(value):
            expansion_size = offset + len(value) - len(self.memory)
            self.memory.extend(b"\x00" * expansion_size)

        new_memory_size = len(self.memory)
        memory_expansion_cost = self.calc_memory_expansion_gas(new_memory_size)

        super().store(offset, value)
        return memory_expansion_cost


class State:
    def __init__(self, sender, program, gas, value, calldata=[]):
        self.pc = 0

        self.stack = Stack()
        self.memory = Memory()
        self.storage = Storage()

        self.sender = sender
        self.program = program
        self.gas = gas
        self.value = value
        self.calldata = calldata

        self.stop_flag = False
        self.revert_flag = False

        self.returndata = []
        self.logs = []


s = State("alice", "program", 100000, 0)

# Stack
s.stack.push(10)
s.stack.push(20)
print(s.stack.pop())  # 20

# Storage warm/cold
s.storage.store(1, 99)
print(s.storage.load(1))  # (False, 99)
print(s.storage.load(1))  # (True, 99)

# Memory
gas = s.memory.store(0, b"hello")
print(s.memory.load(0))   # b'hello' padded to 32?
print("Gas cost:", gas)
