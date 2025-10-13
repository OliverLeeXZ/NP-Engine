#!/usr/bin/env python3
"""
基于规则的0/1背包问题（Knapsack Problem）造题脚本
"""

import json
import random
import argparse
from typing import Dict, List, Tuple

def save_json_compact(data, filename):
    """
    使用自定义的紧凑格式保存JSON文件。
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('{\n')
        f.write(f'  "big_small": "{data["big_small"]}",\n')
        f.write('  "questions": {\n')
        
        question_items = []
        
        # 自定义排序：easy -> medium -> hard
        def sort_key(q_key):
            if q_key.startswith('easy_'):
                return (0, int(q_key.replace('easy_question', '')))
            elif q_key.startswith('medium_'):
                return (1, int(q_key.replace('medium_question', '')))
            elif q_key.startswith('hard_'):
                return (2, int(q_key.replace('hard_question', '')))
            elif q_key.startswith('bench_'):
                return (3, int(q_key.replace('bench_question', '')))
            else:
                # 兼容其他格式
                return (4, int(q_key.replace('question', '')))
        
        sorted_q_keys = sorted(data["questions"].keys(), key=sort_key)
        
        for i, q_key in enumerate(sorted_q_keys):
            q_data = data["questions"][q_key]
            lines = [f'    "{q_key}": {{']
            lines.append(f'      "capacity": {q_data["capacity"]},')
            lines.append(f'      "items": {{')

            item_lines = []
            sorted_item_keys = sorted(q_data["items"].keys(), key=int)
            for j, item_key in enumerate(sorted_item_keys):
                item = q_data["items"][item_key]
                item_line = f'        "{item_key}": {{"weight": {item["weight"]}, "value": {item["value"]}}}'
                if j < len(sorted_item_keys) - 1:
                    item_line += ','
                item_lines.append(item_line)

            lines.append('\n'.join(item_lines))
            lines.append('      }')
            lines.append('    }')
            question_item = '\n'.join(lines)
            if i < len(sorted_q_keys) - 1:
                question_item += ','
            question_items.append(question_item)
            
        f.write('\n'.join(question_items))
        f.write('\n  }\n}\n')

class KnapsackGenerator:
    """背包问题生成器"""

    def __init__(self, params: Dict):
        self.p = params

    def generate_single_question(self) -> Tuple[Dict, List[int]]:
        """
        生成单个背包问题，并确保有解。
        方法：先确定一个要放入背包的物品集合，然后围绕它设定总容量和干扰项。
        """
        num_solution_items = random.randint(*self.p["num_solution_items"])
        num_total_items = num_solution_items + random.randint(*self.p["num_distractor_items"])
        
        all_item_ids = list(range(num_total_items))
        random.shuffle(all_item_ids)
        
        solution_ids = sorted(all_item_ids[:num_solution_items])
        distractor_ids = all_item_ids[num_solution_items:]
        
        items = {}
        total_solution_weight = 0
        
        # 1. 生成解集物品
        for item_id in solution_ids:
            w_range = self.p["solution_weight_range"]
            v_ratio = self.p["solution_value_ratio"]
            weight = random.randint(*w_range)
            # 让价值与重量相关，但有一定浮动
            value = int(weight * (random.uniform(*v_ratio)))
            items[str(item_id)] = {"weight": weight, "value": value}
            total_solution_weight += weight
            
        # 2. 生成干扰物品
        for item_id in distractor_ids:
            category = random.choices(["heavy", "cheap", "trap"], [0.4, 0.4, 0.2], k=1)[0]
            if category == "heavy": # 重量大，价值低
                w_range = self.p["distractor_heavy_weight_range"]
                v_ratio = self.p["distractor_cheap_value_ratio"]
                weight = random.randint(*w_range)
                value = int(weight * random.uniform(*v_ratio))
            elif category == "cheap": # 重量小，价值更低
                w_range = self.p["distractor_cheap_weight_range"]
                v_ratio = self.p["distractor_cheap_value_ratio"]
                weight = random.randint(*w_range)
                value = int(weight * random.uniform(*v_ratio))
            else: # trap: 高价值，但重量也极高
                w_range = self.p["distractor_trap_weight_range"]
                v_ratio = self.p["solution_value_ratio"] # 价值率可能很高
                weight = random.randint(int(total_solution_weight * 0.5), int(total_solution_weight * 0.9))
                value = int(weight * random.uniform(*v_ratio))
            items[str(item_id)] = {"weight": weight, "value": value}
            
        # 3. 设置总容量
        c_ratio = self.p["capacity_ratio_vs_solution"]
        capacity = int(total_solution_weight * random.uniform(*c_ratio))

        problem = {"capacity": capacity, "items": items}
        return problem, solution_ids

    def get_difficulty_params(self, difficulty: str) -> Dict:
        """获取指定难度的参数"""
        if difficulty == "easy":
            return {
                "num_solution_items": (6, 10), "num_distractor_items": (8, 15),
                "solution_weight_range": (5, 25), "solution_value_ratio": (1.8, 2.5),
                "distractor_heavy_weight_range": (30, 50), "distractor_cheap_weight_range": (2, 10),
                "distractor_cheap_value_ratio": (0.3, 0.8), "distractor_trap_weight_range": (40, 80),
                "capacity_ratio_vs_solution": (1.1, 1.4)
            }
        elif difficulty == "medium":
            return {
                "num_solution_items": (8, 12), "num_distractor_items": (15, 25),
                "solution_weight_range": (20, 80), "solution_value_ratio": (1.5, 2.0),
                "distractor_heavy_weight_range": (100, 200), "distractor_cheap_weight_range": (10, 40),
                "distractor_cheap_value_ratio": (0.6, 1.0), "distractor_trap_weight_range": (150, 300),
                "capacity_ratio_vs_solution": (1.05, 1.25)
            }
        elif difficulty == "hard":
            return {
                "num_solution_items": (15, 25), "num_distractor_items": (20, 35),
                "solution_weight_range": (50, 200), "solution_value_ratio": (1.2, 1.6),
                "distractor_heavy_weight_range": (300, 600), "distractor_cheap_weight_range": (30, 100),
                "distractor_cheap_value_ratio": (0.8, 1.1), "distractor_trap_weight_range": (400, 800),
                "capacity_ratio_vs_solution": (1.02, 1.15)
            }
        elif difficulty == "bench":
            return {
                "num_solution_items": (25, 35), "num_distractor_items": (30, 45),
                "solution_weight_range": (50, 200), "solution_value_ratio": (1.2, 1.6),
                "distractor_heavy_weight_range": (300, 600), "distractor_cheap_weight_range": (30, 100),
                "distractor_cheap_value_ratio": (0.8, 1.1), "distractor_trap_weight_range": (400, 800),
                "capacity_ratio_vs_solution": (1.02, 1.15)
            }
        else:
            raise ValueError(f"未知难度: {difficulty}")

    def generate_questions_by_difficulty(self, num_questions: int, difficulty: str, prefix: str = "") -> Tuple[Dict, Dict]:
        """生成指定数量和难度的问题集"""
        self.p = self.get_difficulty_params(difficulty)
            
        questions, answers = {}, {}
        for i in range(1, num_questions + 1):
            # print(f"生成第 {i}/{num_questions} 题 (难度: {difficulty})...")
            problem, answer = self.generate_single_question()
            question_key = f"{prefix}question{i}" if prefix else f"question{i}"
            questions[question_key] = problem
            answers[question_key] = answer
            
        return questions, answers

    def generate_mixed_questions(self, easy_num: int, medium_num: int, hard_num: int, bench_num: int = 0) -> Dict:
        """生成混合难度的问题集，顺序为easy->medium->hard->bench"""
        all_questions, all_answers = {}, {}
        total_items = 0
        total_questions = 0
        
        # 生成easy题目
        if easy_num > 0:
            print(f"\n=== 生成 {easy_num} 道简单题目 ===")
            easy_q, easy_a = self.generate_questions_by_difficulty(easy_num, "easy", "easy_")
            # 按顺序添加easy题目
            for i in range(1, easy_num + 1):
                key = f"easy_question{i}"
                all_questions[key] = easy_q[key]
                all_answers[key] = easy_a[key]
            total_items += sum(len(q["items"]) for q in easy_q.values())
            total_questions += easy_num
        
        # 生成medium题目
        if medium_num > 0:
            print(f"\n=== 生成 {medium_num} 道中等题目 ===")
            medium_q, medium_a = self.generate_questions_by_difficulty(medium_num, "medium", "medium_")
            # 按顺序添加medium题目
            for i in range(1, medium_num + 1):
                key = f"medium_question{i}"
                all_questions[key] = medium_q[key]
                all_answers[key] = medium_a[key]
            total_items += sum(len(q["items"]) for q in medium_q.values())
            total_questions += medium_num
        
        # 生成hard题目
        if hard_num > 0:
            print(f"\n=== 生成 {hard_num} 道困难题目 ===")
            hard_q, hard_a = self.generate_questions_by_difficulty(hard_num, "hard", "hard_")
            # 按顺序添加hard题目
            for i in range(1, hard_num + 1):
                key = f"hard_question{i}"
                all_questions[key] = hard_q[key]
                all_answers[key] = hard_a[key]
            total_items += sum(len(q["items"]) for q in hard_q.values())
            total_questions += hard_num
            
        # 生成bench题目
        if bench_num > 0:
            print(f"\n=== 生成 {bench_num} 道基准题目 ===")
            bench_q, bench_a = self.generate_questions_by_difficulty(bench_num, "bench", "bench_")
            # 按顺序添加bench题目
            for i in range(1, bench_num + 1):
                key = f"bench_question{i}"
                all_questions[key] = bench_q[key]
                all_answers[key] = bench_a[key]
            total_items += sum(len(q["items"]) for q in bench_q.values())
            total_questions += bench_num
            
        avg_items = total_items / total_questions if total_questions > 0 else 0
        big_small = "big"
        
        return {
            "big_small": big_small, 
            "questions": all_questions, 
            "answers": all_answers,
            "metadata": {
                "easy_count": easy_num,
                "medium_count": medium_num, 
                "hard_count": hard_num,
                "bench_count": bench_num,
                "total_questions": total_questions,
                "avg_items": avg_items
            }
        }

def main():
    parser = argparse.ArgumentParser(description='生成0/1背包问题数据集')
    parser.add_argument('--easy', type=int, default=0, help='生成简单题目数量')
    parser.add_argument('--medium', type=int, default=0, help='生成中等题目数量')
    parser.add_argument('--hard', type=int, default=0, help='生成困难题目数量')
    parser.add_argument('--bench', type=int, default=0, help='生成基准题目数量')
    parser.add_argument('--output', type=str, default='generated_knapsack_questions.json', help='输出文件名')
    parser.add_argument('--separate', action='store_true', help='是否为每种难度生成单独的文件')
    args = parser.parse_args()

    # 检查参数
    if args.easy + args.medium + args.hard + args.bench == 0:
        print("错误: 至少需要指定一种难度的题目数量 > 0")
        print("例如: python generate_questions.py --easy 5 --medium 3 --hard 2 --bench 1")
        return

    generator = KnapsackGenerator({})
    
    if args.separate:
        # 为每种难度生成单独文件
        if args.easy > 0:
            print(f"\n=== 生成 {args.easy} 道简单题目到单独文件 ===")
            easy_data = generator.generate_mixed_questions(args.easy, 0, 0, 0)
            easy_output = args.output.replace('.json', '_easy.json')
            output_data = {"big_small": easy_data["big_small"], "questions": easy_data["questions"]}
            save_json_compact(output_data, easy_output)
            print(f"简单题目文件: {easy_output}")
            
        if args.medium > 0:
            print(f"\n=== 生成 {args.medium} 道中等题目到单独文件 ===")
            medium_data = generator.generate_mixed_questions(0, args.medium, 0, 0)
            medium_output = args.output.replace('.json', '_medium.json')
            output_data = {"big_small": medium_data["big_small"], "questions": medium_data["questions"]}
            save_json_compact(output_data, medium_output)
            print(f"中等题目文件: {medium_output}")
            
        if args.hard > 0:
            print(f"\n=== 生成 {args.hard} 道困难题目到单独文件 ===")
            hard_data = generator.generate_mixed_questions(0, 0, args.hard, 0)
            hard_output = args.output.replace('.json', '_hard.json')
            output_data = {"big_small": hard_data["big_small"], "questions": hard_data["questions"]}
            save_json_compact(output_data, hard_output)
            print(f"困难题目文件: {hard_output}")
            
        if args.bench > 0:
            print(f"\n=== 生成 {args.bench} 道基准题目到单独文件 ===")
            bench_data = generator.generate_mixed_questions(0, 0, 0, args.bench)
            bench_output = args.output.replace('.json', '_bench.json')
            output_data = {"big_small": bench_data["big_small"], "questions": bench_data["questions"]}
            save_json_compact(output_data, bench_output)
            print(f"基准题目文件: {bench_output}")
    else:
        # 生成混合文件
        dataset = generator.generate_mixed_questions(args.easy, args.medium, args.hard, args.bench)
        
        output_data = {"big_small": dataset["big_small"], "questions": dataset["questions"]}
        save_json_compact(output_data, args.output)
        
        answer_file = args.output.replace('.json', '_with_answers.json')
        with open(answer_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
            
        print(f"\n生成完成!")
        print(f"题目文件: {args.output}")
        print(f"答案文件: {answer_file}")
        print(f"简单题目: {dataset['metadata']['easy_count']} 道")
        print(f"中等题目: {dataset['metadata']['medium_count']} 道")
        print(f"困难题目: {dataset['metadata']['hard_count']} 道")
        print(f"基准题目: {dataset['metadata']['bench_count']} 道")
        print(f"总题目数: {dataset['metadata']['total_questions']} 道")
        print(f"平均物品数: {dataset['metadata']['avg_items']:.1f}")

if __name__ == "__main__":
    main() 