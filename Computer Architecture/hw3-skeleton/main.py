import sys
import memory_system
import argparse

# do not modify this code
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIPS Cache Simulator")
    parser.add_argument("--access-log", type=str, required=True, help="Path to the memory accessing log file")
    args = parser.parse_args()

    mem = memory_system.Memory()

    access_log = args.access_log
    with open(access_log, "r") as f:
        lines = f.readlines()

    for line in lines:
        mem.dump()
        line = line.split('#')[0].strip()  # Remove comments after '#'
        log_content = line.split()
        address = int(log_content[0], 16)
        if len(log_content) == 2:
            data = int(log_content[1], 16)
            mem.write(address, data)
            print (f"[*] Write data {data:08x} to {address:08x}")
        else:
            data = mem.read(address)
            print (f"[*] Read data {data:08x} from {address:08x}")
    mem.dump()
