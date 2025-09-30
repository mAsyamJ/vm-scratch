
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

    # CREATE STACK
stack = Stack()

stack.push(1)
stack.push(2)
stack.push(3)
stack.pop(2)
stack.push(1000)
print(stack)

