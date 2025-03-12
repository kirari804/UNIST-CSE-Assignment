import subprocess
import difflib
import sys

def compare_output(command_str, txt_file):
    try:
        # Parse command_str
        command_parts = command_str.split()
        python_executable = command_parts[0]
        python_file = command_parts[1]
        script_args = command_parts[2:]

        # Run the Python file and capture stdout, with arguments included
        result = subprocess.run(
            [python_executable, python_file] + script_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # If there is an error, print it and exit
        if result.returncode != 0:
            print("Error executing the Python file:")
            print(result.stderr)
            return False

        # Captured output from the Python file
        output = result.stdout.strip()

        # Read the contents of the expected output text file
        with open(txt_file, 'r') as f:
            expected_output = f.read().strip()

        # Compare results
        if output == expected_output:
            print("The output matches the expected output.")
            return True
        else:
            print("The output does NOT match the expected output.")
            print("\nDifference (lines starting with '-' are in expected output, '+' in actual output):\n")

            # Print differences
            diff = difflib.unified_diff(
                output.splitlines(),
                expected_output.splitlines(),
                fromfile='Actual Output',
                tofile='Expected Output',
                lineterm=''
            )
            for line in diff:
                print(line)
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    # Check if the txt_file argument is provided
    if len(sys.argv) < 2:
        print("Usage: python3 %s <test_case_dir>" % sys.argv[0])
        sys.exit(1)

    test_case_dir = sys.argv[1]                      # Expected output text file from command line
    command_str = f"python3 main.py --access-log {test_case_dir}/memory_access_log.txt"  # Command string with script and arguments
    expected_result_file = f"{test_case_dir}/expected_result.txt"

    # Call the comparison function
    compare_output(command_str, expected_result_file)
