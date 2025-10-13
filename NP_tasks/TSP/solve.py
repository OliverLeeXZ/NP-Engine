import json
import time
import numpy as np
import argparse
from itertools import combinations
import random

class TSP_Solver:
    """
    A solver for the Traveling Salesperson Problem (TSP) using a combination of
    Nearest Neighbor heuristic for the initial tour and 2-opt for optimization.
    """

    def __init__(self, dist_matrix, timeout=60):
        """
        Initializes the solver.

        Args:
            dist_matrix (np.ndarray): A square matrix where dist_matrix[i, j] is the distance
                                      between city i and city j.
            timeout (int): The maximum time in seconds to spend on solving.
        """
        self.dist_matrix = dist_matrix
        self.num_cities = dist_matrix.shape[0]
        self.timeout = timeout
        self.start_time = None

    def _calculate_tour_distance(self, tour):
        """Calculates the total distance of a given tour."""
        total_distance = 0
        for i in range(self.num_cities):
            u = tour[i]
            v = tour[(i + 1) % self.num_cities]
            total_distance += self.dist_matrix[u, v]
        return total_distance

    def _nearest_neighbor_initial_tour(self):
        """
        Generates an initial tour using the Nearest Neighbor heuristic.
        Tries starting from every city and returns the best tour found.
        """
        best_initial_tour = []
        min_tour_distance = float('inf')

        for start_node in range(self.num_cities):
            tour = [start_node]
            unvisited = set(range(self.num_cities))
            unvisited.remove(start_node)
            current_node = start_node

            while unvisited:
                nearest_node = min(unvisited, key=lambda node: self.dist_matrix[current_node, node])
                unvisited.remove(nearest_node)
                tour.append(nearest_node)
                current_node = nearest_node
            
            tour_distance = self._calculate_tour_distance(tour)
            if tour_distance < min_tour_distance:
                min_tour_distance = tour_distance
                best_initial_tour = tour

        return best_initial_tour, min_tour_distance

    def _run_deterministic_2opt(self, initial_tour):
        """Improves a tour using the deterministic 2-opt local search (best improvement)."""
        best_tour = list(initial_tour)
        best_distance = self._calculate_tour_distance(best_tour)
        
        improved = True
        while improved:
            if time.time() - self.start_time > self.timeout:
                break
                
            improved = False
            best_delta = 0
            best_swap = None

            for i in range(self.num_cities - 1):
                for j in range(i + 2, self.num_cities):
                    u1, v1 = best_tour[i], best_tour[i + 1]
                    u2, v2 = best_tour[j], best_tour[(j + 1) % self.num_cities]

                    delta = (self.dist_matrix[u1, u2] + self.dist_matrix[v1, v2]) - \
                            (self.dist_matrix[u1, v1] + self.dist_matrix[u2, v2])

                    if delta < best_delta:
                        best_delta = delta
                        best_swap = (i, j)

            if best_swap:
                i, j = best_swap
                segment = best_tour[i + 1 : j + 1]
                segment.reverse()
                best_tour[i + 1 : j + 1] = segment
                best_distance += best_delta
                improved = True
                
        return best_tour, best_distance

    def _run_sa_with_2opt(self, initial_tour):
        """
        Explores the solution space using Simulated Annealing with a 2-opt neighborhood.
        """
        current_tour = list(initial_tour)
        current_distance = self._calculate_tour_distance(current_tour)
        
        best_tour = current_tour
        best_distance = current_distance

        # SA Parameters
        initial_temp = best_distance / 10 
        cooling_rate = 0.9999
        temp = initial_temp

        # Use a fixed number of iterations for the main loop
        max_iterations = 20000 

        for i in range(max_iterations):
            if time.time() - self.start_time > self.timeout:
                # print("   - Timeout reached during SA optimization.")
                break
            
            # Generate a random 2-opt move
            i, j = sorted(random.sample(range(self.num_cities), 2))
            
            if i == 0 and j == self.num_cities - 1: continue

            # Nodes involved in the swap
            u1, v1 = current_tour[i-1], current_tour[i]
            u2, v2 = current_tour[j], current_tour[(j + 1) % self.num_cities]

            # Calculate change in distance (delta)
            delta = (self.dist_matrix[u1, u2] + self.dist_matrix[v1, v2]) - \
                    (self.dist_matrix[u1, v1] + self.dist_matrix[u2, v2])

            # SA acceptance criteria
            if delta < 0 or (temp > 0 and random.random() < np.exp(-delta / temp)):
                # Accept the move: reverse the segment
                # The previous slice-based reversal was buggy for i=0.
                # This is a more robust way to reverse the segment.
                segment = current_tour[i : j + 1]
                segment.reverse()
                current_tour[i : j + 1] = segment
                current_distance += delta
                
                # Update the best-ever tour if the new one is better
                if current_distance < best_distance:
                    best_distance = current_distance
                    best_tour = list(current_tour)
            
            # Cool down
            temp *= cooling_rate
            
        return best_tour, best_distance

    def solve(self):
        """
        Solves the TSP instance using a hybrid approach:
        1. Nearest Neighbor for a good initial solution.
        2. Simulated Annealing for global search to escape local optima.
        3. Deterministic 2-opt to polish the final solution.
        """
        self.start_time = time.time()
        
        print("1. Generating initial tour using Nearest Neighbor heuristic...")
        initial_tour, initial_distance = self._nearest_neighbor_initial_tour()
        print(f"   - Initial tour distance: {initial_distance}")

        print("2. Exploring solution space with Simulated Annealing...")
        sa_tour, sa_distance = self._run_sa_with_2opt(initial_tour)
        print(f"   - Tour distance after SA: {sa_distance}")

        print("3. Polishing final tour with deterministic 2-opt...")
        final_tour, final_distance = self._run_deterministic_2opt(sa_tour)
        print(f"   - Final optimized tour distance: {final_distance}")
        
        elapsed_time = time.time() - self.start_time
        print(f"\nFinished in {elapsed_time:.2f} seconds.")
        
        return final_tour, final_distance

def parse_question_to_matrix(question_data):
    """Converts a question from the JSON file into a NumPy distance matrix."""
    cities = sorted([int(c) for c in question_data.keys()])
    num_cities = len(cities)
    dist_matrix = np.zeros((num_cities, num_cities))

    for i in range(num_cities):
        city_i_str = str(cities[i])
        for j in range(num_cities):
            city_j_str = str(cities[j])
            if i == j:
                continue
            dist_matrix[i, j] = question_data[city_i_str][city_j_str]
            
    return dist_matrix

def main():
    parser = argparse.ArgumentParser(description="Solve all TSP problems from a JSON file and add ground truth values.")
    parser.add_argument(
        '--file', 
        type=str, 
        default='extreme_5.json', 
        help='Path to the JSON file containing TSP problems.'
    )
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=1, 
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
    
    # Using sorted() to process questions in a consistent order (e.g., question1, question2, ...)
    for i, (question_name, question_data) in enumerate(sorted(questions.items())):
        print(f"--- [{i+1}/{total_questions}] Solving TSP for: {question_name} ---")
        
        dist_matrix = parse_question_to_matrix(question_data)
        
        solver = TSP_Solver(dist_matrix, timeout=args.timeout)
        best_tour, best_distance = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = best_distance
        
        print(f"--- Finished {question_name}, Best Distance: {best_distance} ---")
        print("-" * 50)

    # Save the modified data back to the original file
    try:
        with open(args.file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSuccessfully solved all {total_questions} problems.")
        print(f"All solutions have been added to '{args.file}' with ground_truth fields.")
    except IOError as e:
        print(f"\nError writing solutions to file: {e}")


if __name__ == '__main__':
    main() 