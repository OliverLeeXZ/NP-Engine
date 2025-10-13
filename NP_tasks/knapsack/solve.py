import json
import argparse
import time

class KnapsackSolver:
    """
    Solves the 0/1 Knapsack problem using Dynamic Programming to find the
    optimal solution.
    """

    def __init__(self, items, capacity):
        """
        Initializes the solver.

        Args:
            items (list): A list of item tuples, where each tuple is
                          (item_id, weight, value).
            capacity (int): The maximum capacity of the knapsack.
        """
        # We sort items by ID to ensure consistent processing, although not strictly
        # necessary for the DP algorithm itself.
        self.items = sorted(items, key=lambda x: x[0])
        self.capacity = int(capacity)
        self.num_items = len(self.items)

    def solve(self):
        """
        Calculates the optimal set of items to include in the knapsack.

        Returns:
            A tuple containing:
            - A list of the IDs of the selected items.
            - The maximum total value achieved.
            - The total weight of the selected items.
        """
        # dp[i][w] will be the maximum value that can be attained with
        # a knapsack of capacity w using only the first i items.
        dp = [[0 for _ in range(self.capacity + 1)] for _ in range(self.num_items + 1)]

        # Build table dp[][] in a bottom-up manner
        for i in range(1, self.num_items + 1):
            _item_id, item_weight, item_value = self.items[i - 1]

            for w in range(self.capacity + 1):
                if item_weight <= w:
                    # Decision: include the item or not
                    dp[i][w] = max(item_value + dp[i - 1][w - item_weight], dp[i - 1][w])
                else:
                    # Cannot include the current item
                    dp[i][w] = dp[i - 1][w]

        # --- Backtrack to find which items were included ---
        max_value = dp[self.num_items][self.capacity]
        selected_items_ids = []
        total_weight = 0
        w = self.capacity

        for i in range(self.num_items, 0, -1):
            # If the value is different from the row above, it means we included this item
            if w > 0 and dp[i][w] != dp[i - 1][w]:
                item_id, item_weight, item_value = self.items[i - 1]
                selected_items_ids.append(item_id)
                total_weight += item_weight
                w -= item_weight

        selected_items_ids.reverse() # Sort back to original order
        return selected_items_ids, max_value, total_weight

def parse_question_data(data):
    """Extracts capacity and items from the question JSON object."""
    capacity = data['capacity']
    items = []
    for item_id, details in data['items'].items():
        items.append((int(item_id), details['weight'], details['value']))
    return items, capacity

def main():
    parser = argparse.ArgumentParser(description="Solve Knapsack problems from a JSON file using Dynamic Programming and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with Knapsack problems.')
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
        print(f"--- [{i+1}/{total_questions}] Solving Knapsack for: {question_name} ---")
        
        items, capacity = parse_question_data(question_data)
        
        solver = KnapsackSolver(items, capacity)
        solution, value, weight = solver.solve()
        
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = value
        
        print(f"--- Finished {question_name}, Max Value: {value}, Total Weight: {weight}/{capacity} ---")
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