import time
import csv
import argparse
import random

from B_tree import BTree
from BStar import BStarTree
from BPlus import BPlusTree

def run_insert_experiment(tree_type, d, data):
    # Select tree class
    if tree_type == 'btree':
        tree = BTree(d)
    elif tree_type == 'bstar':
        tree = BStarTree(d)
    else:
        tree = BPlusTree(d)

    start_time = time.time()
    for rid, record in enumerate(data):
        tree.insert(int(record['Student ID']), rid)
    end_time = time.time()


    duration = end_time - start_time
    # Note: You must add a 'get_metrics()' method to your tree classes
    # to return split_count and node_utilization.
    splits = tree.get_split_count() 
    utilization = tree.calculate_utilization()
    print(f"{tree_type.upper()} (d={d}):")
    print(f"  Time: {duration:.4f}s | Splits: {splits} | Utilization: {utilization:.2%}")


def evaluate_sorted_insertion(tree_type, data):
    # Ensure numerical sort
    sorted_data = sorted(data, key=lambda x: int(x['Student ID']))
    
    degrees = list(range(2, 21, 2))
    times = []
    utilizations = []
    splits = []

    print(f"\nEvaluation for {tree_type.upper()}")

    for d in degrees:
        if tree_type == 'btree':
            tree = BTree(d)
        elif tree_type == 'bstar':
            tree = BStarTree(d)
        else:
            tree = BPlusTree(d)
        
        start_time = time.perf_counter()
        for rid, record in enumerate(sorted_data):
            tree.insert(int(record['Student ID']), rid)
        end_time = time.perf_counter()
        
        exec_time = end_time - start_time
        split_count = tree.get_split_count()
        util = tree.calculate_utilization()

        times.append(exec_time)
        utilizations.append(util)
        splits.append(split_count)
        
        print(f"d={d:2d} | Time: {exec_time:.4f}s | Util: {util:.2%}")


    return degrees, times, utilizations

def plot_combined_execution_time(all_tree_data):
    plt.figure(figsize=(10, 6))
    
    # Define distinct styles for each tree type
    styles = {
        'btree': {'color': '#1f77b4', 'marker': 'o', 'label': 'B-Tree'},
        'bstar': {'color': '#2ca02c', 'marker': 's', 'label': 'B* Tree'},
        'bplus': {'color': '#d62728', 'marker': '^', 'label': 'B+ Tree'}
    }

    for tree_type, (degrees, times) in all_tree_data.items():
        plt.plot(
            degrees, 
            times, 
            label=styles[tree_type]['label'],
            color=styles[tree_type]['color'],
            marker=styles[tree_type]['marker'],
            linewidth=2,
            markersize=7
        )

    # Force x-axis to show the specific degrees used
    plt.xticks(degrees) 
    
    plt.title('Execution Time vs. Tree Degree (Sorted Insertion)', fontsize=14)
    plt.xlabel('Degree (d)', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=11)
    
    # Save for Overleaf
    plt.savefig("combined_execution_time.png", dpi=300)
    plt.show()

def search(tree_type, d, data, num_queries = 10000):
    if tree_type == 'btree':
        tree = BTree(d)
    elif tree_type == 'bstar':
        tree = BStarTree(d)
    else:
        tree = BPlusTree(d)

    for rid, record in enumerate(data):
        tree.insert(int(record['Student ID']), rid)

    all_ids = [int(record['Student ID']) for record in data]
    search_targets = random.sample(all_ids, num_queries)


    start_time = time.time()
    for target in search_targets:
        result = tree.search(target)
        if result is None:
            print(f"Error: Key {target} not found!") 
    end_time = time.time()

    total_time = end_time - start_time
    mean_time = total_time / num_queries

    print(f"{tree_type.upper()} (d={d}):")
    print(f"  Search Queries: {num_queries}")
    print(f"  Mean Execution Time: {mean_time:.8f}s")

def run_range_query(tree_type, d, data, start_id, end_id):

    if tree_type == 'btree':
        tree = BTree(d)
    elif tree_type == 'bstar':
        tree = BStarTree(d)
    else:
        tree = BPlusTree(d)
    
    for rid, record in enumerate(data):
        tree.insert(int(record['Student ID']), rid)
    start_time = time.time()
    
    rids = tree.get_range(int(start_id), int(end_id))
    if not rids:
        print(f"DEBUG: Tree has {tree.get_split_count()} splits, but range [{start_id}-{end_id}] found nothing.")
        # Check the very first key in the root to see what's in there
        if len(tree.root.keys) > 0:
            print(f"DEBUG: Root key example: {tree.root.keys[0]}")
    
    # 2. Perform Analytics
    total_gpa = 0
    total_height = 0
    count = 0
    
    for rid in rids:
        student = data[rid]
        # Filter by Male
        if student['Gender'].lower() == 'male':
            total_gpa += float(student['GPA'])
            total_height += float(student['Height'])
            count += 1
            
    avg_gpa = total_gpa / count if count > 0 else 0
    avg_height = total_height / count if count > 0 else 0
    
    execution_time = time.time() - start_time
    
    print(f"\nRange Query Results ({tree_type.upper()}):")
    print(f"  Execution Time: {execution_time:.6f}s")
    print(f"  Results: Avg GPA: {avg_gpa:.2f}, Avg Height: {avg_height:.2f} (n={count})")
    
    return execution_time

def run_deletion_benchmark(tree_type, d, data, num_to_delete=2000):
    if tree_type == 'btree':
            tree = BTree(d)
    elif tree_type == 'bstar':
        tree = BStarTree(d)
    else:
        tree = BPlusTree(d)
    
    for rid, record in enumerate(data):
        tree.insert(int(record['Student ID']), rid)

 
    all_ids = [int(record['Student ID']) for record in data]
    ids_to_delete = random.sample(all_ids, num_to_delete)
    
    start_time = time.time()
    
    for student_id in ids_to_delete:
        tree.delete(student_id)
        
    execution_time = time.time() - start_time
    
    print(f"\nDeletion Results ({tree_type.upper()}):")
    print(f"  Deleted: {num_to_delete} records")
    print(f"  Execution Time: {execution_time:.6f}s")
    
    return execution_time

import matplotlib.pyplot as plt

def plot_degree_vs_time(results):

    plt.figure(figsize=(12, 7))
    
    # Use distinct colors and markers for clarity
    styles = {
        'B Tree': {'color': 'blue', 'marker': 'o'},
        'B* Tree': {'color': 'green', 'marker': 's'},
        'B+ Tree': {'color': 'red', 'marker': '^'}
    }

    for tree_type, data in results.items():
        plt.plot(
            data['d'], 
            data['time'], 
            label=tree_type, 
            color=styles.get(tree_type, {}).get('color', 'black'),
            marker=styles.get(tree_type, {}).get('marker', 'x'),
            linewidth=2,
            markersize=8
        )

    plt.title('U-Curve Analysis: Execution Time vs. Tree Degree ($d$)', fontsize=14)
    plt.xlabel('Degree ($d$)', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    
    # Optional: Highlight the best degree found across all tests
    plt.tight_layout()
    plt.savefig('degree_vs_time_u_curve.png') # Save it for your report
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tree', choices=['btree', 'bstar', 'bplus', 'all'], required=True)
    parser.add_argument('--d', type=int, nargs='+', required=True)
    args = parser.parse_args()

    # Load CSV into memory
    with open('student.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    trees_to_test = ['btree', 'bstar', 'bplus'] if args.tree == 'all' else [args.tree]
    
    # Code block for testing required operations
    for d_val in args.d:
        for t in trees_to_test:
            # run_insert_experiment(t, d_val, data)
            # run_range_query(t, d_val, data,  int(202100000),  int(202200001))
            # search(t, d_val, data)
            run_deletion_benchmark(t, d_val, data, 2000)

    # Code block for additional experiment (sorted insertion) only
    # all_results = {}
    # for t in trees_to_test:
    #     degs, times,_= evaluate_sorted_insertion(t, data)
    #     all_results[t] = (degs, times)
    # plot_combined_execution_time(all_results)
