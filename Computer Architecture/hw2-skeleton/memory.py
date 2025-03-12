import utils

class Memory:
    # do not modify this function
    def __init__(self, inst_file, data_file):
        self.instruction_memory = self.load_instructions(inst_file)
        self.data_memory = self.load_data(data_file)


    # do not modify this function
    def load_instructions(self, inst_file):
        instruction_memory = {}
        with open(inst_file, 'r') as file:
            address = 0
            for line in file:
                line = line.split('#')[0].strip()  # Remove comments after '#'
                instruction_memory[address] = int(line, 16)  # Store as hexadecimal integer
                address += 4
        return instruction_memory

    # do not modify this function
    def load_data(self, data_file):
        data_memory = {}
        with open(data_file, 'r') as file:
            for line in file.read().strip().split("\n"):
                address, value = line.strip().split()
                data_memory[int(address)] = int(value, 16)  # Store as hexadecimal integer
        return data_memory

    def read_instruction(self, address):
        """
        Read (fetch) an instruction form instruction_memroy.

        Parameters:
            - address (int): The address to read the value from.

        Returns:
            - The instruction memory value (int) at the specified address.
        """
        return self.instruction_memory[address]

    def read_data(self, address):
        """
        Read data from data_memory.

        Parameters:
            - address (int): The address to read the data from .

        Returns:
            - The data memory value (int) at the specified address.
        """       
        if address % 4 == 0 and 0 <= address < 32:
            return self.data_memory[address]
        utils.handle_invalid_memory_access()

    def write_data(self, address, value):
        """
        Write data to data_memory.

        Parameters:
            - address (int): The address in data memory to write to.
            - value (int): The value to store at the specified address.

        Returns:
            None.
        """
        if address % 4 == 0 and 0 <= address < 32:
            self.data_memory[address] = value
        else:
            utils.handle_invalid_memory_access()

    # do not modify this function
    def dump_data_memory(self):
        print ("-" * 35)
        print ("Current memory states:")
        print ("-" * 35)
        for address in range(0, 32, 4):
            print(f"Address {address:02}: 0x{self.read_data(address):08x}")
        print ("-" * 35)
