#!/usr/bin/env python3
"""
基于规则的子集和问题（Subset Sum Problem）造题脚本
特定变体：找到和为T的、包含元素数量最多的子集
支持混合难度生成：可以同时生成不同难度的题目
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
        f.write('{' + '\n')
        f.write(f'  "big_small": "{data["big_small"]}",' + '\n')
        f.write('  "questions": {' + '\n')
        
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
            question = data["questions"][q_key]
            lines = [f'    "{q_key}": {{']
            
            lines.append(f'      "target": {question["target"]},')
            
            num_dict_str = ", ".join([f'"{k}": {v}' for k, v in question["numbers"].items()])
            lines.append(f'      "numbers": {{ {num_dict_str} }}')
            
            lines.append('    }')
            question_item = '\n'.join(lines)
            if i < len(sorted_q_keys) - 1:
                question_item += ','
            question_items.append(question_item)
        
        f.write('\n'.join(question_items))
        f.write('\n  }\n}\n')

class SubsetSumGenerator:
    """子集和问题生成器"""

    def __init__(self,
                 total_numbers_range: Tuple[int, int] = (10, 20),
                 solution_size_range: Tuple[int, int] = (3, 5),
                 value_range: Tuple[int, int] = (1, 50)):
        """
        初始化生成器
        
        Args:
            total_numbers_range: 问题中数字总数的范围
            solution_size_range: 解集中数字数量的范围
            value_range: 数字本身的数值范围
        """
        self.total_numbers_range = total_numbers_range
        self.solution_size_range = solution_size_range
        self.value_range = value_range
        self.current_difficulty = None

    def _generate_solution_with_sum(self, target_sum: int, solution_size: int, low: int, high: int, max_attempts: int = 200) -> List[int]:
        """在区间[low, high]内生成一个长度为solution_size且和为target_sum的列表"""
        if solution_size <= 0:
            return []
        for _ in range(max_attempts):
            # 先随机生成，再微调到目标和
            vals = [random.randint(low, high) for _ in range(solution_size)]
            s = sum(vals)
            diff = target_sum - s
            # 通过随机调节若干次来逼近目标
            adjust_attempts = 0
            while diff != 0 and adjust_attempts < 500:
                idx = random.randrange(solution_size)
                if diff > 0:
                    inc = min(diff, high - vals[idx])
                    if inc <= 0:
                        adjust_attempts += 1
                        continue
                    vals[idx] += inc
                    diff -= inc
                else:
                    dec = min(-diff, vals[idx] - low)
                    if dec <= 0:
                        adjust_attempts += 1
                        continue
                    vals[idx] -= dec
                    diff += dec
                adjust_attempts += 1
            if sum(vals) == target_sum and all(low <= v <= high for v in vals):
                return vals
        # 失败回退：均匀拆分
        base = target_sum // solution_size
        rem = target_sum % solution_size
        vals = [base] * solution_size
        for i in range(rem):
            vals[i] += 1
        if all(low <= v <= high for v in vals):
            return vals
        raise ValueError("无法在给定范围内生成满足和的解列表")

    def generate_single_question(self) -> Tuple[Dict, List[List[int]]]:
        """
        生成单个子集和问题，并确保存在多个最优解（如果可能）。
        返回：problem, answers_index_sets（多个索引集合）
        """
        num_total = random.randint(*self.total_numbers_range)
        num_solution = random.randint(*self.solution_size_range)
        # 按难度确定目标多解数量范围
        if self.current_difficulty == "easy":
            desired_min, desired_max = 2, 3
        elif self.current_difficulty == "medium":
            desired_min, desired_max = 3, 4
        elif self.current_difficulty == "hard":
            desired_min, desired_max = 4, 5
        elif self.current_difficulty == "bench":
            desired_min, desired_max = 5, 6
        else:
            desired_min, desired_max = 2, 3  # 默认
        num_variants = random.randint(desired_min, desired_max)
        # 若总位数不足以容纳所有解，降低解的个数
        num_variants = min(num_variants, max(1, num_total // max(1, num_solution)))

        # 约束小数值区间，用于偏向小数确保“基数最大”
        small_high = min(self.value_range[1], self.value_range[0] + 15)
        low, high = self.value_range[0], self.value_range[1]

        # 1) 先生成第一个解，确定target
        solution_values_1 = [random.randint(self.value_range[0], small_high) for _ in range(num_solution)]
        target = sum(solution_values_1)
        solutions_values_list: List[List[int]] = [solution_values_1]

        # 2) 生成另外(num_variants-1)个不同的解，和为同一target
        for _ in range(num_variants - 1):
            for _attempt in range(200):
                candidate = self._generate_solution_with_sum(target, num_solution, self.value_range[0], small_high)
                # 要求与已有解的多重集不同
                def multiset_signature(vals: List[int]) -> Tuple[Tuple[int, int], ...]:
                    m = {}
                    for v in vals:
                        m[v] = m.get(v, 0) + 1
                    return tuple(sorted(m.items()))
                cand_sig = multiset_signature(candidate)
                if all(cand_sig != multiset_signature(exist) for exist in solutions_values_list):
                    solutions_values_list.append(candidate)
                    break

        # 3) 生成干扰项
        # 预留出所有解需要的槽位
        required_slots = num_solution * len(solutions_values_list)
        if required_slots > num_total:
            num_total = required_slots
        num_distractors = max(0, num_total - required_slots)
        distractors = [random.randint(low, high) for _ in range(num_distractors)]

        # 4) 合并并打乱，记录各个解在打乱后的索引
        tagged = []
        answer_index_sets: List[List[int]] = []
        for sol_idx, sol_vals in enumerate(solutions_values_list):
            tagged.extend([(v, ('sol', sol_idx)) for v in sol_vals])
        tagged.extend([(v, 'dist') for v in distractors])
        random.shuffle(tagged)

        numbers_dict = {}
        # 使用每个解的编号进行分桶，保证与原始解一一对应
        sol_buckets: List[List[int]] = [[] for _ in range(len(solutions_values_list))]

        for i, (value, tag) in enumerate(tagged):
            numbers_dict[str(i)] = value
            if isinstance(tag, tuple) and tag[0] == 'sol':
                sol_idx = tag[1]
                sol_buckets[sol_idx].append(i)

        # 归并答案索引
        answer_index_sets = [sorted(bucket) for bucket in sol_buckets if len(bucket) == num_solution]

        problem = {"target": target, "numbers": numbers_dict}
        return problem, answer_index_sets

    def set_difficulty_params(self, difficulty: str):
        """根据难度设置参数"""
        if difficulty == "easy":
            self.total_numbers_range = (5, 10)
            self.solution_size_range = (4, 8)
            self.value_range = (1, 5)
            self.current_difficulty = "easy"
        elif difficulty == "medium":
            self.total_numbers_range = (8, 12)
            self.solution_size_range = (4, 8)
            self.value_range = (1, 10)
            self.current_difficulty = "medium"
        elif difficulty == "hard":
            self.total_numbers_range = (12, 15)
            self.solution_size_range = (8, 12)
            self.value_range = (1, 15)
            self.current_difficulty = "hard"
        elif difficulty == "bench":
            self.total_numbers_range = (15, 20)
            self.solution_size_range = (10, 15)
            self.value_range = (1, 15)
            self.current_difficulty = "bench"

    def generate_questions(self, num_questions: int, difficulty: str = "medium") -> Dict:
        """
        生成指定数量和难度的问题集
        """
        self.set_difficulty_params(difficulty)
            
        questions = {}
        answers = {}
        
        for i in range(1, num_questions + 1):
            # print(f"生成第 {i}/{num_questions} 题 ({difficulty})...")
            problem, answer_index_sets = self.generate_single_question()
            questions[f"question{i}"] = problem
            # 多解答案为索引列表的列表
            answers[f"question{i}"] = answer_index_sets
            
        avg_numbers = sum(len(q["numbers"]) for q in questions.values()) / len(questions)
        big_small = "big"
        
        return {
            "big_small": big_small,
            "questions": questions,
            "answers": answers,
            "metadata": {
                "difficulty": difficulty,
                "num_questions": num_questions,
                "avg_numbers": avg_numbers,
                "generation_params": {
                    "total_numbers_range": self.total_numbers_range,
                    "solution_size_range": self.solution_size_range,
                    "value_range": self.value_range,
                }
            }
        }
    
    def generate_mixed_difficulty_questions(self, easy_count: int = 0, medium_count: int = 0, hard_count: int = 0, bench_count: int = 0) -> Dict:
        """
        生成混合难度的问题集，顺序为easy->medium->hard->bench
        
        Args:
            easy_count: 简单题目数量
            medium_count: 中等题目数量  
            hard_count: 困难题目数量
            bench_count: 基准题目数量
        """
        all_questions = {}
        all_answers = {}
        all_metadata = {}
        
        total_count = easy_count + medium_count + hard_count + bench_count
        current_count = 0
        
        # 生成简单题目
        if easy_count > 0:
            print(f"\n=== 生成 {easy_count} 道简单题目 ===")
            self.set_difficulty_params("easy")
            # 按顺序添加easy题目
            for i in range(1, easy_count + 1):
                current_count += 1
                problem, answer_index_sets = self.generate_single_question()
                
                key = f"easy_question{i}"
                all_questions[key] = problem
                all_answers[key] = {
                    "answer": answer_index_sets,
                    "difficulty": "easy"
                }
            
            all_metadata["easy"] = {
                "count": easy_count,
                "params": {
                    "total_numbers_range": (5, 10),
                    "solution_size_range": (4, 8),
                    "value_range": (1, 5)
                }
            }
        
        # 生成中等题目
        if medium_count > 0:
            print(f"\n=== 生成 {medium_count} 道中等题目 ===")
            self.set_difficulty_params("medium")
            # 按顺序添加medium题目
            for i in range(1, medium_count + 1):
                current_count += 1
                problem, answer_index_sets = self.generate_single_question()
                
                key = f"medium_question{i}"
                all_questions[key] = problem
                all_answers[key] = {
                    "answer": answer_index_sets,
                    "difficulty": "medium"
                }
            
            all_metadata["medium"] = {
                "count": medium_count,
                "params": {
                    "total_numbers_range": (10, 15),
                    "solution_size_range": (8, 12),
                    "value_range": (1, 10)
                }
            }
        
        # 生成困难题目
        if hard_count > 0:
            print(f"\n=== 生成 {hard_count} 道困难题目 ===")
            self.set_difficulty_params("hard")
            # 按顺序添加hard题目
            for i in range(1, hard_count + 1):
                current_count += 1
                problem, answer_index_sets = self.generate_single_question()
                
                key = f"hard_question{i}"
                all_questions[key] = problem
                all_answers[key] = {
                    "answer": answer_index_sets,
                    "difficulty": "hard"
                }
            
            all_metadata["hard"] = {
                "count": hard_count,
                "params": {
                    "total_numbers_range": (15, 20),
                    "solution_size_range": (12, 16),
                    "value_range": (1, 20)
                }
            }
        
        # 生成基准题目
        if bench_count > 0:
            print(f"\n=== 生成 {bench_count} 道基准题目 ===")
            self.set_difficulty_params("bench")
            # 按顺序添加bench题目
            for i in range(1, bench_count + 1):
                current_count += 1
                problem, answer_index_sets = self.generate_single_question()
                
                key = f"bench_question{i}"
                all_questions[key] = problem
                all_answers[key] = {
                    "answer": answer_index_sets,
                    "difficulty": "bench"
                }
            
            all_metadata["bench"] = {
                "count": bench_count,
                "params": {
                    "total_numbers_range": (15, 20),
                    "solution_size_range": (10, 15),
                    "value_range": (1, 15)
                }
            }
        
        # 计算平均数字数量
        avg_numbers = sum(len(q["numbers"]) for q in all_questions.values()) / len(all_questions) if all_questions else 0
        big_small = "big"
        
        return {
            "big_small": big_small,
            "questions": all_questions,
            "answers": all_answers,
            "metadata": {
                "total_count": total_count,
                "easy_count": easy_count,
                "medium_count": medium_count,
                "hard_count": hard_count,
                "bench_count": bench_count,
                "avg_numbers": avg_numbers,
                "difficulties": all_metadata
            }
        }

def main():
    parser = argparse.ArgumentParser(
        description='生成子集和问题数据集',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成混合难度题目
  python generate_questions.py --easy 5 --medium 3 --hard 2 --bench 1 --output mixed_questions.json
  
  # 只生成简单题目
  python generate_questions.py --easy 10 --output easy_questions.json
  
  # 生成分离文件
  python generate_questions.py --easy 5 --medium 5 --hard 5 --bench 5 --separate
  
  # 传统模式 (兼容旧版本)
  python generate_questions.py --num_questions 5 --difficulty medium
        """)
    
    # 混合难度参数
    parser.add_argument('--easy', type=int, default=0, help='生成简单题目数量')
    parser.add_argument('--medium', type=int, default=0, help='生成中等题目数量')
    parser.add_argument('--hard', type=int, default=0, help='生成困难题目数量')
    parser.add_argument('--bench', type=int, default=0, help='生成基准题目数量')
    parser.add_argument('--separate', action='store_true', help='为每个难度生成单独的文件')
    
    # 传统参数 (兼容性)
    parser.add_argument('--num_questions', type=int, default=None, help='生成题目数量 (传统模式)')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard', 'bench'], default='medium', help='难度级别 (传统模式)')
    
    # 输出参数
    parser.add_argument('--output', type=str, default='generated_subset_sum_questions.json', help='输出文件名')
    
    # 高级参数
    parser.add_argument('--num_total_min', type=int, default=None, help='数字总数最小值 (覆盖默认值)')
    parser.add_argument('--num_total_max', type=int, default=None, help='数字总数最大值 (覆盖默认值)')
    parser.add_argument('--solution_size_min', type=int, default=None, help='解集大小最小值 (覆盖默认值)')
    parser.add_argument('--solution_size_max', type=int, default=None, help='解集大小最大值 (覆盖默认值)')
    parser.add_argument('--value_min', type=int, default=None, help='数值范围最小值 (覆盖默认值)')
    parser.add_argument('--value_max', type=int, default=None, help='数值范围最大值 (覆盖默认值)')

    args = parser.parse_args()
    
    # 检查参数有效性
    if args.num_questions is not None:
        # 传统模式
        if args.easy + args.medium + args.hard + args.bench > 0:
            print("错误: 不能同时使用传统模式参数 (--num_questions) 和混合模式参数 (--easy, --medium, --hard, --bench)")
            return
        use_traditional_mode = True
        total_questions = args.num_questions
    else:
        # 混合模式
        use_traditional_mode = False
        total_questions = args.easy + args.medium + args.hard + args.bench
        if total_questions == 0:
            print("错误: 必须指定至少一种难度的题目数量")
            print("使用 --easy N, --medium M, --hard P, 或 --bench B 来指定各难度题目数量")
            print("或使用传统模式: --num_questions N --difficulty LEVEL")
            return
    
    generator = SubsetSumGenerator()
    
    # 应用自定义参数
    if args.num_total_min and args.num_total_max:
        generator.total_numbers_range = (args.num_total_min, args.num_total_max)
    if args.solution_size_min and args.solution_size_max:
        generator.solution_size_range = (args.solution_size_min, args.solution_size_max)
    if args.value_min and args.value_max:
        generator.value_range = (args.value_min, args.value_max)
    
    print("="*60)
    print("子集和问题生成器")
    print("="*60)
    
    if use_traditional_mode:
        print(f"模式: 传统模式")
        print(f"题目数量: {args.num_questions}")
        print(f"难度: {args.difficulty}")
        
        dataset = generator.generate_questions(args.num_questions, args.difficulty)
        
        # 保存文件
        output_data = {"big_small": dataset["big_small"], "questions": dataset["questions"]}
        save_json_compact(output_data, args.output)
        
        # 保存答案文件（多解）
        answer_file = args.output.replace('.json', '_with_answers.json')
        with open(answer_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n生成完成!")
        print(f"题目文件: {args.output}")
        print(f"答案文件: {answer_file}")
        
    else:
        print(f"模式: 混合难度模式")
        print(f"简单题目: {args.easy}")
        print(f"中等题目: {args.medium}")  
        print(f"困难题目: {args.hard}")
        print(f"基准题目: {args.bench}")
        print(f"总计: {total_questions}")
        
        dataset = generator.generate_mixed_difficulty_questions(
            easy_count=args.easy,
            medium_count=args.medium,
            hard_count=args.hard,
            bench_count=args.bench
        )
        
        if args.separate:
            # 分离模式：为每个难度生成单独文件
            base_name = args.output.replace('.json', '')
            
            if args.easy > 0:
                easy_questions = {k: v for k, v in dataset["questions"].items() if k.startswith("easy_")}
                easy_data = {"big_small": dataset["big_small"], "questions": easy_questions}
                easy_file = f"{base_name}_easy.json"
                save_json_compact(easy_data, easy_file)
                print(f"简单题目文件: {easy_file}")
                
            if args.medium > 0:
                medium_questions = {k: v for k, v in dataset["questions"].items() if k.startswith("medium_")}
                medium_data = {"big_small": dataset["big_small"], "questions": medium_questions}
                medium_file = f"{base_name}_medium.json"
                save_json_compact(medium_data, medium_file)
                print(f"中等题目文件: {medium_file}")
                
            if args.hard > 0:
                hard_questions = {k: v for k, v in dataset["questions"].items() if k.startswith("hard_")}
                hard_data = {"big_small": dataset["big_small"], "questions": hard_questions}
                hard_file = f"{base_name}_hard.json"
                save_json_compact(hard_data, hard_file)
                print(f"困难题目文件: {hard_file}")

            if args.bench > 0:
                bench_questions = {k: v for k, v in dataset["questions"].items() if k.startswith("bench_")}
                bench_data = {"big_small": dataset["big_small"], "questions": bench_questions}
                bench_file = f"{base_name}_bench.json"
                save_json_compact(bench_data, bench_file)
                print(f"基准题目文件: {bench_file}")
        else:
            # 混合模式：所有题目在一个文件中
            output_data = {"big_small": dataset["big_small"], "questions": dataset["questions"]}
            save_json_compact(output_data, args.output)
            print(f"混合题目文件: {args.output}")
        
        # 总是生成包含答案的文件（多解）
        answer_file = args.output.replace('.json', '_with_answers.json')
        with open(answer_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"答案文件: {answer_file}")
    
    print(f"\n生成统计:")
    if use_traditional_mode:
        print(f"  难度: {dataset['metadata']['difficulty']}")
        print(f"  题目数量: {dataset['metadata']['num_questions']}")
        print(f"  平均数字数量: {dataset['metadata']['avg_numbers']:.1f}")
    else:
        print(f"  简单题目: {dataset['metadata']['easy_count']}")
        print(f"  中等题目: {dataset['metadata']['medium_count']}")
        print(f"  困难题目: {dataset['metadata']['hard_count']}")
        print(f"  基准题目: {dataset['metadata']['bench_count']}")
        print(f"  总题目数: {dataset['metadata']['total_count']}")
        print(f"  平均数字数量: {dataset['metadata']['avg_numbers']:.1f}")
    
    # 显示第一题的示例
    if dataset["questions"]:
        first_question_key = list(dataset["questions"].keys())[0]
        first_question = dataset["questions"][first_question_key]
        first_answer = dataset["answers"][first_question_key]
        # 兼容两种结构：传统模式(list) 与 混合模式(dict: {"answer": list})
        if isinstance(first_answer, dict) and "answer" in first_answer:
            sol_sets = first_answer["answer"]
        else:
            sol_sets = first_answer
        print(f"\n示例题目 ({first_question_key}):")
        print(f"数字总数: {len(first_question['numbers'])}")
        print(f"目标和: {first_question['target']}")
        print(f"可行最优解数量: {len(sol_sets) if isinstance(sol_sets, list) else 0}")
        if isinstance(sol_sets, list) and sol_sets:
            print(f"每个解的基数: {len(sol_sets[0])}")

if __name__ == "__main__":
    main() 