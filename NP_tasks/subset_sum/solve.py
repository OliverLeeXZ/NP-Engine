import json
import argparse
import time
import random

class SubsetSumSolver:
    """
    Solves the Subset Sum problem with the objective of maximizing the number
    of elements in the subset. This is solved optimally using Dynamic Programming,
    framing it as a variation of the 0/1 Knapsack problem.
    """
    def __init__(self, numbers, target):
        """
        Initializes the solver.

        Args:
            numbers (list): A list of (index, value) tuples.
            target (int): The target sum.
        """
        self.numbers = sorted(numbers, key=lambda x: x[0])
        self.target = target
        self.num_items = len(self.numbers)

    def solve(self):
        """
        Dispatches to the appropriate solver based on problem size.
        It prioritizes exact solvers and chooses the most efficient one based on
        the problem's characteristics (number of items vs. target value).
        """
        # For a small number of items, Meet-in-the-middle is generally most efficient.
        if self.num_items <= 40:
            # print("   - Using exact Meet-in-the-middle solver.")
            return self._solve_meet_in_the_middle()

        # For a larger number of items, DP is feasible if the target is not too large.
        if self.num_items * self.target <= 2 * 10**7:
            # print("   - Using exact DP solver.")
            return self._solve_dp()

        # If the problem is too large for any exact solver, we cannot guarantee an optimal solution.
        print("   - Problem size too large for any exact solver, no solution can be found.")
        return "No solution", 0

    def _get_subset_sums_max_cardinality(self, number_list):
        """
        Generates all possible subset sums for a given list of numbers,
        optimizing for maximum cardinality for each sum.

        Args:
            number_list: A list of (index, value) tuples.

        Returns:
            A dictionary mapping each possible sum to a tuple of
            (max_cardinality, list_of_indices).
            Example: {sum: (cardinality, [indices])}
        """
        sums = {0: (0, [])}  # Start with sum 0, cardinality 0, empty set
        for index, value in number_list:
            new_sums = {}
            for s, (card, indices) in sums.items():
                new_s = s + value
                new_card = card + 1
                
                # Check if this new sum is an improvement (either new or better cardinality)
                # We check against new_sums to handle cases where multiple items in number_list
                # could form the same new_s. We want the one with highest cardinality.
                if new_s not in sums or new_card > sums[new_s][0]:
                    if new_s not in new_sums or new_card > new_sums[new_s][0]:
                        new_sums[new_s] = (new_card, indices + [index])

            # Merge the improvements into the main sums dictionary
            for s, (card, indices) in new_sums.items():
                if s not in sums or card > sums[s][0]:
                    sums[s] = (card, indices)
        return sums

    def _solve_meet_in_the_middle(self):
        """
        Finds the optimal solution using the Meet-in-the-Middle algorithm.
        This approach is very efficient for a small number of items (e.g., N <= 40).
        """
        if self.target == 0:
            return [], 0

        # 1. Split the numbers into two halves
        mid_index = self.num_items // 2
        first_half = self.numbers[:mid_index]
        second_half = self.numbers[mid_index:]

        # 2. Generate all subset sums for both halves, optimized for max cardinality
        sums_a = self._get_subset_sums_max_cardinality(first_half)
        sums_b = self._get_subset_sums_max_cardinality(second_half)

        # 3. Meet in the middle to find the best combination
        best_cardinality = -1
        best_indices = []

        if self.target in sums_a:
            card, indices = sums_a[self.target]
            best_cardinality = card
            best_indices = indices

        if self.target in sums_b:
            card, indices = sums_b[self.target]
            if card > best_cardinality:
                best_cardinality = card
                best_indices = indices

        for s_a, (card_a, indices_a) in sums_a.items():
            needed_sum = self.target - s_a
            if needed_sum in sums_b:
                card_b, indices_b = sums_b[needed_sum]
                
                current_cardinality = card_a + card_b
                if current_cardinality > best_cardinality:
                    best_cardinality = current_cardinality
                    best_indices = indices_a + indices_b

        if best_cardinality == -1:
            return "No solution", 0
        
        return sorted(best_indices), best_cardinality

    def _solve_dp(self):
        """
        Calculates the optimal subset of numbers that sums to the target
        with the maximum possible number of elements, using Dynamic Programming.
        This implementation is written from scratch based on the problem description.

        Returns:
            A tuple containing:
            - A list of the indices of the selected numbers.
            - The number of elements in the solution subset.
            - "No solution" if no subset sums to the target.
        """
        # dp[i][j] will store the max number of items to get sum j using first i items.
        # Initialize with -1 to indicate "not reachable".
        dp = [[-1 for _ in range(self.target + 1)] for _ in range(self.num_items + 1)]

        # Base case: a sum of 0 is possible with 0 items.
        for i in range(self.num_items + 1):
            dp[i][0] = 0

        # Build the DP table row by row
        for i in range(1, self.num_items + 1):
            _index, num_value = self.numbers[i - 1]
            
            for j in range(1, self.target + 1):
                # Case 1: Don't include the current number (numbers[i-1]).
                # The max cardinality is the same as for the previous i-1 items.
                card_without = dp[i - 1][j]

                # Case 2: Include the current number.
                card_with = -1
                if j >= num_value and dp[i - 1][j - num_value] != -1:
                    card_with = dp[i - 1][j - num_value] + 1
                
                # dp[i][j] is the best we can do with the first i items for sum j.
                dp[i][j] = max(card_without, card_with)
        
        # --- Backtrack to find which numbers were included ---
        max_cardinality = dp[self.num_items][self.target]
        if max_cardinality == -1:
            return "No solution", 0

        selected_indices = []
        # Start from the bottom-right corner of the DP table
        j = self.target
        for i in range(self.num_items, 0, -1):
            _index, num_value = self.numbers[i - 1]
            
            # To reconstruct the path, we check if including the current item was
            # necessary to achieve the optimal cardinality at dp[i][j].
            # This is true if the value at dp[i][j] is different from the value
            # at dp[i-1][j] (the case where we didn't include the item).
            if dp[i][j] != dp[i-1][j]:
                selected_indices.append(_index)
                j -= num_value
        
        return sorted(selected_indices), max_cardinality

def parse_question_data(data):
    """Extracts target and numbers from the question JSON object."""
    target = data['target']
    numbers = []
    for index, value in data['numbers'].items():
        numbers.append((int(index), value))
    return numbers, target

def main():
    parser = argparse.ArgumentParser(description="Solve Subset Sum (Max Cardinality) problems from a JSON file and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with Subset Sum problems.')
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
        print(f"--- [{i+1}/{total_questions}] Solving Subset Sum for: {question_name} ---")
        
        numbers, target = parse_question_data(question_data)
        
        solver = SubsetSumSolver(numbers, target)
        solution, size = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = size

        if solution == "No solution":
            print(f"--- Finished {question_name}, No solution found ---")
        else:
            print(f"--- Finished {question_name}, Max Cardinality: {size} ---")
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