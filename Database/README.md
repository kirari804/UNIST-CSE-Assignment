Tree-Based Indexing Structures: Performance Benchmark

1. Prerequisites:
   
  Programming Language: Python 3.10 or higher.

  Operating System: Cross-platform (Linux, macOS, Windows).

  Required Dependencies
  The benchmarking tool utilizes standard Python libraries and matplotlib for data visualization.

2. File Structure
   
  evaluate.py: The main entry point for running benchmarks.

  B_tree.py: Implementation of the standard B-Tree.

  BStar.py: Implementation of the B*-Tree (2/3 occupancy logic).

  BPlus.py: Implementation of the B+ Tree (linked leaf nodes).

  student.csv: The dataset containing student records (required for execution).
  
3. Execution Instructions
   
  
 Basic Command syntax (for required operations):
 python3 evaluate.py --tree <tree_type> --d <degree_values>
 
 Basic Command syntax (for additional experiment)
 python3 evaluate.py --tree all

 To switch to this benchmark, you should command out the line 'parser.add_argument('--d', type=int, nargs='+', required=True)' and the code block for testing required operations (specified in 'evaluate.py'). Use the code block for testing the additional experiment.
