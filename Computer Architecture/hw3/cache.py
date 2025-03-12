from collections import deque

from ram import BLOCK_SIZE, WORD_SIZE

ASSOC = 4
SETS = 8


def set_index(address):
    return address // WORD_SIZE // BLOCK_SIZE % SETS


def block_offset(address):
    return address // WORD_SIZE % BLOCK_SIZE


def tag_from_address(address):
    return address // (WORD_SIZE*BLOCK_SIZE*SETS)


def address_from_tag(tag, set_idx):
    return (tag*SETS + set_idx) * WORD_SIZE * BLOCK_SIZE

class Cache:
    def __init__(self, ram):
        self.ram = ram
        self.sets = [Set(i) for i in range(SETS)]

    # Unlike Homework 2, we will not test each function individually in this
    # assignment. Therefore, if you do not want to use the skeleton code, you
    # are allowed to write the code from scratch. Additionally, you are free to
    # modify the parameters, return types, or other aspects

    def get_block(self, address):
        """Return the cache block containing the word at given address."""
        return self.sets[set_index(address)].find(tag_from_address(address), self.ram)

    def read(self, address):
        """Retrieve data from the cache using the given address."""
        return self.get_block(address).data[block_offset(address)]
        
    # Stores data in the cache at the specified address
    def write(self, address, data):
        block = self.get_block(address)
        block.data[block_offset(address)] = data   
        block.dirty = 1

    def dump(self):
        print("Cache content:")

        empty = " " * BLOCK_SIZE * WORD_SIZE
        print(f"|index| v |  tag   |  {empty}way0{empty}   | v |  tag   |  {empty}way1{empty}   | v |  tag   |  {empty}way2{empty}   | v |  tag   |  {empty}way3{empty}   |")

        idx = 0
        for set in self.sets:
            pline = f"| {idx:03b} |"
            for b in set.blocks:
                data_str = '.'.join(f"{word_data:08x}" for word_data in b.data)
                pline += f" {b.valid} | {b.tag:06x} | {data_str} |"
            print(pline)
            idx += 1
        print("")


class Block:
    def __init__(self):
        self.valid = 0
        self.dirty = 0
        self.tag = 0
        self.data = [0x00000000] * BLOCK_SIZE


class Set:
    def __init__(self, index):
        self.index = index
        self.blocks = [Block() for i in range(ASSOC)]
        self.history = deque(range(ASSOC)) # Access history for LRU replacement

    def find(self, tag, ram):
        for i, block in enumerate(self.blocks):
            if block.tag == tag and block.valid:  # cache hit
                self.history.remove(i)
                self.history.append(i)
                return block

        block = self.blocks[self.history[0]]
        if block.valid and block.dirty:  # write back
            ram.block_write(address_from_tag(block.tag, self.index), block.data)

        # New block
        block.tag = tag
        block.valid = 1
        block.dirty = 0
        block.data = ram.block_read(address_from_tag(tag, self.index))
        self.history.rotate(-1)
        return block