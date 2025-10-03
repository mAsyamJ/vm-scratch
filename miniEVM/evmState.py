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

class Opcodes:
    def stop(evm):
    evm.stop_flag = True

    # MATH
    def add(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a+b)
    evm.pc += 1
    evm.gas_dec(3)
        
    def mul(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a*b)
    evm.pc += 1
    evm.gas_dec(5)

    def sub(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a-b)
    evm.pc += 1
    evm.gas_dec(3)

    def div(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(0 if b == 0 else a // b)
    evm.pc += 1
    evm.gas_dec(5)

    pos_or_neg = lambda number: -1 if number < 0 else 1

    def mod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(0 if b == 0 else a % b)
    evm.pc += 1
    evm.gas_dec(5)

    def smod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    sign = -1 if a < 0 else 1  # sign of dividend only
    evm.stack.push(0 if b == 0 else abs(a) % abs(b) * sign)
    evm.pc += 1
    evm.gas_dec(5)

    def addmod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    N = evm.stack.pop()
    evm.stack.push((a + b) % N)
    evm.pc += 1
    evm.gas_dec(8)

    def mulmod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    N = evm.stack.pop()
    evm.stack.push((a * b) % N)
    evm.pc += 1
    evm.gas_dec(8)


    def size_in_bytes(number):
    import math
    if number == 0: return 1
    bits_needed = math.ceil(math.log2(abs(number) + 1))
    return math.ceil(bits_needed / 8)

    def exp(evm):
    a, exponent = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a ** exponent)
    evm.pc += 1
    evm.gas_dec(10 + (50 * size_in_bytes(exponent)))

    def signextend(evm):
    b, x = evm.stack.pop(), evm.stack.pop()
    if b <= 31:
        testbit = b * 8 + 7
        # NOTE: 2^n 
        sign_bit = 1 << testbit
        # x        = 01111111   # decimal 127
        # sign_bit = 10000000   # decimal 128
        if x & sign_bit: result = x | (2**256 - sign_bit)
        else           : result = x & (sign_bit - 1)
    else: result = x
    
    evm.stack.push(result)
    evm.pc += 1
    evm.gas_dec(5)

    # Less than
    def lt(evm):
        a,b = evm.stack.pop(), evm.stackj.pop()
        evm.stack.push(1 if a < b else 0)
        evm.pc += 1
        evm.gas_dec(3)

    # Signed less than
    def slt(evm):
        a, b = evm.stack.pop(), evm.stack.pop()
        a = unsigned_to_signed(a)
        b = unsigned_to_signed(b)
        evm.stack.push(1 if a < b else 0)
        evm.pc += 1
        evm.gas_dec(3)

    # Greater than
    def gt(evm): # greater than
        a, b = evm.stack.pop(), evm.stack.pop()
        evm.stack.push(1 if a > b else 0)
        evm.pc += 1
        evm.gas_dec(3)

    # Equal
    def eq(evm):
        a, b = evm.stack.pop(), evm.stack.pop()
        evm.stack.push(1 if a == b else 0)
        evm.pc += 1
        evm.gas_dec(3)

    # Is Zero
    def iszero(evm):
        a = evm.stack.pop()
        evm.stack.push(1 if a == 0 else 0)
        evm.pc += 1
        evm.gas_dec(3)

    # =========================== Logic =============================
    # And
    def _and(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a & b)
    evm.pc += 1
    evm.gas_dec(3)

    # Or
    def _or(evm): 
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a | b)
    evm.pc += 1
    evm.gas_dec(3)

    # Xor
    def _xor(evm): 
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a ^ b)
    evm.pc += 1
    evm.gas_dec(3)

    # Not
    def _not(evm): 
    a = evm.stack.pop()
    evm.stack.push(~a)
    evm.pc += 1
    evm.gas_dec(3)

    # =========================== Byte =============================
    def byte(evm):
    i, x = evm.stack.pop(), evm.stack.pop()
    if i >= 32: result = 0
    else      : result = (x // pow(256, 31 - i)) % 256
    evm.stack.push(result)
    evm.pc += 1
    evm.gas_dec(3)

    # Bit Shift Left
    def shl(evm): 
    shift, value = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(value << shift)
    evm.pc += 1
    evm.gas_dec(3)

    # Bit shift right
    def shr(evm): 
    shift, value = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(value >> shift)
    evm.pc += 1
    evm.gas_dec(3)

    def sar(evm):
    shift, value = evm.stack.pop(), evm.stack.pop()
    if shift >= 256:
        result = 0 if value >= 0 else UINT_255_NEGATIVE_ONE
    else:
        result = (value >> shift) & UINT_256_MAX
        
    evm.stack.push(result)
    evm.pc += 1
    evm.gas_dec(3)

    def sha3(evm):
    offset, size = evm.stack.pop(), evm.stack.pop()
    value = evm.memory.access(offset, size)
    evm.stack.push(hash(str(value)))

    evm.pc += 1

    # calculate gas
    minimum_word_size = (size + 31) / 32
    dynamic_gas = 6 * minimum_word_size # TODO: + memory_expansion_cost
    evm.gas_dec(30 + dynamic_gas)

    # =========================== Environment =============================
    # Address
    def address(evm):
    evm.stack.push(evm.sender)
    evm.pc += 1
    evm.gas_dec(2)

    # Balance (mock)
    def balance(evm):
    address = evm.stack.pop()
    evm.stack.push(99999999999)

    evm.pc += 1
    evm.gas_dec(2600) # 100 if warm

    # Origin
    def origin(evm):
    evm.stack.push(evm.sender)
    evm.pc += 1
    evm.gas_dec(2)

    # Caller (Mock)
    def caller(evm):
    evm.stack.push("0x414b60745072088d013721b4a28a0559b1A9d213")
    evm.pc += 1
    evm.gas_dec(2)

    # Callvalue
    def callvalue(evm):
    evm.stack.push(evm.value)
    evm.pc += 1
    evm.gas_dec(2)

    #CalldataLoad
    def calldataload(evm):
    i = evm.stack.pop()

    delta = 0
    if i+32 > len(evm.calldata):
        delta = i+32 - len(evm.calldata)

    # always has to be 32 bytes
    # if its not we append 0x00 bytes until it is
    calldata = evm.calldata[i:i+32-delta]
    calldata += 0x00*delta

    evm.stack.push(calldata)
    evm.pc += 1
    evm.gas_dec(3)

    # CallDataSize
    def calldatasize(evm):
    evm.stack.push(len(evm.calldata))
    evm.pc += 1
    evm.gas_dec(2)

    # CallDaatCopy
    def calldatacopy(evm):
    destOffset = evm.stack.pop()
    offset = evm.stack.pop()
    size = evm.stack.pop()

    calldata = evm.calldata[offset:offset+size]
    memory_expansion_cost = evm.memory.store(destOffset, calldata)

    static_gas = 3
    minimum_word_size = (size + 31) // 32
    dynamic_gas = 3 * minimum_word_size + memory_expansion_cost

    evm.gas_dec(static_gas + dynamic_gas)
    evm.pc += 1

    # CodeSize
    def codesize(evm):
    evm.stack.push(len(evm.program))
    evm.pc += 1
    evm.gas_dec(2)

    # CodeCopy
    def codecopy(evm):
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    code = evm.program[offset:offset+size]
    memory_expansion_cost = evm.memory.store(destOffset, code)

    static_gas = 3
    minimum_word_size = (size + 31) / 32
    dynamic_gas = 3 * minimum_word_size + memory_expansion_cost

    evm.gas_dec(static_gas + dynamic_gas)
    evm.pc += 1

    # GasPrice
    def gasprice(evm):
    evm.stack.push(0x00)
    evm.pc += 1
    evm.gas_dec(2)

    # External Code Size
    def extcodesize(evm):
    address = evm.stack.pop()
    evm.stack.push(0x00)
    evm.gas_dec(2600) # 100 if warm
    evm.pc += 1

    # External Code Copy:
    def extcodecopy(evm):
    address    = evm.stack.pop()
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    extcode = [] # no external code
    memory_expansion_cost = evm.memory.store(destOffset, extcode)

    # refactor this in seperate method
    minimum_word_size = (size + 31) / 32
    dynamic_gas = 3 * minimum_word_size + memory_expansion_cost
    address_access_cost = 100 if warm else 2600

    evm.gas_dec(dynamic_gas + address_access_cost)
    evm.pc += 1

    # Retrubn Data Size
    def returndatasize(evm):
    evm.stack.push(0x00) # no return data
    evm.pc += 1
    evm.gas_dec(2)

    # Return Data Copy
    def returndatacopy(evm):
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    returndata            = evm.program[offset:offset+size]
    memory_expansion_cost = evm.memory.store(destOffset, returndata)

    minimum_word_size = (size + 31) / 32
    dynamic_gas = 3 * minimum_word_size + memory_expansion_cost

    evm.gas_dec(3 + dynamic_gas)
    evm.pc += 1

    # External Code Hash
    def extcodehash(evm):
    address = evm.stack.pop()
    evm.stack.push(0x00) # no code

    evm.gas_dec(2600) # 100 if warm
    evm.pc += 1

    # Block Hash
    def blockhash(evm):
    blockNumber = evm.stack.pop()
    if blockNumber > 256: raise Exception("Only last 256 blocks can be accessed")
    evm.stack.push(0x1cbcfa1ffb1ca1ca8397d4f490194db5fc0543089b9dee43f76cf3f962a185e8)
    evm.pc += 1
    evm.gas_dec(20)

    # Get address of the miner for this block
    def coinbase(evm):
    evm.stack.push(0x1cbcfa1ffb1ca1ca8397d4f490194db5fc0543089b9dee43f76cf3f962a185e8)
    evm.pc += 1
    evm.gas_dec(2)

    # Pop
    def _pop(evm):
    evm.pc += 1
    evm.gas_dec(2)
    evm.stack.pop(0)

    # =========================== Memory =============================
    # MLOAD
    def mload(evm): 
    offset = evm.stack.pop()
    value = evm.memory.load(offset)
    evm.stack.push(value)
    evm.pc += 1

    # MSTORE
    def mstore(evm): 
    # TODO: should be right aligned
    offset, value = evm.stack.pop(), evm.stack.pop()
    evm.memory.store(offset, value)
    evm.pc += 1

    def mstore8(evm): 
    offset, value = evm.stack.pop(), evm.stack.pop()
    evm.memory.store(offset, value)
    evm.pc += 1

    # =========================== Storage =============================
    # SLOAD
    def sload(evm): 
    key = evm.stack.pop().value
    warm, value = evm.storage.load(key)
    evm.stack.push(value)

    evm.gas_dec(2100) # 100 if warm
    evm.pc += 1

    # SSTORE
    def sstore(evm): 
    key, value = evm.stack.pop(), evm.stack.pop()
    warm, old_value = evm.storage.store(key, value)

    base_dynamic_gas = 0

    if value != old_value:
        if old_value == 0:
            base_dynamic_gas = 20000
        else:
            base_dynamic_gas = 2900

    access_cost = 100 if warm else 2100
    evm.gas_dec(base_dynamic_gas + access_cost)

    evm.pc += 1

    # TODO: do refunds

    # =========================== Transient Storage =============================
    # Transient Storage Load
    def tload(evm): 
    key = evm.stack.pop().value
    warm, value = evm.storage.load(key)
    evm.stack.push(value)

    evm.gas_dec(100)
    evm.pc += 1

    # Transient Storage Store
    # NOTE: sstore = real blockchain memory (slow but permanent)
    #       tstore = temp notes on scratch paper (fast but wiped at the end)
    def tstore(evm): 
    key, value = evm.stack.pop(), evm.stack.pop()
    evm.storage.store(key, value)
    evm.gas_dec(100)
    evm.pc += 1

    # =========================== JUMP =============================
    def jump(evm):
    counter = evm.stack.pop()

    # make sure that we jump to an JUMPDEST opcode
    if not evm.program[counter] == JUMPDEST:
        raise Exception("Can only jump to JUMPDEST")

    evm.pc = counter
    evm.gas_dec(8)

    def jumpi(evm):
    counter, b = evm.stack.pop(), evm.stack.pop()

    if b != 0: evm.pc = counter
    else     : evm.pc += 1
    
    evm.gas_dec(10)

    def pc(evm):
    evm.stack.push(evm.pc)
    evm.pc += 1
    evm.gas_dec(2)

    def jumpdest(evm):
    evm.pc += 1
    evm.gas_dec(1)

    # Push
    def _push(evm, n):
    evm.pc += 1
    evm.gas_dec(3)
    
    value = []
    for _ in range(n):
        value.append(evm.peek())
        evm.pc += 1
    evm.stack.push(int(''.join(map(str, value))))



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
