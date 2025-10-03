class EVM:
    def __init__(self,
                 program,
                 gas,
                 value,
                 calldata=[]):
        self.pc      = 0
        self.stack   = Stack()
        self.memory  = Memory()
        self.storage = Storage()
        
        self.program  = program
        self.gas      = gas
        self.value    = value
        self.calldata = calldata
        
        self.stop_flag   = False
        self.revert_flag = False
        
        self.returndata = []
        self.logs       = []
        
    def peek(self): return self.program[self.pc]
    
    def gas_dec(self, amount):
        if self.gas - amount < 0: 
            raise Exception("out of gas")
        self.gas -= amount

    
    def should_execute_next_opcode(self):
        if self.pc > len(self.program)-1: return False
        if self.stop_flag               : return False
        if self.revert_flag             : return False
        
        return True
    
    def run(self):
        while self.should_execute_next_opcode():
            op = self.program[self.pc]
            
            # Stop & Control Flow
            if op == STOP: stop(self)
            
            # Math Operations
            elif op == ADD:        add(self)
            elif op == MUL:        mul(self)
            elif op == SUB:        sub(self)
            elif op == DIV:        div(self)
            elif op == SDIV:       sdiv(self)
            elif op == MOD:        mod(self)
            elif op == SMOD:       smod(self)
            elif op == ADDMOD:     addmod(self)
            elif op == MULMOD:     mulmod(self)
            elif op == EXP:        exp(self)
            elif op == SIGNEXTEND: signextend(self)
            
            # Comparison Operations
            elif op == LT:     lt(self)
            elif op == GT:     gt(self)
            elif op == SLT:    slt(self)
            elif op == SGT:    sgt(self)
            elif op == EQ:     eq(self)
            elif op == ISZERO: iszero(self)
            
            # Logic Operations
            elif op == AND: _and(self)
            elif op == OR:  _or(self)
            elif op == XOR: _xor(self)
            elif op == NOT: _not(self)
            
            # Bit Operations
            elif op == BYTE: byte(self)
            elif op == SHL:  shl(self)
            elif op == SHR:  shr(self)
            elif op == SAR:  sar(self)
            
            # SHA3
            elif op == SHA3: sha3(self)
            
            # Environment Information
            elif op == ADDRESS:        address(self)
            elif op == BALANCE:        balance(self)
            elif op == ORIGIN:         origin(self)
            elif op == CALLER:         caller(self)
            elif op == CALLVALUE:      callvalue(self)
            elif op == CALLDATALOAD:   calldataload(self)
            elif op == CALLDATASIZE:   calldatasize(self)
            elif op == CALLDATACOPY:   calldatacopy(self)
            elif op == CODESIZE:       codesize(self)
            elif op == CODECOPY:       codecopy(self)
            elif op == GASPRICE:       gasprice(self)
            elif op == EXTCODESIZE:    extcodesize(self)
            elif op == EXTCODECOPY:    extcodecopy(self)
            elif op == RETURNDATASIZE: returndatasize(self)
            elif op == RETURNDATACOPY: returndatacopy(self)
            elif op == EXTCODEHASH:    extcodehash(self)
            elif op == BLOCKHASH:      blockhash(self)
            elif op == COINBASE:       coinbase(self)
            elif op == TIMESTAMP:      timestamp(self)
            elif op == NUMBER:         number(self)
            elif op == DIFFICULTY:     difficulty(self)
            elif op == GASLIMIT:       gaslimit(self)
            elif op == CHAINID:        chainid(self)
            elif op == SELFBALANCE:    selfbalance(self)
            elif op == BASEFEE:        basefee(self)
            
            # Stack Operations
            elif op == POP: _pop(self)
            
            # Memory Operations
            elif op == MLOAD:   mload(self)
            elif op == MSTORE:  mstore(self)
            elif op == MSTORE8: mstore8(self)
            
            # Storage Operations
            elif op == SLOAD:  sload(self)
            elif op == SSTORE: sstore(self)
            
            # Jump Operations
            elif op == JUMP:     jump(self)
            elif op == JUMPI:    jumpi(self)
            elif op == PC:       pc(self)
            elif op == JUMPDEST: jumpdest(self)
            
            # Transient Storage Operations
            elif op == TLOAD:  tload(self)
            elif op == TSTORE: tstore(self)
            
            # Push Operations (0x60-0x7F)
            elif op == PUSH1:  _push(self, 1)
            elif op == PUSH2:  _push(self, 2)
            elif op == PUSH3:  _push(self, 3)
            elif op == PUSH4:  _push(self, 4)
            elif op == PUSH5:  _push(self, 5)
            elif op == PUSH6:  _push(self, 6)
            elif op == PUSH7:  _push(self, 7)
            elif op == PUSH8:  _push(self, 8)
            elif op == PUSH9:  _push(self, 9)
            elif op == PUSH10: _push(self, 10)
            elif op == PUSH11: _push(self, 11)
            elif op == PUSH12: _push(self, 12)
            elif op == PUSH13: _push(self, 13)
            elif op == PUSH14: _push(self, 14)
            elif op == PUSH15: _push(self, 15)
            elif op == PUSH16: _push(self, 16)
            elif op == PUSH17: _push(self, 17)
            elif op == PUSH18: _push(self, 18)
            elif op == PUSH19: _push(self, 19)
            elif op == PUSH20: _push(self, 20)
            elif op == PUSH21: _push(self, 21)
            elif op == PUSH22: _push(self, 22)
            elif op == PUSH23: _push(self, 23)
            elif op == PUSH24: _push(self, 24)
            elif op == PUSH25: _push(self, 25)
            elif op == PUSH26: _push(self, 26)
            elif op == PUSH27: _push(self, 27)
            elif op == PUSH28: _push(self, 28)
            elif op == PUSH29: _push(self, 29)
            elif op == PUSH30: _push(self, 30)
            elif op == PUSH31: _push(self, 31)
            elif op == PUSH32: _push(self, 32)
            
            # Dup Operations (0x80-0x8F)
            elif op == DUP1:  _dup(self, 1)
            elif op == DUP2:  _dup(self, 2)
            elif op == DUP3:  _dup(self, 3)
            elif op == DUP4:  _dup(self, 4)
            elif op == DUP5:  _dup(self, 5)
            elif op == DUP6:  _dup(self, 6)
            elif op == DUP7:  _dup(self, 7)
            elif op == DUP8:  _dup(self, 8)
            elif op == DUP9:  _dup(self, 9)
            elif op == DUP10: _dup(self, 10)
            elif op == DUP11: _dup(self, 11)
            elif op == DUP12: _dup(self, 12)
            elif op == DUP13: _dup(self, 13)
            elif op == DUP14: _dup(self, 14)
            elif op == DUP15: _dup(self, 15)
            elif op == DUP16: _dup(self, 16)
            
            # Swap Operations (0x90-0x9F)
            elif op == SWAP1:  _swap(self, 1)
            elif op == SWAP2:  _swap(self, 2)
            elif op == SWAP3:  _swap(self, 3)
            elif op == SWAP4:  _swap(self, 4)
            elif op == SWAP5:  _swap(self, 5)
            elif op == SWAP6:  _swap(self, 6)
            elif op == SWAP7:  _swap(self, 7)
            elif op == SWAP8:  _swap(self, 8)
            elif op == SWAP9:  _swap(self, 9)
            elif op == SWAP10: _swap(self, 10)
            elif op == SWAP11: _swap(self, 11)
            elif op == SWAP12: _swap(self, 12)
            elif op == SWAP13: _swap(self, 13)
            elif op == SWAP14: _swap(self, 14)
            elif op == SWAP15: _swap(self, 15)
            elif op == SWAP16: _swap(self, 16)
            
            # Log Operations
            elif op == LOG0: log0(self)
            elif op == LOG1: log1(self)
            elif op == LOG2: log2(self)
            elif op == LOG3: log3(self)
            elif op == LOG4: log4(self)
            
            # Contract Operations
            elif op == CREATE:       create(self)
            elif op == CALL:         call(self)
            elif op == CALLCODE:     callcode(self)
            elif op == RETURN:       _return(self)
            elif op == DELEGATECALL: delegatecall(self)
            elif op == CREATE2:      create2(self)
            elif op == STATICCALL:   staticcall(self)
            elif op == REVERT:       revert(self)
            elif op == INVALID:      invalid(self)
            elif op == SELFDESTRUCT: selfdestruct(self)
            
            else:
                raise Exception(f"Unknown opcode: {hex(op)}")
        
    def reset(self):
        self.pc      = 0
        self.stack   = Stack()
        self.memory  = Memory()
        self.storage = Storage()