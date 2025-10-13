import json
import time
import argparse
import random

class LongestCycleSolver:
    """
    Finds a long simple cycle in a graph using a greedy heuristic with
    random restarts. This is for the optimization version of the Hamiltonian
    Cycle problem, where the goal is to maximize the number of vertices in a cycle.
    """

    def __init__(self, adj_list, timeout):
        """
        Initializes the solver.

        Args:
            adj_list (dict): An adjacency list representation of the graph.
            timeout (int): The maximum time in seconds to spend on solving.
        """
        self.adj_list = {int(k): v for k, v in adj_list.items()}
        self.nodes = list(self.adj_list.keys())
        self.num_vertices = len(self.nodes)
        self.timeout = timeout
        self.start_time = None
        self.best_cycle = []

    def _get_unvisited_neighbors(self, node, current_path_set):
        """Helper to get neighbors of a node that are not in the current path."""
        if node not in self.adj_list:
            return []
        return [n for n in self.adj_list[node] if n not in current_path_set]

    def _greedy_path_construction(self, start_node):
        """
        Constructs a long path greedily from a start_node using a smart heuristic.
        The heuristic (Warnsdorff's rule variant) is to choose the neighbor with
        the fewest onward unvisited connections.
        """
        path = [start_node]
        path_set = {start_node}
        
        current_node = start_node
        while True:
            unvisited_neighbors = self._get_unvisited_neighbors(current_node, path_set)
            
            if not unvisited_neighbors:
                break # Dead end

            # Find the neighbor with the minimum number of its own unvisited neighbors
            next_node = min(unvisited_neighbors, key=lambda n: len(self._get_unvisited_neighbors(n, path_set)))
            
            path.append(next_node)
            path_set.add(next_node)
            current_node = next_node
            
        return path

    def _close_path_to_cycle(self, path):
        """Tries to form the longest possible cycle from a given path."""
        if len(path) < 3:
            return []

        start_node = path[0]
        end_node = path[-1]
        
        # Check if the end node can connect back to any node in the path to form a cycle
        if end_node not in self.adj_list:
            return []

        path_set = set(path)
        end_node_neighbors = self.adj_list[end_node]

        # Iterate from the start of the path to find the earliest connection point
        for i, node in enumerate(path):
            if node in end_node_neighbors:
                # Found a connection. The cycle is from this point to the end.
                cycle = path[i:] + [node]
                return cycle
        
        return []

    def _improve_cycle_with_insertion(self, cycle):
        """
        Tries to extend a given cycle by inserting unvisited nodes.
        Repeats the process until no more nodes can be inserted.
        """
        current_cycle = list(cycle)
        
        while True:
            cycle_set = set(current_cycle)
            # Find nodes that are not in the cycle yet
            unvisited_nodes = [n for n in self.nodes if n not in cycle_set]
            
            if not unvisited_nodes:
                break # It's a full Hamiltonian cycle

            node_inserted_in_pass = False
            random.shuffle(unvisited_nodes)

            for node_to_insert in unvisited_nodes:
                # Find if this node can be inserted between any two adjacent nodes in the cycle
                neighbors_of_insert_node = set(self.adj_list.get(node_to_insert, []))
                
                # Check each edge (u, v) in the current cycle
                for i in range(len(current_cycle) - 1):
                    u, v = current_cycle[i], current_cycle[i+1]
                    
                    # If u and v are both neighbors of the node_to_insert, we can insert it.
                    if u in neighbors_of_insert_node and v in neighbors_of_insert_node:
                        # Insert the node: ...u, node_to_insert, v...
                        current_cycle.insert(i + 1, node_to_insert)
                        node_inserted_in_pass = True
                        break # Move to the next pass with the updated cycle
                
                if node_inserted_in_pass:
                    break # Restart the main while loop with the larger cycle
            
            # If we go through all unvisited nodes and can't insert any, we're done.
            if not node_inserted_in_pass:
                break
                
        return current_cycle

    def solve(self):
        """
        Repeatedly runs the greedy construction from random start nodes until timeout.
        
        Returns:
            - The longest cycle found (list of ints).
            - None if no cycle is found.
        """
        self.start_time = time.time()
        
        if not self.nodes:
            return None

        iteration = 0
        while time.time() - self.start_time < self.timeout:
            iteration += 1
            # Choose a random starting point for this iteration
            start_node = random.choice(self.nodes)
            
            # 1. Construct a long path greedily
            path = self._greedy_path_construction(start_node)
            
            # 2. Try to close the path to form a cycle
            cycle = self._close_path_to_cycle(path)
            
            # 3. Iteratively improve the cycle by inserting nodes
            if cycle:
                cycle = self._improve_cycle_with_insertion(cycle)

            # 4. Keep track of the best cycle found so far
            if len(cycle) > len(self.best_cycle):
                self.best_cycle = cycle
                # Don't print inside the loop for cleaner output, but can be useful for debugging
                # print(f"   - Iteration {iteration}: New best cycle found with length {len(self.best_cycle)}")
        
        print(f"   - Finished after {iteration} iterations.")
        if self.best_cycle:
            print(f"   - Longest cycle found has length {len(self.best_cycle)}.")
            return self.best_cycle
        else:
            print("   - No cycle was found.")
            return None

def parse_question_to_adj_list(question_data):
    """Converts a question from the JSON file into an adjacency list (dict of ints)."""
    adj_list = {}
    if not question_data:
        return adj_list
        
    for node_str, neighbors_list in question_data.items():
        adj_list[int(node_str)] = [int(n) for n in neighbors_list]
    
    return adj_list

def main():
    parser = argparse.ArgumentParser(description="Find the longest simple cycle in graphs from a JSON file and add ground truth values.")
    parser.add_argument(
        '--file', 
        type=str, 
        default='question.json', 
        help='Path to the JSON file containing graph problems.'
    )
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=0.01, 
        help='Timeout in seconds for the solver for each problem.'
    )
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
        print(f"--- [{i+1}/{total_questions}] Solving Longest Cycle for: {question_name} ---")
        
        adj_list = parse_question_to_adj_list(question_data)
        
        solver = LongestCycleSolver(adj_list, timeout=args.timeout)
        solution_path = solver.solve()
        
        # Add ground_truth field to the original question data
        if solution_path:
            question_data['ground_truth'] = len(solution_path)
        else:
            question_data['ground_truth'] = 0
        
        print(f"--- Finished {question_name} ---")
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