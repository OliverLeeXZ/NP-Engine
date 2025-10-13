#!/usr/bin/env python3
"""
基于规则的旅行商问题（TSP）造题脚本
支持通过超参数控制生成题目的难度和数量
支持混合难度生成：可以同时生成不同难度的题目
"""

import json
import random
import argparse
from typing import Dict, List, Tuple

def save_json_compact(data, filename):
    """
    使用自定义的紧凑格式保存JSON文件，使每个城市的距离信息在一行内显示。
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
            question = data["questions"][q_key]
            lines = [f'    "{q_key}": {{']
            node_lines = []
            
            # 按城市ID排序
            sorted_node_keys = sorted(question.keys(), key=int)
            for j, node_key in enumerate(sorted_node_keys):
                distances = question[node_key]
                # 格式化距离字典为单行字符串
                dist_items = [f'"{k}": {v}' for k, v in sorted(distances.items(), key=lambda item: int(item[0]))]
                node_line = f'      "{node_key}": {{{", ".join(dist_items)}}}'
                if j < len(sorted_node_keys) - 1:
                    node_line += ','
                node_lines.append(node_line)
            
            lines.append('\n'.join(node_lines))
            lines.append('    }')
            question_item = '\n'.join(lines)
            if i < len(sorted_q_keys) - 1:
                question_item += ','
            question_items.append(question_item)
        
        f.write('\n'.join(question_items))
        f.write('\n  }\n}\n')


class TSPGenerator:
    """旅行商问题生成器"""

    def __init__(self,
                 num_cities_range: Tuple[int, int] = (5, 10),
                 distance_range: Tuple[int, int] = (10, 100)):
        """
        初始化生成器
        
        Args:
            num_cities_range: 城市数量范围 (min, max)
            distance_range: 城市间距离范围 (min, max)
        """
        self.num_cities_range = num_cities_range
        self.distance_range = distance_range

    def generate_single_question(self) -> Dict:
        """
        生成单个TSP问题图。
        """
        num_cities = random.randint(*self.num_cities_range)
        
        # 生成对称的距离矩阵
        dist_matrix = [[0] * num_cities for _ in range(num_cities)]
        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                dist = random.randint(*self.distance_range)
                dist_matrix[i][j] = dist_matrix[j][i] = dist
        
        # 转换为题目要求的字典格式
        graph_dict = {}
        for i in range(num_cities):
            graph_dict[str(i)] = {str(j): dist_matrix[i][j] for j in range(num_cities)}
            
        return graph_dict

    def set_difficulty_params(self, difficulty: str):
        """根据难度设置参数"""
        if difficulty == "easy":
            self.num_cities_range = (10, 20)
        elif difficulty == "medium":
            self.num_cities_range = (20, 30)
        elif difficulty == "hard":
            self.num_cities_range = (35, 45)
        elif difficulty == "bench":
            self.num_cities_range = (45, 55)

    def generate_questions(self, num_questions: int, difficulty: str = "medium") -> Dict:
        """
        生成指定数量和难度的问题集
        """
        # 根据难度调整参数
        self.set_difficulty_params(difficulty)
            
        questions = {}
        
        for i in range(1, num_questions + 1):
            print(f"生成第 {i}/{num_questions} 题 ({difficulty}, 城市数范围: {self.num_cities_range})...")
            graph_dict = self.generate_single_question()
            questions[f"question{i}"] = graph_dict
        
        avg_cities = sum(len(q) for q in questions.values()) / len(questions)
        big_small = "small"
        
        return {
            "big_small": big_small,
            "questions": questions,
            "metadata": {
                "difficulty": difficulty,
                "num_questions": num_questions,
                "avg_cities": avg_cities,
                "generation_params": {
                    "num_cities_range": self.num_cities_range,
                    "distance_range": self.distance_range,
                }
            }
        }
    
    def generate_mixed_difficulty_questions(self, easy_count: int = 0, medium_count: int = 0, hard_count: int = 0, bench_count: int = 0) -> Dict:
        """
        生成混合难度的问题集，顺序为easy->medium->hard
        
        Args:
            easy_count: 简单题目数量
            medium_count: 中等题目数量  
            hard_count: 困难题目数量
            bench_count: 基准题目数量
        """
        all_questions = {}
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
                print(f"生成第 {current_count}/{total_count} 题 (easy_{i}, 城市数范围: {self.num_cities_range})...")
                graph_dict = self.generate_single_question()
                key = f"easy_question{i}"
                all_questions[key] = graph_dict
            
            all_metadata["easy"] = {
                "count": easy_count,
                "params": {
                    "num_cities_range": (4, 8),
                    "distance_range": self.distance_range
                }
            }
        
        # 生成中等题目
        if medium_count > 0:
            print(f"\n=== 生成 {medium_count} 道中等题目 ===")
            self.set_difficulty_params("medium")
            # 按顺序添加medium题目
            for i in range(1, medium_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (medium_{i}, 城市数范围: {self.num_cities_range})...")
                graph_dict = self.generate_single_question()
                key = f"medium_question{i}"
                all_questions[key] = graph_dict
            
            all_metadata["medium"] = {
                "count": medium_count,
                "params": {
                    "num_cities_range": (8, 15),
                    "distance_range": self.distance_range
                }
            }
        
        # 生成困难题目
        if hard_count > 0:
            print(f"\n=== 生成 {hard_count} 道困难题目 ===")
            self.set_difficulty_params("hard")
            # 按顺序添加hard题目
            for i in range(1, hard_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (hard_{i}, 城市数范围: {self.num_cities_range})...")
                graph_dict = self.generate_single_question()
                key = f"hard_question{i}"
                all_questions[key] = graph_dict
            
            all_metadata["hard"] = {
                "count": hard_count,
                "params": {
                    "num_cities_range": (15, 25),
                    "distance_range": self.distance_range
                }
            }
        
        # 生成基准题目
        if bench_count > 0:
            print(f"\n=== 生成 {bench_count} 道基准题目 ===")
            self.set_difficulty_params("bench")
            # 按顺序添加bench题目
            for i in range(1, bench_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (bench_{i}, 城市数范围: {self.num_cities_range})...")
                graph_dict = self.generate_single_question()
                key = f"bench_question{i}"
                all_questions[key] = graph_dict
            
            all_metadata["bench"] = {
                "count": bench_count,
                "params": {
                    "num_cities_range": (25, 35),
                    "distance_range": self.distance_range
                }
            }
        
        # 计算平均城市数
        avg_cities = sum(len(q) for q in all_questions.values()) / len(all_questions) if all_questions else 0
        big_small = "small"
        
        return {
            "big_small": big_small,
            "questions": all_questions,
            "metadata": {
                "total_count": total_count,
                "easy_count": easy_count,
                "medium_count": medium_count,
                "hard_count": hard_count,
                "bench_count": bench_count,
                "avg_cities": avg_cities,
                "difficulties": all_metadata
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='生成旅行商问题数据集',
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
    parser.add_argument('--output', type=str, default='generated_tsp_questions.json', help='输出文件名')
    
    # 高级参数
    parser.add_argument('--num_cities_min', type=int, default=None, help='最小城市数 (覆盖默认值)')
    parser.add_argument('--num_cities_max', type=int, default=None, help='最大城市数 (覆盖默认值)')
    parser.add_argument('--dist_min', type=int, default=10, help='最小距离')
    parser.add_argument('--dist_max', type=int, default=100, help='最大距离')
    
    args = parser.parse_args()
    
    # 检查参数有效性
    if args.num_questions is not None:
        # 传统模式
        if args.easy + args.medium + args.hard + args.bench > 0:
            print("错误: 不能同时使用传统模式参数 (--num_questions) 和混合模式参数 (--easy, --medium, --hard)")
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
    
    generator = TSPGenerator(
        distance_range=(args.dist_min, args.dist_max)
    )
    
    # 应用自定义城市数量范围
    if args.num_cities_min and args.num_cities_max:
        generator.num_cities_range = (args.num_cities_min, args.num_cities_max)
    
    print("="*60)
    print("旅行商问题生成器")
    print("="*60)
    
    if use_traditional_mode:
        print(f"模式: 传统模式")
        print(f"题目数量: {args.num_questions}")
        print(f"难度: {args.difficulty}")
        
        dataset = generator.generate_questions(args.num_questions, args.difficulty)
        
        # 保存文件
        output_data = {
            "big_small": dataset["big_small"],
            "questions": dataset["questions"]
        }
        save_json_compact(output_data, args.output)
        
        print(f"\n生成完成!")
        print(f"题目文件: {args.output}")
        
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
            output_data = {
                "big_small": dataset["big_small"],
                "questions": dataset["questions"]
            }
            save_json_compact(output_data, args.output)
            print(f"混合题目文件: {args.output}")
    
    print(f"\n生成统计:")
    if use_traditional_mode:
        print(f"  难度: {dataset['metadata']['difficulty']}")
        print(f"  题目数量: {dataset['metadata']['num_questions']}")
        print(f"  平均城市数: {dataset['metadata']['avg_cities']:.1f}")
    else:
        print(f"  简单题目: {dataset['metadata']['easy_count']}")
        print(f"  中等题目: {dataset['metadata']['medium_count']}")
        print(f"  困难题目: {dataset['metadata']['hard_count']}")
        print(f"  基准题目: {dataset['metadata']['bench_count']}")
        print(f"  总题目数: {dataset['metadata']['total_count']}")
        print(f"  平均城市数: {dataset['metadata']['avg_cities']:.1f}")
    
    # 显示第一题的示例
    if dataset["questions"]:
        first_question_key = list(dataset["questions"].keys())[0]
        first_question = dataset["questions"][first_question_key]
        print(f"\n示例题目 ({first_question_key}):")
        print(f"城市数量: {len(first_question)}")

if __name__ == "__main__":
    main() 