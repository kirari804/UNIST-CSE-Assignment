from alu import ALU
from control import Control
from memory import Memory
from register_file import RegisterFile
import utils

import sys

class CPU:
    # do not modify this function
    def __init__(self, inst_file, data_file, reg_file):
        self.pc = 0
        self.alu = ALU()
        self.control = Control()
        self.memory = Memory(inst_file, data_file)
        self.register_file = RegisterFile(reg_file)


    #FIXME
    def run_cycle(self):
        """
        Implement the cycle steps by using the self.pc, self.alu, self.control,
        self.memory, and self.register_file objects.

        Functionality:
            1. Instruction Fetch
            2. Instruction Decode
               - During this step, set control signals by using
                 set_control_signals and set_alu_signal functions
            3. Execute
            4. Memory Access
            5. Register Write-back
            Also, update the PC for the next instruction

        Returns:
            None
        """
        #IF
        inst = self.memory.read_instruction(self.pc)
        assert(0 <= inst < 1 << 32)
        utils.print_instruction_fetch(self.pc, inst)

        #ID
        opcode = (inst >> 26) & 0x3F
        self.control.set_control_signals(opcode)
        if opcode == 0x0:  # R-type
            funct = inst & 0x3F
            aluop = self.control.signals["ALUOp"]
            self.control.set_alu_signal(aluop, funct)
        elif opcode in {0x23, 0x2B, 0x04, 0x08}:
            aluop = self.control.signals["ALUOp"]
            self.control.set_alu_signal(aluop, None)
        
        #Execute
        rs = (inst >> 21) & 0x1F
        rt = (inst >> 16) & 0x1F
        immediate = inst & 0xFFFF
        immediate = (immediate ^ 0x8000) - 0x8000

        operation = self.control.get_alu_signal()
        operand1 = self.register_file.read(rs)
        operand2 = self.register_file.read(rt)
        if not self.control.signals["ALUSrc"]: #r-type and beq
            alu_result, zero_flag = self.alu.operate(operation, operand1, operand2)
        else: #lw, sw and i-type
            alu_result, zero_flag = self.alu.operate(operation, operand1, immediate)
        if opcode == 0x04 and zero_flag:
            offset = immediate << 2
            self.pc = self.pc + 4 + offset
        else:
            self.pc+=4
        
        #MEM
        if self.control.signals["MemRead"]:
            data_memory_value = self.memory.read_data(alu_result)
        elif self.control.signals["MemWrite"]:
            self.memory.write_data(alu_result, operand2)
        
        #WB:
        if self.control.signals["RegWrite"]:
            if self.control.signals["RegDst"]: #dest_reg is rd in r-type
                dest_reg = (inst >> 11) &0x1F 
            else:                              #dest_reg is rt in i-type
                dest_reg = (inst >> 16) & 0x1F 

            if self.control.signals["MemtoReg"]:
                value = data_memory_value
            else:
                value = alu_result
            self.register_file.write(dest_reg, value)
        

    # do not modify this function
    def run(self):
        print (f"[*] Initial states")
        self.register_file.dump_register()
        self.memory.dump_data_memory()

        cycle_num = 1
        while self.pc in self.memory.instruction_memory:
            print (f"\n[*] Current cycle: {cycle_num}")
            self.run_cycle()
            self.register_file.dump_register()
            self.memory.dump_data_memory()

            cycle_num += 1
