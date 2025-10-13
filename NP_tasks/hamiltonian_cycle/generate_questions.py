#!/usr/bin/env python3
"""
基于规则的哈密顿回路问题（Hamiltonian Cycle Problem）造题脚本
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
            graph = data["questions"][q_key]
            lines = [f'    "{q_key}": {{']
            
            node_items = []
            sorted_node_keys = sorted(graph.keys(), key=int)
            for j, node_key in enumerate(sorted_node_keys):
                adj_list = sorted([int(neighbor) for neighbor in graph[node_key]])
                adj_str = json.dumps(adj_list)
                node_line = f'      "{node_key}": {adj_str}'
                if j < len(sorted_node_keys) - 1:
                    node_line += ','
                node_items.append(node_line)
            
            lines.append('\n'.join(node_items))
            lines.append('    }')
            question_item = '\n'.join(lines)
            if i < len(sorted_q_keys) - 1:
                question_item += ','
            question_items.append(question_item)
            
        f.write('\n'.join(question_items))
        f.write('\n  }\n}\n')

class HamiltonianCycleGenerator:
    """哈密顿回路问题生成器"""

    def __init__(self, params: Dict):
        self.p = params

    def generate_single_question(self) -> Tuple[Dict, List[int]]:
        """
        生成单个哈密顿回路问题，并确保有解。
        方法：先创建一个包含所有顶点的环，然后添加额外的边作为干扰。
        """
        num_vertices = random.randint(*self.p["num_vertices"])
        
        # 1. 创建一个包含所有顶点的路径，并随机打乱
        nodes = list(range(num_vertices))
        random.shuffle(nodes)
        solution_cycle = nodes + [nodes[0]] # 闭合成环

        # 2. 初始化邻接表并构建环的边
        adj = {str(i): {} for i in range(num_vertices)}
        for i in range(len(solution_cycle) - 1):
            u, v = solution_cycle[i], solution_cycle[i+1]
            adj[str(u)][str(v)] = 1
            adj[str(v)][str(u)] = 1

        # 3. 添加额外的"干扰"边
        edge_density = self.p["edge_density"]
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                # 如果边不存在，则按概率添加
                if str(j) not in adj[str(i)]:
                    if random.random() < edge_density:
                        adj[str(i)][str(j)] = 1
                        adj[str(j)][str(i)] = 1
        
        # 将邻接字典转换为邻接列表以匹配输出格式
        final_adj = {k: list(v.keys()) for k, v in adj.items()}

        return final_adj, solution_cycle

    def get_difficulty_params(self, difficulty: str) -> Dict:
        """获取指定难度的参数"""
        if difficulty == "easy":
            # 节点少，干扰边少
            return {"num_vertices": (15, 20), "edge_density": 0.2}
        elif difficulty == "medium":
            return {"num_vertices": (20, 30), "edge_density": 0.3}
        elif difficulty == "hard":
            # 节点多，图更稠密，更难找到主路径
            return {"num_vertices": (30, 40), "edge_density": 0.4}
        elif difficulty == "bench":
            # 节点多，图更稠密，更难找到主路径
            return {"num_vertices": (40, 50), "edge_density": 0.5}
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
        total_vertices = 0
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
            total_vertices += sum(len(q) for q in easy_q.values())
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
            total_vertices += sum(len(q) for q in medium_q.values())
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
            total_vertices += sum(len(q) for q in hard_q.values())
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
            total_vertices += sum(len(q) for q in bench_q.values())
            total_questions += bench_num
            
        avg_vertices = total_vertices / total_questions if total_questions > 0 else 0
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
                "avg_vertices": avg_vertices
            }
        }

def main():
    parser = argparse.ArgumentParser(description='生成哈密顿回路问题数据集')
    parser.add_argument('--easy', type=int, default=0, help='生成简单题目数量')
    parser.add_argument('--medium', type=int, default=0, help='生成中等题目数量')
    parser.add_argument('--hard', type=int, default=0, help='生成困难题目数量')
    parser.add_argument('--bench', type=int, default=0, help='生成基准题目数量')
    parser.add_argument('--output', type=str, default='generated_hamiltonian_cycle_questions.json', help='输出文件名')
    parser.add_argument('--separate', action='store_true', help='是否为每种难度生成单独的文件')
    args = parser.parse_args()

    # 检查参数
    if args.easy + args.medium + args.hard + args.bench == 0:
        print("错误: 至少需要指定一种难度的题目数量 > 0")
        print("例如: python generate_questions.py --easy 5 --medium 3 --hard 2 --bench 1")
        return

    generator = HamiltonianCycleGenerator({})
    
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
        print(f"平均顶点数: {dataset['metadata']['avg_vertices']:.1f}")

if __name__ == "__main__":
    main() 