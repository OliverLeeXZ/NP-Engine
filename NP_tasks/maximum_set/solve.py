import json
import argparse
import time
import random

def compute_complement_graph(adj_list):
    """Computes the complement of a graph given in adjacency list format."""
    nodes = sorted(adj_list.keys())
    num_vertices = len(nodes)
    complement_adj = {node: [] for node in nodes}

    # Create a set representation for faster lookups
    adj_set = {node: set(neighbors) for node, neighbors in adj_list.items()}

    for i in range(num_vertices):
        u = nodes[i]
        for j in range(i + 1, num_vertices):
            v = nodes[j]
            # If there is no edge between u and v in the original graph, add one in the complement.
            if v not in adj_set.get(u, set()):
                complement_adj[u].append(v)
                complement_adj[v].append(u)
    return complement_adj

class MaxIndependentSetSolver:
    """
    Finds a large Independent Set in a graph.
    This is achieved by finding the Maximum Clique in the complement graph.
    The algorithm uses a greedy randomized heuristic with multiple restarts.
    """

    def __init__(self, adj_list, timeout=60):
        """
        Initializes the solver.
        """
        print("   - Computing complement graph...")
        self.complement_adj_list = {int(k): set(v) for k, v in compute_complement_graph(adj_list).items()}
        self.nodes = sorted(self.complement_adj_list.keys())
        self.num_vertices = len(self.nodes)
        self.timeout = timeout
        self.start_time = None
        self.best_clique_in_complement = [] # This will be the MIS in the original graph

    def _get_common_neighbors(self, clique_nodes, candidate):
        """Finds neighbors of 'candidate' in the complement graph that are also
           connected to all nodes in 'clique_nodes'."""
        common = self.complement_adj_list.get(candidate, set()).copy()
        for node in clique_nodes:
            common.intersection_update(self.complement_adj_list.get(node, set()))
        return common

    def _construct_greedy_clique(self, start_node):
        """
        Constructs a clique in the complement graph (which is an independent set
        in the original graph) using a smart greedy heuristic.
        """
        clique = [start_node]
        candidates = self.complement_adj_list.get(start_node, set()).copy()

        while candidates:
            best_candidate = -1
            max_future_candidates = -1

            for candidate in candidates:
                future_candidates = self._get_common_neighbors(clique, candidate)
                if len(future_candidates) > max_future_candidates:
                    max_future_candidates = len(future_candidates)
                    best_candidate = candidate
            
            if best_candidate != -1:
                clique.append(best_candidate)
                candidates.intersection_update(self.complement_adj_list.get(best_candidate, set()))
            else:
                break
        
        return clique

    def _local_search_phase(self, initial_clique):
        """
        Improves a given clique in the complement graph using a local search heuristic.
        This is the same logic used in the Maximum Clique solver.
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
                    # Check if v can replace u
                    if all(v in self.complement_adj_list.get(node, set()) for node in clique_minus_u):
                        swapped_clique = clique_minus_u | {v}
                        
                        # Check if this new clique can be extended
                        if not swapped_clique: continue
                        
                        iter_swapped = iter(swapped_clique)
                        first_node = next(iter_swapped)
                        extensions = self.complement_adj_list.get(first_node, set()).copy()

                        for node in iter_swapped:
                            extensions.intersection_update(self.complement_adj_list.get(node, set()))
                        
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
                break

        return sorted(list(current_clique))

    def solve(self):
        """
        Repeatedly runs the greedy construction on the complement graph.
        """
        self.start_time = time.time()
        
        if not self.nodes:
            return []
        
        nodes_to_try = self.nodes[:]
        random.shuffle(nodes_to_try)

        iteration = 0
        for start_node in nodes_to_try:
            iteration += 1
            if time.time() - self.start_time > self.timeout:
                print("   - Timeout reached.")
                break

            # Find a clique in the complement graph
            clique = self._construct_greedy_clique(start_node)
            
            # Improve the clique using local search
            clique = self._local_search_phase(clique)
            
            if len(clique) > len(self.best_clique_in_complement):
                self.best_clique_in_complement = clique
                # print(f"   - Iteration {iteration}: New best independent set found with size {len(self.best_clique_in_complement)}")
        
        print(f"   - Finished after {iteration} iterations.")
        return self.best_clique_in_complement

def parse_question_to_adj_list(question_data):
    adj_list = {}
    if not question_data: return adj_list
    
    all_nodes = set()
    parsed_data = {}
    for node_str, neighbors_list in question_data.items():
        node = int(node_str)
        neighbors = [int(n) for n in neighbors_list]
        parsed_data[node] = neighbors
        all_nodes.add(node)
        all_nodes.update(neighbors)
    
    # Ensure adj_list has an entry for every node from 0 to max_node.
    max_node = max(all_nodes) if all_nodes else -1
    for i in range(max_node + 1):
        adj_list[i] = parsed_data.get(i, [])

    return adj_list

def main():
    parser = argparse.ArgumentParser(description="Find large independent sets in graphs from a JSON file and add ground truth values.")
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
        print(f"--- [{i+1}/{total_questions}] Solving Max Independent Set for: {question_name} ---")
        
        adj_list = parse_question_to_adj_list(question_data)
        
        solver = MaxIndependentSetSolver(adj_list, timeout=args.timeout)
        solution_set = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = len(solution_set)
        
        print(f"--- Finished {question_name}, Max Independent Set Size Found: {len(solution_set)} ---")
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