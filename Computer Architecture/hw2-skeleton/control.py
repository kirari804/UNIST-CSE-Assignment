import utils

class Control:

    # do not modify this function
    def __init__(self):
        self.signals = {
            "RegDst": None, "ALUSrc": None, "MemtoReg": None, "RegWrite": None,
            "MemRead": None, "MemWrite": None, "Branch": None, "ALUOp": None
        }
        self.alu_signal = 0

    #FIXME
    def set_control_signals(self, opcode):
        """
        Sets main control signals based on the given opcode.

        Parameters:
            - opcode (int): The 6-bit opcode value extracted from the
              instruction.

        Functionality:
            - Based on the opcode, this method determines the appropriate
              values for various control signals, including RegDst, ALUSrc,
              MemtoReg, RegWrite, MemRead, MemWrite, Branch, and ALUOp (signal
              values should be integer type). These control signals influence
              the datapath for instruction execution. The resulting control
              signals are stored in the self.signals dictionary. If the value
              of a control signal is 'don't care', assign it as None.
              Assign example:
                  self.signals = {
                      "RegDst": None, "ALUSrc": 1, "MemtoReg": None, "RegWrite": 0,
                      "MemRead": 0, "MemWrite": 1, "Branch": 0, "ALUOp": 0b00
                  }

        Returns:
            None
        """
        if opcode == 0x0: #R-type
            self.signals = {
                "RegDst": 1, "ALUSrc": 0, "MemtoReg": 0, "RegWrite": 1,
                "MemRead": 0, "MemWrite": 0, "Branch": 0, "ALUOp": 0b10
            }
        elif opcode == 0x23: #lw
            self.signals = {
                "RegDst": 0, "ALUSrc": 1, "MemtoReg": 1, "RegWrite": 1,
                "MemRead": 1, "MemWrite": 0, "Branch": 0, "ALUOp": 0b00
            }
        elif opcode == 0x2B: #sw
            self.signals = {
                "RegDst": None, "ALUSrc": 1, "MemtoReg": None, "RegWrite": 0,
                "MemRead": 0, "MemWrite": 1, "Branch": 0, "ALUOp": 0b00
            }
        elif opcode == 0x04: #beq
            self.signals = {
                "RegDst": None, "ALUSrc": 0, "MemtoReg": None, "RegWrite": 0,
                "MemRead": 0, "MemWrite": 0, "Branch": 1, "ALUOp": 0b01
            }
        elif opcode == 0x08: #addi
            self.signals = {
                "RegDst": 0, "ALUSrc": 1, "MemtoReg": 0, "RegWrite": 1,
                "MemRead": 0, "MemWrite": 0, "Branch": 0, "ALUOp": 0b00
            }
        else:
            utils.handle_invalid_opcode()

    #FIXME
    def set_alu_signal(self, aluop, funct):
        """
        Determines the ALU operation based on ALUOp and funct code.

        Parameters:
            - aluop (int): The 2-bit aluop control signal value.
            - funct (int): The 6-bit function code from the instruction.

        Functionality:
            - This function analyzes the aluop and funct to determine the exact
              ALU operation signal. The determined 4-bit ALU operation code
              (int) is stored in self.alu_signal.

        Returns:
            None

        /*************************************************/
        /********************* FIXME *********************/
        /*************************************************/
        """
        if aluop == 0b10: 
            if funct == 0b100000: #add
                self.alu_signal = 0x0010
            elif funct == 0b100010: #subtract
                self.alu_signal = 0x0110
            elif funct == 0b100100: #and
                self.alu_signal = 0x0000
            elif funct == 0b100101: #or
                self.alu_signal = 0x0001
            elif funct == 0b101010: #slt
                self.alu_signal = 0x0111
            else:
                utils.handle_invalid_funct()
        elif aluop == 0b00: #lw, sw, addi
            self.alu_signal = 0x0010
        elif aluop == 0b01: #beq
            self.alu_signal = 0x0110
        else:
            utils.handle_invalid_opcode()


    # do not modify this function
    # you can access to the signals dictionary using this function
    def get_signal(self, signal_name):
        return self.signals.get(signal_name)


    # you can access to the alu_signal variable using this function
    # do not modify this function
    def get_alu_signal(self):
        return self.alu_signal
