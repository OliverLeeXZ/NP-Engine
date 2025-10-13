import json
import argparse
import time
import random
import math

class SetCoverSolver:
    """
    Solves the Set Cover problem using Simulated Annealing, a powerful
    metaheuristic for finding high-quality approximate solutions.
    It uses a greedy algorithm to obtain a good initial solution.
    """
    def __init__(self, universe, subsets, timeout=60):
        """
        Initializes the solver.
        """
        self.universe = set(universe)
        self.subsets = {int(k): set(v) for k, v in subsets.items()}
        self.timeout = timeout
        self.start_time = None

    def _greedy_initial_solve(self):
        """
        Finds an initial solution using the standard greedy heuristic.
        """
        uncovered = self.universe.copy()
        cover = set()
        available_subsets = self.subsets.copy()

        while uncovered and available_subsets:
            # Find the subset that covers the most currently uncovered elements
            best_subset_id = max(
                available_subsets,
                key=lambda sid: len(uncovered.intersection(available_subsets[sid]))
            )
            cover.add(best_subset_id)
            uncovered -= available_subsets[best_subset_id]
            del available_subsets[best_subset_id]
        
        return cover

    def _remove_redundant_subsets(self, cover_set):
        """
        Greedily removes any redundant subsets from a given cover.
        A subset is redundant if its elements are all covered by other subsets in the cover.
        """
        current_cover = list(cover_set)
        random.shuffle(current_cover) # Randomize order to get different results
        
        best_cover = set(current_cover)

        for subset_id in current_cover:
            # Temporarily remove the subset
            temp_cover = best_cover - {subset_id}
            
            # Check if the universe is still covered without this subset
            covered_by_rest = set().union(*(self.subsets.get(sid, set()) for sid in temp_cover))
            
            if self.universe.issubset(covered_by_rest):
                # If it is, the subset was redundant, so we confirm its removal
                best_cover.remove(subset_id)
        
        return best_cover

    def solve(self):
        """
        Finds a small set cover using Simulated Annealing.
        """
        self.start_time = time.time()

        # 1. Pre-check: Verify if a solution is possible.
        union_of_all_subsets = set().union(*self.subsets.values())
        if not self.universe.issubset(union_of_all_subsets):
            return "Impossible", 0

        # 2. Get a good initial solution using the greedy algorithm
        print("   - Finding initial solution with greedy algorithm...")
        current_solution_set = self._greedy_initial_solve()
        
        # 2.5 Clean up the initial greedy solution
        current_solution_set = self._remove_redundant_subsets(current_solution_set)
        
        best_solution_set = current_solution_set.copy()
        print(f"   - Greedy solution size (after cleanup): {len(best_solution_set)}")

        # 3. Simulated Annealing Parameters
        T = 1.0
        T_min = 0.0001
        alpha = 0.995 # Slower cooling rate for more exploration
        
        print("   - Improving solution with Simulated Annealing...")
        iteration = 0
        while T > T_min and (time.time() - self.start_time) < self.timeout:
            iteration += 1
            
            # --- Generate a neighbor solution using one of two strategies ---
            neighbor_set = set()
            
            if random.random() < 0.6:
                # Strategy 1: "Shrink" (Remove and Repair) - More exploitative
                temp_set = current_solution_set.copy()
                if temp_set:
                    subset_to_remove = random.choice(list(temp_set))
                    temp_set.remove(subset_to_remove)
                
                # Repair the cover greedily
                uncovered_after_removal = self.universe - set().union(*(self.subsets.get(sid, set()) for sid in temp_set))
                
                # This repair logic can be a bit slow, let's simplify for speed
                # by reusing the greedy logic on the missing parts.
                if uncovered_after_removal:
                    # Find subsets that can help cover the remaining elements
                    available_for_repair = {
                        sid: elements for sid, elements in self.subsets.items()
                        if sid not in temp_set and not uncovered_after_removal.isdisjoint(elements)
                    }
                    while uncovered_after_removal and available_for_repair:
                        best_repair_subset = max(available_for_repair,
                            key=lambda sid: len(uncovered_after_removal.intersection(available_for_repair[sid])))
                        temp_set.add(best_repair_subset)
                        uncovered_after_removal -= available_for_repair[best_repair_subset]
                        del available_for_repair[best_repair_subset]
                
                neighbor_set = temp_set
            else:
                # Strategy 2: "Expand and Contract" - More explorative
                temp_set = current_solution_set.copy()
                unused_subsets = [sid for sid in self.subsets if sid not in temp_set]
                if unused_subsets:
                    subset_to_add = random.choice(unused_subsets)
                    temp_set.add(subset_to_add)
                    # Contract by removing redundancies
                    neighbor_set = self._remove_redundant_subsets(temp_set)

            # --- Evaluate the new neighbor solution ---
            if not neighbor_set:
                continue

            uncovered_elements = self.universe - set().union(*(self.subsets.get(sid, set()) for sid in neighbor_set))
            if uncovered_elements:
                continue

            cost_current = len(current_solution_set)
            cost_neighbor = len(neighbor_set)
            delta = cost_neighbor - cost_current

            # Acceptance probability
            if delta < 0 or (T > 0 and random.random() < math.exp(-delta / T)):
                current_solution_set = neighbor_set
                # Clean up the new current solution occasionally
                if random.random() < 0.1:
                    current_solution_set = self._remove_redundant_subsets(current_solution_set)

                if len(current_solution_set) < len(best_solution_set):
                    best_solution_set = current_solution_set.copy()
                    print(f"   - Iteration {iteration}: New best solution found with size {len(best_solution_set)}")
            
            T *= alpha
        
        # Final cleanup of the best solution found
        best_solution_set = self._remove_redundant_subsets(best_solution_set)
        print(f"   - Finished after {iteration} iterations.")
        return sorted(list(best_solution_set)), len(best_solution_set)

def parse_question_data(data):
    """Extracts universe and subsets from the question JSON object."""
    # Ensure universe elements are integers if they are numeric strings
    universe = [int(e) if str(e).isdigit() else e for e in data['U']]
    subsets = {int(k): v for k, v in data['S'].items()}
    return universe, subsets

def main():
    parser = argparse.ArgumentParser(description="Solve Set Cover problems from a JSON file using Simulated Annealing and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with Set Cover problems.')
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
    
    start_time = time.time()
    for i, (question_name, question_data) in enumerate(sorted(questions.items())):
        print(f"--- [{i+1}/{total_questions}] Solving Set Cover for: {question_name} ---")
        
        universe, subsets = parse_question_data(question_data)
        
        solver = SetCoverSolver(universe, subsets, timeout=args.timeout)
        solution, size = solver.solve()
        
        # Add ground_truth field to the original question data
        if solution == "Impossible":
            question_data['ground_truth'] = -1
        else:
            question_data['ground_truth'] = size
        
        if solution == "Impossible":
            print(f"--- Finished {question_name}, No valid cover found ---")
        else:
            print(f"--- Finished {question_name}, Cover Size: {size} ---")
        print("-" * 50)

    # Save the modified data back to the original file
    try:
        with open(args.file, 'w') as f:
            json.dump(data, f, indent=2)
        total_time = time.time() - start_time
        print(f"\nSuccessfully processed all {total_questions} problems in {total_time:.2f} seconds.")
        print(f"All solutions have been added to '{args.file}' with ground_truth fields.")
    except IOError as e:
        print(f"\nError writing solutions to file: {e}")

if __name__ == '__main__':
    main() 