"""
    @notice
        Storage

Persistent – lives on-chain, stored in the blockchain state.

Expensive — every write costs gas, because miners/validators must store it on disk.

Word size: 32 bytes.

Use case: contract state variables, balances, mappings, anything you want to persist.
"""
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

storage = Storage()
storage.store(1, 420)
print(storage.cache)
print(storage.load(1))
print(storage.load(1))
print(storage.cache)
print(storage.load)