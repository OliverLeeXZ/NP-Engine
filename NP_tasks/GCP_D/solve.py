import json
import time
import argparse
import random
from collections import defaultdict

class GCP_Solver:
    """
    A solver for the Graph Coloring Problem (GCP-D) using a powerful hybrid
    heuristic approach:
    1. DSatur algorithm for a high-quality initial coloring.
    2. Tabu Search to iteratively try and reduce the number of colors used.
    """

    def __init__(self, adj_list, timeout=60):
        self.adj_list = {int(k): v for k, v in adj_list.items()}
        self.nodes = sorted(self.adj_list.keys())
        self.num_vertices = len(self.nodes)
        self.timeout = timeout
        self.start_time = None

    def _dsatur_initial_coloring(self):
        """
        Generates a valid coloring using the DSatur heuristic.
        Returns a dictionary of node->color and the number of colors used.
        """
        if not self.nodes:
            return {}, 0

        # Saturation degrees, and degrees for tie-breaking
        saturation = {node: 0 for node in self.nodes}
        degrees = {node: len(self.adj_list.get(node, [])) for node in self.nodes}
        coloring = {}
        uncolored_nodes = set(self.nodes)

        while uncolored_nodes:
            # Select the node with max saturation, breaking ties with max degree
            node_to_color = max(uncolored_nodes, key=lambda u: (saturation[u], degrees[u]))
            
            uncolored_nodes.remove(node_to_color)
            
            # Find the smallest valid color for this node
            neighbor_colors = {coloring[n] for n in self.adj_list.get(node_to_color, []) if n in coloring}
            color = 1
            while color in neighbor_colors:
                color += 1
            coloring[node_to_color] = color

            # Update saturation degrees of its neighbors
            for neighbor in self.adj_list.get(node_to_color, []):
                if neighbor in uncolored_nodes:
                    # Recalculate saturation for precision
                    neighbor_neighbor_colors = {coloring[n] for n in self.adj_list.get(neighbor, []) if n in coloring}
                    saturation[neighbor] = len(neighbor_neighbor_colors)
        
        num_colors = max(coloring.values()) if coloring else 0
        return coloring, num_colors

    def _tabu_search_for_k_colors(self, k, base_coloring, max_iter=10000):
        """
        Tries to find a valid k-coloring using Tabu Search, starting from a
        modified (k+1)-coloring instead of a random one.
        The objective is to minimize the number of conflicts (colliding edges).
        """
        # --- intelligent Initialization from base_coloring (k+1 colors) ---
        current_coloring = dict(base_coloring)
        
        # Group nodes by color
        colors_to_nodes = defaultdict(list)
        for node, color in current_coloring.items():
            colors_to_nodes[color].append(node)
            
        # Sort color classes by size to find the smallest ones to merge
        sorted_color_classes = sorted(colors_to_nodes.items(), key=lambda item: len(item[1]))
        
        # Merge the smallest color class into the second smallest
        if len(sorted_color_classes) > 1:
            color_to_remove = sorted_color_classes[0][0]
            nodes_to_recolor = sorted_color_classes[0][1]
            target_color = sorted_color_classes[1][0]
            for node in nodes_to_recolor:
                current_coloring[node] = target_color
        
        # Remap colors to be contiguous from 1 to k
        distinct_colors = sorted(list(set(current_coloring.values())))
        color_map = {old_color: new_color for new_color, old_color in enumerate(distinct_colors, 1)}
        current_coloring = {node: color_map[color] for node, color in current_coloring.items()}

        # Calculate initial conflicts
        conflicts = set()
        for u in self.nodes:
            for v in self.adj_list.get(u, []):
                if u < v and current_coloring[u] == current_coloring[v]:
                    conflicts.add(tuple(sorted((u, v))))
        
        tabu_list = {} # Using dict for (node, color) -> iteration_to_unban
        tabu_tenure = min(15, self.num_vertices // 4 + 1)
        
        best_conflict_count = len(conflicts)
        
        for i in range(max_iter):
            if not conflicts:
                return current_coloring # Success

            if time.time() - self.start_time > self.timeout:
                raise TimeoutError

            # Find best non-tabu move
            best_move = None
            best_delta = float('inf')

            # Consider moving a node from a conflicting edge to a new color
            conflicting_nodes = list(set(u for u, v in conflicts).union(v for u, v in conflicts))
            random.shuffle(conflicting_nodes)
            
            for node in conflicting_nodes: # Search all conflicting nodes
                current_color = current_coloring[node]
                for new_color in range(1, k + 1):
                    if new_color == current_color:
                        continue
                        
                    # Check if move is tabu
                    if (node, new_color) in tabu_list and tabu_list[(node, new_color)] > i:
                        continue

                    # Calculate change in conflicts (delta)
                    old_conflicts = sum(1 for neighbor in self.adj_list.get(node, []) if current_coloring[neighbor] == current_color)
                    new_conflicts = sum(1 for neighbor in self.adj_list.get(node, []) if current_coloring[neighbor] == new_color)
                    delta = new_conflicts - old_conflicts

                    if delta < best_delta:
                        best_delta = delta
                        best_move = (node, new_color)

            if best_move:
                node_to_move, new_color = best_move
                old_color = current_coloring[node_to_move]
                
                # Update conflicts
                for neighbor in self.adj_list.get(node_to_move, []):
                    edge = tuple(sorted((node_to_move, neighbor)))
                    if current_coloring[neighbor] == old_color: conflicts.remove(edge)
                    if current_coloring[neighbor] == new_color: conflicts.add(edge)

                # Make the move
                current_coloring[node_to_move] = new_color
                
                # Update tabu list
                tabu_list[(node_to_move, old_color)] = i + tabu_tenure
        
        return None # Failed to find a solution

    def solve(self):
        self.start_time = time.time()
        print("   1. Finding initial solution with DSatur...")
        best_coloring, k = self._dsatur_initial_coloring()
        if not best_coloring:
            return None, 0
        print(f"      - DSatur found a solution with {k} colors.")

        print("   2. Iteratively improving with Tabu Search...")
        try:
            for target_k in range(k - 1, 0, -1):
                if time.time() - self.start_time > self.timeout:
                    print("      - Timeout reached during improvement phase.")
                    break
                print(f"      - Trying to find a solution with {target_k} colors...")
                new_solution = self._tabu_search_for_k_colors(target_k, best_coloring)
                if new_solution:
                    best_coloring = new_solution
                    k = target_k
                    print(f"      - Success! Found a better solution with {k} colors.")
                else:
                    print(f"      - Failed to find a {target_k}-coloring. Best is {k}.")
                    break # Cannot improve further
        except TimeoutError:
            print("      - Timeout reached during Tabu Search for a specific k.")

        # Convert to list format for output
        final_coloring_list = [0] * self.num_vertices
        for node, color in best_coloring.items():
            final_coloring_list[node] = color

        return final_coloring_list, k


def parse_question_to_adj_list(question_data):
    adj_list = {}
    if not question_data: return adj_list
    for node_str, neighbors_list in question_data.items():
        adj_list[int(node_str)] = [int(n) for n in neighbors_list]
    return adj_list

def main():
    parser = argparse.ArgumentParser(description="Solve Graph Coloring problems from a JSON file and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with graph problems.')
    parser.add_argument('--timeout', type=float, default=0.01, help='Timeout in seconds for each problem.')
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
        print(f"--- [{i+1}/{total_questions}] Solving GCP for: {question_name} ---")
        
        adj_list = parse_question_to_adj_list(question_data)
        
        solver = GCP_Solver(adj_list, timeout=args.timeout)
        coloring, num_colors = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = num_colors
        
        print(f"--- Finished {question_name}, Best solution uses {num_colors} colors ---")
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