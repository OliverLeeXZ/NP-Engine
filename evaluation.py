from backend import query, batch_query
import argparse
import json
from NP_tasks.knapsack.validation import validation as knapsack_validation
from NP_tasks.GCP_D.validation import validation as GCP_D_validation
from NP_tasks.TSP.validation import validation as TSP_validation
from NP_tasks.hamiltonian_cycle.validation import validation as hamiltonian_cycle_validation
from NP_tasks.maximum_clique_problem.validation import validation as maximum_clique_validation
from NP_tasks.maximum_set.validation import validation as maximum_set_validation
from NP_tasks.meeting_schedule.validation import validation as meeting_schedule_validation
from NP_tasks.minimum_cut.validation import validation as minimum_cut_validation
from NP_tasks.set_cover.validation import validation as set_cover_validation
from NP_tasks.subset_sum.validation import validation as subset_sum_validation
import importlib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import numpy as np
import csv

def aggregate_and_save_csv(stats, output_filename):
    CATEGORY_MAP = {
        "selection": ["set-cover", "subset-sum", "knapsack"],
        "planning": ["TSP", "hamiltonian-cycle"],
        "graph": ["maximum_clique_problem", "maximum-set", "GCP-D"],
        "partition": ["minimum-cut"],
        "schedule": ["meeting-schedule"]
    }
    TASK_TO_CATEGORY = {task: category for category, tasks in CATEGORY_MAP.items() for task in tasks}
    CATEGORIES_ORDER = ["graph", "schedule", "partition", "selection", "planning"]

    category_data = defaultdict(lambda: defaultdict(lambda: {'rates': [], 'ratios': []}))

    for task_type, diff_dict in stats.items():
        category = TASK_TO_CATEGORY.get(task_type)
        if not category:
            continue
        for diff, v in diff_dict.items():
            problem_rate = v["problem_success"] / v["problem_total"] if v["problem_total"] > 0 else 0
            avg_ratio = v["avg_ratio"]
            category_data[diff][category]['rates'].append(problem_rate)
            category_data[diff][category]['ratios'].append(avg_ratio)

    csv_rows = []
    difficulties = sorted(category_data.keys(), key=lambda d: ['easy', 'medium', 'hard'].index(d) if d in ['easy', 'medium', 'hard'] else 99)

    for diff in difficulties:
        row = {'difficulty': diff}
        for category in CATEGORIES_ORDER:
            cat_rates = category_data[diff][category]['rates']
            cat_ratios = category_data[diff][category]['ratios']
            
            avg_rate = sum(cat_rates) / len(cat_rates) if cat_rates else 0
            avg_ratio = sum(cat_ratios) / len(cat_ratios) if cat_ratios else 0
            
            row[f'{category}_success_rate'] = f"{avg_rate:.4f}"
            row[f'{category}_avg_ratio'] = f"{avg_ratio:.4f}"
        csv_rows.append(row)

    if not csv_rows:
        print("没有可聚合的数据用于写入CSV。")
        return

    fieldnames = ['difficulty']
    for category in CATEGORIES_ORDER:
        fieldnames.append(f'{category}_success_rate')
        fieldnames.append(f'{category}_avg_ratio')

    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"聚合结果已保存至: {output_filename}")


def result_query(model, prompt, temperature, retries=3):
    """
    单条推理，兼容重试
    """
    completion_text = None
    for _ in range(retries):
        completion_text = query(
            system_message=prompt,
            user_message=None,
            model=model,
            temperature=temperature,
        )
        if completion_text:
            return completion_text
    print("Final plan attempt failed, giving up...")
    return completion_text  # type: ignore

def single_query(args, prompt, question, validation_fn):
    response = result_query(args.model, prompt, args.temperature)
    valid, value, msg = validation_fn(question, response)
    return valid, value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the task difficulty experiment.")
    parser.add_argument("--model", type=str, default="OliverLee/Qwen2.5-7B-NP", help="The model to use.")
    parser.add_argument("--temperature", type=float, default=0.7, help="The temperature to use.")
    parser.add_argument("--json_file", default= 'data/NP_Bench.json',type=str, help="The json file to use.")
    parser.add_argument("--steps", type=int, default=3, help="The steps to use.")
    parser.add_argument("--output_csv", type=str, default="aggregated_results.csv", help="聚合结果的CSV输出文件名")
    args = parser.parse_args()

    with open(args.json_file, "r") as f:
        data = json.load(f)
    items_iter = list(data.items())
    stats = {}
    validation_map = {
        "knapsack": knapsack_validation,
        "GCP-D": GCP_D_validation,
        "TSP": TSP_validation,
        "hamiltonian-cycle": hamiltonian_cycle_validation,
        "maximum_clique_problem": maximum_clique_validation,
        "maximum-set": maximum_set_validation,
        "meeting-schedule": meeting_schedule_validation,
        "minimum-cut": minimum_cut_validation,
        "set-cover": set_cover_validation,
        "subset-sum": subset_sum_validation,
    }
    small_tasks = ["GCP-D", "TSP", "minimum-cut", "set-cover"]

    tasks = []
    for key, item in items_iter:
        if "easy" in key:
            difficulty = "easy"
        elif "medium" in key:
            difficulty = "medium"
        elif "hard" in key:
            difficulty = "hard"
        elif "bench" in key:
            difficulty = "bench"
        else:
            continue
        prompt = item["prompt"]
        question = item["question"]
        task_type = item["task_type"]
        ground_truth = item.get("ground_truth")
        validation_fn = validation_map[task_type]
        for _ in range(args.steps):
            tasks.append((prompt, question, validation_fn, task_type, difficulty, ground_truth))

    stats = defaultdict(lambda: defaultdict(lambda: {
        "steps_success": 0,
        "steps_total": 0,
        "problem_success": 0,
        "problem_total": 0,
        "problem_results": [], 
        "avg_ratio": 0.0,
    }))
    MAX_WORKERS = 64 
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_task = {
            executor.submit(single_query, args, prompt, question, validation_fn): (task_type, difficulty, prompt, question, ground_truth)
            for prompt, question, validation_fn, task_type, difficulty, ground_truth in tasks
        }
        for future in tqdm(as_completed(future_to_task), total=len(future_to_task)):
            task_type, difficulty, prompt, question, ground_truth = future_to_task[future]
            valid, value = future.result()
            stats[task_type][difficulty]["steps_total"] += 1
            
            ratio = 0.0
            if not valid:  
                stats[task_type][difficulty]["steps_success"] += 1
                if ground_truth is not None and value is not None:
                    if task_type in small_tasks:
                        if value > 0:
                            ratio = ground_truth / value
                        elif value == 0:
                            ratio = 1.0 if ground_truth == 0 else float('inf')
                    else:
                        if ground_truth > 0:
                            ratio = value / ground_truth
                        elif ground_truth == 0:
                            ratio = 1.0 if value == 0 else float('inf')
            
            stats[task_type][difficulty]["problem_results"].append((prompt, question, ratio))

    print(f'{args.json_file} 统计完成')

    for task_type in stats:
        for difficulty in stats[task_type]:
            pq2ratios = defaultdict(list)
            for prompt, question, ratio in stats[task_type][difficulty]["problem_results"]:
                pq2ratios[(prompt, str(question))].append(ratio)
            
            if not pq2ratios:
                continue

            problem_total = len(pq2ratios)
            problem_success = sum(any(r > 0 for r in ratios) for ratios in pq2ratios.values())
            
            all_best_ratios = [max(ratios) for ratios in pq2ratios.values()]
            
            avg_ratio = sum(all_best_ratios) / problem_total if problem_total > 0 else 0
            problem_success = problem_success * 100
            avg_ratio = avg_ratio * 100
            stats[task_type][difficulty]["problem_total"] = problem_total
            stats[task_type][difficulty]["problem_success"] = problem_success
            stats[task_type][difficulty]["avg_ratio"] = avg_ratio

    print(f'{args.json_file} 统计完成')
    print(args.model)
    for task_type, diff_dict in stats.items():
        print(f"Task: {task_type}")
        for diff, v in diff_dict.items():
            steps_rate = v["steps_success"] / v["steps_total"] if v["steps_total"] else 0
            problem_rate = v["problem_success"] / v["problem_total"] if v["problem_total"] else 0
            print(
                f"  {diff}: \n"
                f"    - 题目数={v['problem_total']}, 成功题目数={v['problem_success']} (题目成功率={problem_rate:.1f})\n"
                f"    - steps总数={v['steps_total']}, 成功steps={v['steps_success']} (steps成功率={steps_rate:.1f})\n"
                f"    - ratio均值={v['avg_ratio']:.1f}"
            )
    
    model_name = args.model.replace("/", "_")
    aggregate_and_save_csv(stats, f"{model_name}_{args.output_csv}")