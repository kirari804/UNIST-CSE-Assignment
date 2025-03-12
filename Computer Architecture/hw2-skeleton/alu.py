import math
import utils

class ALU:
    # do not modify this function
    def __init__(self):
        pass

    def operate(self, operation, operand1, operand2):
        """
        Perform ALU operation based on the operation code.cd 

        Parameters:
            - operation (int): The 4-bit ALU control signal that determines
              the operation to be performed.
            - operand1 (int): The first operand (32-bit data) for the ALU
              operation.
            - operand2 (int): The second operand (32-bit data) for the ALU
              operation.

        Functionality:
            - This function performs ALU operations based on the operation
              argument and the operand1 and operand2 arguments. It returns the
              result of the operation along with a zero flag.


        Returns:
            - A tuple (result, zero), where:
                - result (int): Result of the ALU operation.
                - zero (int): A flag indicating if the result is zero (1 if
                              zero, otherwise 0).
        """
        MAX_INT_32 = 0x7FFFFFFF 
        MIN_INT_32 = -0x80000000
        if operation == 0x0010:  # add
            result = (operand1 + operand2) 
            if result > MAX_INT_32:
                utils.handle_overflow()
            result &= 0xFFFFFFFF
        elif operation == 0x0110: #substract
            result = operand1-operand2
            if result > MAX_INT_32 or result < MIN_INT_32:
                utils.handle_overflow()
            result &= 0xFFFFFFFF
        elif operation == 0x0000: #and
            result = operand1 & operand2
        elif operation == 0x0001: #or
            result = operand1 | operand2
        elif operation == 0x0111: #slt
            signed_operand1 = operand1 if operand1 < 0x80000000 else operand1 - 0x100000000
            signed_operand2 = operand2 if operand2 < 0x80000000 else operand2 - 0x100000000
            if (signed_operand1 < signed_operand2):
                result = 1
            else:
                result = 0
        elif operation == 0x1100:
            result = ~(operand1 | operand2) & 0xFFFFFFFF
        else:
            utils.handle_invalid_operation()
        return result, int(result == 0)
