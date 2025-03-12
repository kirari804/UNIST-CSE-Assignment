BLOCK_SIZE = 8
WORD_SIZE = 4
ADDR_MIN = 0x10000000
ADDR_RANGE = 0x700
ADDR_MAX = ADDR_MIN + ADDR_RANGE


def base_index(address):
    word = (address - ADDR_MIN) // WORD_SIZE
    return word - (word % BLOCK_SIZE)


class RAM:
    def __init__(self):
        self.words = [0 for _ in range(ADDR_MIN, ADDR_MAX, WORD_SIZE)]

    # Unlike Homework 2, we will not test each function individually in this
    # assignment. Therefore, if you do not want to use the skeleton code, you
    # are allowed to write the code from scratch. Additionally, you are free to
    # modify the parameters, return types, or other aspects

    #  Retrieves a 32-byte block of data from the main memory
    def block_read(self, address):
        """Retrieve a 32-byte block of data from the main memory."""
        base = base_index(address)
        return self.words[base:base+BLOCK_SIZE]

    def block_write(self, address, block_data):
        """Write a 32-byte block of data from the cache back to the main memory."""
        base = base_index(address)
        self.words[base:base+BLOCK_SIZE] = block_data

    def dump(self):
        print(f"memory [0x{ADDR_MIN:08x}..0x{ADDR_MAX:08x}] :")
        print("-------------------------------------")
        for addr in range(ADDR_MIN, ADDR_MAX, WORD_SIZE*BLOCK_SIZE):
            block_repr = '.'.join(f'{word:08x}' for word in self.block_read(addr))
            print(f'{addr:08x}...{addr+0x1c:08x}|', block_repr, '|')
        print('\n')
