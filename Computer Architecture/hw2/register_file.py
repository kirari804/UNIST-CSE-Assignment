import utils

class RegisterFile:
    # do not modify this function
    def __init__(self, reg_file):
        self.registers = self.load_registers(reg_file)

    # do not modify this function
    def load_registers(self, filename):
        registers = {}
        with open(filename, 'r') as file:
            for line in file:
                reg, value = line.strip().split()
                registers[reg] = int(value, 16)
        return registers

    #FIXME
    def read(self, reg_num):
        """
        This function reads the value stored in the specified register.

        Parameters:
            - reg_num (int): The register number to read the value from.

        Returns:
            - The value stored in the specified register in self.registers
              (int)
        """
        try:
            return self.registers[f'${reg_num}']
        except KeyError:
            utils.handle_invalid_register_access()

    def write(self, reg_num, value):
        """
        This function writes a value to the specified register in
        self.registers.

        Parameters:
            - reg_num (int): The register number to write the value to.
            - value (int): The value to store in the specified register.

        Returns:
            None
        """
        try:
            self.registers[f'${reg_num}'] = value
        except KeyError:
            utils.handle_invalid_register_access()

    # do not modify this function
    def dump_register(self):
        print ("-" * 35)
        print ("Current register states:")
        print ("-" * 35)
        for reg_num in range(10):
            print(f"${reg_num}: 0x{self.read(reg_num):08x}")
        print ("-" * 35)
