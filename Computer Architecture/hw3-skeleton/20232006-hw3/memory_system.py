from cache import Cache
from ram import RAM


# do not modify this code
class Memory:
    def __init__(self):
        self.ram = RAM()
        self.cache = Cache(self.ram)

    def read(self, address):
        return self.cache.read(address)

    def write(self, address, value):
        self.cache.write(address, value)

    def dump(self):
        self.cache.dump()
        self.ram.dump()
