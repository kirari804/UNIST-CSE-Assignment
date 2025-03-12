import argparse
from cpu import CPU

# do not modify this code
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIPS CPU Simulator")
    parser.add_argument("--inst-file", type=str, required=True, help="Path to the instruction memory file")
    parser.add_argument("--data-file", type=str, required=True, help="Path to the data memory file")
    parser.add_argument("--reg-file", type=str, required=True, help="Path to the register file")
    args = parser.parse_args()

    hw2_cpu = CPU(args.inst_file, args.data_file, args.reg_file)
    hw2_cpu.run()
