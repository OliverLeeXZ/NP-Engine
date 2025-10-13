import json
import argparse
import time
import random

class MaxCliqueSolver:
    """
    Finds a large clique in a graph using a greedy randomized heuristic
    with multiple restarts.
    """

    def __init__(self, adj_list, timeout=60):
        """
        Initializes the solver.

        Args:
            adj_list (dict): An adjacency list representation of the graph.
            timeout (int): The maximum time in seconds to spend on solving.
        """
        self.adj_list = {int(k): set(v) for k, v in adj_list.items()}
        self.nodes = sorted(self.adj_list.keys())
        self.num_vertices = len(self.nodes)
        self.timeout = timeout
        self.start_time = None
        self.best_clique = []

    def _get_common_neighbors(self, clique_nodes, candidate):
        """Finds neighbors of 'candidate' that are also connected to all nodes in 'clique_nodes'."""
        common = self.adj_list.get(candidate, set()).copy()
        for node in clique_nodes:
            common.intersection_update(self.adj_list.get(node, set()))
        return common

    def _construct_greedy_clique(self, start_node):
        """
        Constructs a clique starting from a given node using a smart
        greedy heuristic: choose the next node that maximizes the
        subsequent candidate set.
        """
        clique = [start_node]
        # Initial candidates are the neighbors of the start node
        candidates = self.adj_list.get(start_node, set()).copy()

        while candidates:
            best_candidate = -1
            max_future_candidates = -1

            # Find the best candidate to add to the clique
            for candidate in candidates:
                # Find how many nodes would remain as candidates if we add this one
                future_candidates = self._get_common_neighbors(clique, candidate)
                
                # The heuristic: pick the one that leaves the most options open
                if len(future_candidates) > max_future_candidates:
                    max_future_candidates = len(future_candidates)
                    best_candidate = candidate
            
            if best_candidate != -1:
                clique.append(best_candidate)
                # The new candidate set is the intersection of the old one
                # and the neighbors of the newly added node.
                candidates.intersection_update(self.adj_list.get(best_candidate, set()))
            else:
                # No candidate can extend the clique further
                break
        
        return clique

    def _local_search_phase(self, initial_clique):
        """
        Improves a given clique using a local search heuristic.
        It tries to swap a node in the clique with a node outside,
        and if the swap is successful, it tries to extend the new clique.
        """
        if not initial_clique:
            return []

        current_clique = set(initial_clique)

        while True:
            improvement_made = False
            
            nodes_in_clique = list(current_clique)
            random.shuffle(nodes_in_clique)

            for u in nodes_in_clique:
                clique_minus_u = current_clique - {u}
                
                nodes_outside = [n for n in self.nodes if n not in current_clique]
                random.shuffle(nodes_outside)

                for v in nodes_outside:
                    # Check if v can replace u (i.e., is connected to all other nodes)
                    if all(v in self.adj_list.get(node, set()) for node in clique_minus_u):
                        # The swap is valid. Now, can we extend this new clique?
                        swapped_clique = clique_minus_u | {v}
                        
                        # Find common neighbors of the new clique to extend it
                        if not swapped_clique: continue
                        
                        iter_swapped = iter(swapped_clique)
                        first_node = next(iter_swapped)
                        extensions = self.adj_list.get(first_node, set()).copy()

                        for node in iter_swapped:
                            extensions.intersection_update(self.adj_list.get(node, set()))
                        
                        extensions -= swapped_clique
                        
                        if extensions:
                            new_clique = swapped_clique | extensions
                            if len(new_clique) > len(current_clique):
                                current_clique = new_clique
                                improvement_made = True
                                break # from v loop
                
                if improvement_made:
                    break # from u loop
            
            if not improvement_made:
                break # No improvements in a full pass.

        return sorted(list(current_clique))

    def solve(self):
        """
        Repeatedly runs the greedy construction from random start nodes until timeout.
        """
        self.start_time = time.time()
        
        if not self.nodes:
            return []

        # For small graphs, we can try starting from all nodes.
        # For larger graphs, we rely on random sampling.
        nodes_to_try = self.nodes
        if self.num_vertices > 200:
             nodes_to_try = self.nodes[:] # Create a copy to shuffle
             random.shuffle(nodes_to_try)

        iteration = 0
        for start_node in nodes_to_try:
            iteration += 1
            if time.time() - self.start_time > self.timeout:
                print("   - Timeout reached.")
                break

            clique = self._construct_greedy_clique(start_node)
            clique = self._local_search_phase(clique)
            
            if len(clique) > len(self.best_clique):
                self.best_clique = clique
                print(f"   - Iteration {iteration}: New best clique found with size {len(self.best_clique)}")
        
        print(f"   - Finished after {iteration} iterations.")
        return self.best_clique

def parse_question_to_adj_list(question_data):
    adj_list = {}
    if not question_data: return adj_list
    for node_str, neighbors_list in question_data.items():
        adj_list[int(node_str)] = [int(n) for n in neighbors_list]
    return adj_list

def main():
    parser = argparse.ArgumentParser(description="Find large cliques in graphs from a JSON file and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with graph problems.')
    parser.add_argument('--timeout', type=int, default=1, help='Timeout in seconds for each problem.')
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
        print(f"--- [{i+1}/{total_questions}] Solving Max Clique for: {question_name} ---")
        
        adj_list = parse_question_to_adj_list(question_data)
        
        solver = MaxCliqueSolver(adj_list, timeout=args.timeout)
        solution_clique = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = len(solution_clique)
        
        print(f"--- Finished {question_name}, Max Clique Size Found: {len(solution_clique)} ---")
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