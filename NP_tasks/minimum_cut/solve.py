import json
import argparse
import time
import random
import math
from collections import defaultdict

class MinBisectionSolver:
    """
    Solves the Balanced Minimum Bisection problem using Simulated Annealing,
    a powerful metaheuristic suitable for finding high-quality approximate
    solutions to combinatorial optimization problems.
    """
    def __init__(self, graph_data, timeout=60):
        self.nodes = sorted(list(graph_data.keys()))
        self.num_vertices = len(self.nodes)
        self.adj = {node: defaultdict(int) for node in self.nodes}
        for u, neighbors in graph_data.items():
            for v, weight in neighbors.items():
                # Ensure the graph is undirected for calculations
                u_int, v_int = int(u), int(v)
                self.adj[u_int][v_int] = weight
                self.adj[v_int][u_int] = weight
        
        self.timeout = timeout
        self.start_time = None

    def _calculate_cut_and_D_values(self, partition_A_set, partition_B_set):
        """Calculates the initial cut size and all D-values."""
        cut_size = 0
        D = {}
        for node in self.nodes:
            internal_cost = 0
            external_cost = 0
            current_partition = partition_A_set if node in partition_A_set else partition_B_set
            other_partition = partition_B_set if node in partition_A_set else partition_A_set
            
            for neighbor, weight in self.adj[node].items():
                if neighbor in current_partition:
                    internal_cost += weight
                else: # neighbor in other_partition
                    external_cost += weight
            
            D[node] = external_cost - internal_cost
            if node in partition_A_set:
                cut_size += external_cost
        # Each edge from A to B is counted once by this loop, so the sum is the correct cut size.
        return cut_size, D

    def solve(self):
        self.start_time = time.time()

        # 1. Initial State
        nodes_shuffled = self.nodes[:]
        random.shuffle(nodes_shuffled)
        size_A = self.num_vertices // 2
        
        partition_A = nodes_shuffled[:size_A]
        partition_B = nodes_shuffled[size_A:]
        
        partition_A_set = set(partition_A)
        partition_B_set = set(partition_B)

        current_cut, D_values = self._calculate_cut_and_D_values(partition_A_set, partition_B_set)
        
        best_partition = [sorted(partition_A), sorted(partition_B)]
        best_cut_size = current_cut

        # 2. Simulated Annealing Parameters
        initial_temp = current_cut / 10 if current_cut > 0 else 1.0
        T = initial_temp
        cooling_rate = 0.9995
        
        iteration = 0
        while time.time() - self.start_time < self.timeout:
            iteration += 1

            # 3. Propose a move (swap) using a semi-greedy strategy
            if not partition_A or not partition_B: continue

            a = random.choice(partition_A)
            
            # Find the best node `b` in partition_B to swap with `a`
            best_gain = -float('inf')
            best_b = None
            
            for b_candidate in partition_B:
                gain = D_values[a] + D_values[b_candidate] - 2 * self.adj[a][b_candidate]
                if gain > best_gain:
                    best_gain = gain
                    best_b = b_candidate
            
            if best_b is None: continue
            b = best_b

            # 4. Calculate change in cut size (delta)
            delta = -best_gain # delta < 0 is an improvement

            # 5. Decision: Accept or reject the move
            if delta < 0 or (T > 0 and random.random() < math.exp(-delta / T)):
                # Accept the move: update partitions and D-values
                partition_A.remove(a)
                partition_A.append(b)
                partition_B.remove(b)
                partition_B.append(a)
                
                old_D_a, old_D_b = D_values[a], D_values[b]

                # Update D-values for a and b
                D_values[a] = -old_D_a + 2 * self.adj[a][b]
                D_values[b] = -old_D_b + 2 * self.adj[a][b]
                
                # Update D-values for neighbors of a and b
                for neighbor, weight in self.adj[a].items():
                    if neighbor != b: D_values[neighbor] += 2 * weight if neighbor in partition_A else -2 * weight
                for neighbor, weight in self.adj[b].items():
                    if neighbor != a: D_values[neighbor] += 2 * weight if neighbor in partition_B else -2 * weight

                current_cut += delta
                
                if current_cut < best_cut_size:
                    best_cut_size = current_cut
                    best_partition = [sorted(partition_A), sorted(partition_B)]
            
            # 6. Cool down
            T *= cooling_rate
        
        print(f"   - Finished after {iteration} iterations.")
        return best_partition, best_cut_size


def parse_question_to_graph_data(data):
    graph = defaultdict(dict)
    nodes = set()
    for u_str, neighbors in data.items():
        u = int(u_str)
        nodes.add(u)
        for v_str, weight in neighbors.items():
            v = int(v_str)
            nodes.add(v)
            graph[u][v] = weight
    
    # Ensure all nodes are keys in the graph dict
    for node in nodes:
        if node not in graph:
            graph[node] = {}

    return {int(k): v for k, v in graph.items()}

def main():
    parser = argparse.ArgumentParser(description="Solve Balanced Minimum Bisection problems from a JSON file and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with graph problems.')
    parser.add_argument('--timeout', type=int, default=0.1, help='Timeout in seconds for each problem.')
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {args.file}")
        return
        
    questions = data.get("questions")
    if not questions:
        print(f"Error: No 'questions' key found in '{args.file}'")
        return
        
    total_questions = len(questions)
    
    for i, (question_name, question_data) in enumerate(sorted(questions.items())):
        print(f"--- [{i+1}/{total_questions}] Solving Min Bisection for: {question_name} ---")
        
        graph_data = parse_question_to_graph_data(question_data)
        
        solver = MinBisectionSolver(graph_data, timeout=args.timeout)
        partition, cut_size = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = cut_size
        
        print(f"--- Finished {question_name}, Min Cut Size Found: {cut_size} ---")
        print("-" * 50)

    # Save the modified data back to the original file
    try:
        with open(args.file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSuccessfully processed all {total_questions} problems.")
        print(f"All solutions have been added to '{args.file}' with ground_truth fields.")
    except IOError as e:
        print(f"\nError writing solutions to file: {e}")

if __name__ == '__main__':
    main() 