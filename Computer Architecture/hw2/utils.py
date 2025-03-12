import sys

# do not modify this function
def print_instruction_fetch(pc, instruction):
    print(f"Fetching instruction at PC={pc}: 0x{instruction:08X}")

# do not modify this function
def handle_overflow():
    print("Error: integer overflow")
    sys.exit()

# do not modify this function
def handle_invalid_opcode():
    print("Error: invalid opcode")
    sys.exit()

# do not modify this function
def handle_invalid_funct():
    print("Error: invalid funct")
    sys.exit()

# do not modify this function
def handle_invalid_memory_access():
    print("Error: invalid memory access")
    sys.exit()

# do not modify this function
def handle_invalid_register_access():
    print("Error: invalid register access")
    sys.exit()

def handle_invalid_operation():
    print("Error: invalid operation")
    sys.exit()
# You can write the necessary functions here
