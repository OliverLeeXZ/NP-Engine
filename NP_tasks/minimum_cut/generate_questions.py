#!/usr/bin/env python3
"""
基于规则的平衡最小割（Minimum Bisection）造题脚本
支持通过超参数控制生成题目的难度和数量
支持混合难度生成：可以同时生成不同难度的题目
"""

import json
import random
import argparse
from typing import Dict, List, Tuple, Set
import networkx as nx
from itertools import combinations
from networkx.algorithms.community import kernighan_lin_bisection


class CompactJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，用于生成紧凑格式的JSON"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_indent = 0
        
    def encode(self, obj):
        if isinstance(obj, dict):
            if self._is_node_dict(obj):
                # 如果是节点字典（包含数字键的字典），使用紧凑格式
                return self._encode_node_dict(obj)
            elif self._is_questions_dict(obj):
                # 如果是questions字典，特殊处理
                return self._encode_questions_dict(obj)
        return super().encode(obj)
    
    def _is_node_dict(self, obj):
        """检查是否是节点邻接字典（所有键都是数字字符串）"""
        if not isinstance(obj, dict) or not obj:
            return False
        return all(key.isdigit() for key in obj.keys())
    
    def _is_questions_dict(self, obj):
        """检查是否是questions字典"""
        if not isinstance(obj, dict):
            return False
        return any(key.startswith('question') for key in obj.keys())
    
    def _encode_node_dict(self, obj):
        """编码节点邻接字典为紧凑格式"""
        items = []
        for key in sorted(obj.keys(), key=int):
            value = obj[key]
            items.append(f'"{key}": {value}')
        return '{' + ', '.join(items) + '}'
    
    def _encode_questions_dict(self, obj):
        """编码questions字典"""
        items = []
        for key in sorted(obj.keys(), key=lambda x: int(x.replace('question', '').replace('easy_', '').replace('medium_', '').replace('hard_', '')) if any(prefix in x for prefix in ['question', 'easy_', 'medium_', 'hard_']) else 0):
            value = obj[key]
            if self._is_node_dict(value):
                encoded_value = self._encode_question_graph(value)
                items.append(f'    "{key}": {encoded_value}')
            else:
                items.append(f'    "{key}": {json.dumps(value)}')
        return '{\n' + ',\n'.join(items) + '\n  }'
    
    def _encode_question_graph(self, graph_dict):
        """编码单个问题的图字典"""
        lines = []
        lines.append('{')
        node_items = []
        for node_key in sorted(graph_dict.keys(), key=int):
            node_value = graph_dict[node_key]
            node_line = f'      "{node_key}": {self._encode_node_dict(node_value)}'
            node_items.append(node_line)
        lines.append(',\n'.join(node_items))
        lines.append('    }')
        return '\n'.join(lines)


def save_json_compact(data, filename):
    """保存JSON文件，使用紧凑格式"""
    with open(filename, 'w', encoding='utf-8') as f:
        if "questions" in data:
            # 手动构建格式化的JSON字符串
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
            
            for question_key in sorted_q_keys:
                question_value = data["questions"][question_key]
                
                # 构建question的内容
                lines = [f'    "{question_key}": {{']
                node_lines = []
                for node_key in sorted(question_value.keys(), key=int):
                    node_value = question_value[node_key]
                    # 构建单行的节点邻接信息
                    adj_items = []
                    for adj_key in sorted(node_value.keys(), key=int):
                        adj_items.append(f'"{adj_key}": {node_value[adj_key]}')
                    node_line = f'      "{node_key}": {{{", ".join(adj_items)}}}'
                    node_lines.append(node_line)
                
                lines.append(',\n'.join(node_lines))
                lines.append('    }')
                question_items.append('\n'.join(lines))
            
            f.write(',\n'.join(question_items))
            f.write('\n  }\n}')
        else:
            # 对于包含answers的文件，使用标准格式
            json.dump(data, f, indent=2, ensure_ascii=False)


class MinimumCutGenerator:
    """平衡最小割（Minimum Bisection）问题生成器"""
    
    def __init__(self, 
                 num_nodes_range: Tuple[int, int] = (4, 12),
                 edge_density: float = 0.5,
                 weight_range: Tuple[int, int] = (1, 6),
                 ensure_path_exists: bool = True,
                 min_cut_size: int = 1,
                 exact_threshold: int = 16,
                 kl_restarts: int = 8):
        """
        初始化生成器
        
        Args:
            num_nodes_range: 节点数量范围 (min, max)
            edge_density: 边密度 (0-1), 控制图的稠密程度
            weight_range: 边权重范围 (min, max)
            ensure_path_exists: 是否确保图连通
            min_cut_size: 最小割的最小大小（用于过滤过于容易的题）
            exact_threshold: 小图精确求解阈值（节点数<=该值时做精确等分枚举）
            kl_restarts: 大图KL启发式的随机重启次数
        """
        self.num_nodes_range = num_nodes_range
        self.edge_density = edge_density
        self.weight_range = weight_range
        self.ensure_path_exists = ensure_path_exists
        self.min_cut_size = min_cut_size
        self.exact_threshold = exact_threshold
        self.kl_restarts = kl_restarts
        
    def generate_connected_graph(self, num_nodes: int) -> nx.Graph:
        """生成连通图"""
        G = nx.Graph()
        G.add_nodes_from(range(num_nodes))
        
        # 首先确保图连通 - 生成一个生成树
        nodes = list(range(num_nodes))
        random.shuffle(nodes)
        
        # 构建最小生成树确保连通性
        for i in range(1, num_nodes):
            # 连接到之前的一个随机节点
            prev_node = random.choice(nodes[:i])
            weight = random.randint(*self.weight_range)
            G.add_edge(nodes[i], prev_node, weight=weight)
        
        # 根据edge_density添加额外的边
        max_edges = num_nodes * (num_nodes - 1) // 2
        current_edges = num_nodes - 1
        target_edges = int(max_edges * self.edge_density)
        
        possible_edges = list(combinations(range(num_nodes), 2))
        existing_edges = set(G.edges())
        possible_new_edges = [e for e in possible_edges if e not in existing_edges and (e[1], e[0]) not in existing_edges]
        
        # 随机添加边直到达到目标密度
        additional_edges = min(target_edges - current_edges, len(possible_new_edges))
        if additional_edges > 0:
            new_edges = random.sample(possible_new_edges, additional_edges)
            for u, v in new_edges:
                weight = random.randint(*self.weight_range)
                G.add_edge(u, v, weight=weight)
        
        return G

    def generate_random_graph(self, num_nodes: int) -> nx.Graph:
        """生成（可能不连通的）随机图——用于 ensure_path_exists=False 的分支"""
        G = nx.Graph()
        G.add_nodes_from(range(num_nodes))
        possible_edges = list(combinations(range(num_nodes), 2))
        random.shuffle(possible_edges)
        target_edges = int(self.edge_density * len(possible_edges))
        for (u, v) in possible_edges[:target_edges]:
            weight = random.randint(*self.weight_range)
            G.add_edge(u, v, weight=weight)
        return G

    def _generate_deceptive_graph(self, num_nodes: int) -> nx.Graph:
        """
        生成一个带有欺骗性结构的图，用于“困难”级别。
        这个图有一个明显的、但却是次优的切割方案。
        """
        G = nx.Graph()
        nodes = list(range(num_nodes))
        G.add_nodes_from(nodes)

        # 1. 将节点分为两个最终的正确分区 A 和 B
        half = num_nodes // 2
        set_A = nodes[:half]
        set_B = nodes[half:]

        # 2. 在分区内部创建高权重的紧密连接
        for u in set_A:
            for v in set_A:
                if u < v and random.random() < 0.8: # 高密度
                    G.add_edge(u, v, weight=random.randint(8, 10))
        for u in set_B:
            for v in set_B:
                if u < v and random.random() < 0.8:
                    G.add_edge(u, v, weight=random.randint(8, 10))
        
        # 3. 创建真正的、权重较低的最优割
        optimal_cut_weight = 0
        for _ in range(num_nodes // 8):
            u = random.choice(set_A)
            v = random.choice(set_B)
            if not G.has_edge(u,v):
                weight = random.randint(1, 3)
                G.add_edge(u, v, weight=weight)
                optimal_cut_weight += weight

        # 4. 创建欺骗性结构
        # 从 A 和 B 中各取一小部分节点作为“诱饵”
        trap_size = max(2, num_nodes // 8)
        trap_nodes_A = random.sample(set_A, trap_size)
        trap_nodes_B = random.sample(set_B, trap_size)
        
        # 在这些诱饵节点之间创建权重中等的边，形成一个“假桥”
        # 这个假桥的权重总和应该比最优割稍高，但看起来很有吸引力
        decoy_cut_weight = 0
        while decoy_cut_weight <= optimal_cut_weight:
            u = random.choice(trap_nodes_A)
            v = random.choice(trap_nodes_B)
            if not G.has_edge(u,v):
                # 权重比最优割的边要高，但比内部连接的边要低
                weight = random.randint(4, 6) 
                G.add_edge(u, v, weight=weight)
                decoy_cut_weight += weight

        return G
        
    def _generate_community_graph(self, num_nodes: int, intra_density: float, inter_edges: int, noise_level: float) -> nx.Graph:
        """
        生成一个具有两个社区的图，用于“简单”和“中等”级别。
        难度由社区内部密度和社区间连接数控制。
        """
        G = nx.Graph()
        nodes = list(range(num_nodes))
        G.add_nodes_from(nodes)
        
        half = num_nodes // 2
        set_A = nodes[:half]
        set_B = nodes[half:]

        # 社区内部连接
        for u in set_A:
            for v in set_A:
                if u < v and random.random() < intra_density:
                    G.add_edge(u, v, weight=random.randint(5, 10))
        for u in set_B:
            for v in set_B:
                if u < v and random.random() < intra_density:
                    G.add_edge(u, v, weight=random.randint(5, 10))

        # 社区之间连接
        for _ in range(inter_edges):
            u = random.choice(set_A)
            v = random.choice(set_B)
            if not G.has_edge(u,v):
                G.add_edge(u, v, weight=random.randint(1, 4))
        
        # 确保图是连通的
        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            for i in range(len(components) - 1):
                u = random.choice(list(components[i]))
                v = random.choice(list(components[i+1]))
                if not G.has_edge(u, v):
                    G.add_edge(u, v, weight=random.randint(1,3))

        # 最后，加入全局噪声
        self._add_noise_edges(G, noise_level)

        return G

    def _add_noise_edges(self, G: nx.Graph, noise_level: float):
        """
        在图中添加随机的噪声边，以增加结构复杂性。
        """
        if noise_level == 0:
            return
        
        num_nodes = G.number_of_nodes()
        nodes = list(G.nodes())
        max_possible_edges = num_nodes * (num_nodes - 1) // 2
        num_noise_edges = int(max_possible_edges * noise_level)

        for _ in range(num_noise_edges):
            u, v = random.sample(nodes, 2)
            if not G.has_edge(u, v):
                # 噪声边的权重范围很广，使其难以预测
                weight = random.randint(self.weight_range[0], self.weight_range[1])
                G.add_edge(u, v, weight=weight)

    def _generate_hell_mode_graph(self, num_nodes: int, traitor_strength: int, noise_level: float) -> nx.Graph:
        """
        生成一个极具挑战性的图，用于“地狱级”难度。
        此图包含多个相互关联的欺骗性结构。
        """
        G = nx.Graph()
        nodes = list(range(num_nodes))
        G.add_nodes_from(nodes)

        # 1. 将节点分为三个社区 A, B, C
        third = num_nodes // 3
        set_A = nodes[:third]
        set_B = nodes[third:2*third]
        set_C = nodes[2*third:]
        
        # 让B和C内部连接更紧密
        for u in set_B:
            for v in set_B:
                if u < v and random.random() < 0.9:
                    G.add_edge(u, v, weight=random.randint(8, 10))
        for u in set_C:
            for v in set_C:
                if u < v and random.random() < 0.9:
                    G.add_edge(u, v, weight=random.randint(8, 10))

        # 2. 创建真正的最优割：分离 {A} 与 {B, C}
        optimal_cut_weight = 0
        # A与B的连接
        for _ in range(num_nodes // 10):
            u, v = random.choice(set_A), random.choice(set_B)
            if not G.has_edge(u,v):
                weight = random.randint(1, 2)
                G.add_edge(u, v, weight=weight)
                optimal_cut_weight += weight
        # A与C的连接
        for _ in range(num_nodes // 10):
            u, v = random.choice(set_A), random.choice(set_C)
            if not G.has_edge(u,v):
                weight = random.randint(1, 2)
                G.add_edge(u, v, weight=weight)
                optimal_cut_weight += weight
        
        # 3. 第一层陷阱：在B和C之间制造一个次优的“假桥”
        decoy_cut_weight = 0
        while decoy_cut_weight <= optimal_cut_weight * 1.2: # 确保比最优解差一些
            u, v = random.choice(set_B), random.choice(set_C)
            if not G.has_edge(u,v):
                weight = random.randint(3, 5)
                G.add_edge(u, v, weight=weight)
                decoy_cut_weight += weight

        # 4. 第二层陷阱：在社区A内部制造“叛徒”节点
        traitor_size = max(1, third // 4)
        traitors = random.sample(set_A, traitor_size)
        loyalists = [node for node in set_A if node not in traitors]
        
        # “叛徒”与社区A内部连接稀疏
        for u in traitors:
            for v in loyalists:
                if random.random() < 0.2:
                    G.add_edge(u, v, weight=random.randint(1, 3))
        
        # 忠诚者之间紧密连接
        for u in loyalists:
            for v in loyalists:
                if u < v and random.random() < 0.9:
                     G.add_edge(u, v, weight=random.randint(8, 10))
        
        # “叛徒”与外部社区B和C建立超高权重连接
        for u in traitors:
            # 与B建立连接
            for _ in range(traitor_strength):
                v = random.choice(set_B)
                if not G.has_edge(u,v):
                    G.add_edge(u, v, weight=random.randint(9, 10))
            # 与C建立连接
            for _ in range(traitor_strength):
                v = random.choice(set_C)
                if not G.has_edge(u,v):
                    G.add_edge(u, v, weight=random.randint(9, 10))

        # 最后，加入全局噪声
        self._add_noise_edges(G, noise_level)

        return G

    # ---------- 新增：割权重工具 ----------
    def _cut_weight_of_partition(self, graph: nx.Graph, set1: Set[int], set2: Set[int]) -> int:
        w = 0
        # 只累加跨集边
        for u in set1:
            for v in set2:
                if graph.has_edge(u, v):
                    w += graph[u][v]['weight']
        return int(w)

    # ---------- 新增：带平衡约束的最小割 ----------
    def find_balanced_bisection(self, graph: nx.Graph) -> Tuple[List[int], List[int], int]:
        """
        平衡最小割（Minimum Bisection）
        - 小图 (n <= exact_threshold)：精确等分/近等分枚举，返回全局最优
        - 大图：Kernighan–Lin 启发式（多次随机重启取最优），支持权重
        返回: (subset1, subset2, cut_weight)
        """
        n = graph.number_of_nodes()
        nodes = list(graph.nodes())
        if n < 2:
            return [], [], 0

        # ---------- 精确枚举 ----------
        if n <= self.exact_threshold:
            best_w = float('inf')
            best_part = None

            # 允许奇数：近等分（n//2 或 n//2+1）
            sizes = [n // 2] if n % 2 == 0 else [n // 2, n // 2 + 1]
            # 固定一个锚点以避免对称重复
            anchor = nodes[0]
            rest = nodes[1:]
            for k in sizes:
                need = k - 1  # 已含anchor
                if need < 0 or need > len(rest):
                    continue
                for combo in combinations(rest, need):
                    S = set([anchor]) | set(combo)
                    T = set(nodes) - S
                    w = self._cut_weight_of_partition(graph, S, T)
                    if w < best_w:
                        best_w, best_part = w, (sorted(S), sorted(T))
            if best_part is None:
                return [], [], 0
            return best_part[0], best_part[1], int(best_w)

        # ---------- 大图：KL 启发式 ----------
        G = graph.copy()
        dummy = None
        # KL 只能等分；若 n 为奇数，加入哑元节点补足为偶数
        if n % 2 == 1:
            dummy = "__DUMMY__"
            G.add_node(dummy)
            n += 1

        def kl_once() -> Tuple[Set[int], Set[int]]:
            nodes_kl = list(G.nodes())
            random.shuffle(nodes_kl)
            half = n // 2
            A_init = set(nodes_kl[:half])
            B_init = set(nodes_kl[half:])
            A2, B2 = kernighan_lin_bisection(G, partition=(A_init, B_init), weight='weight')
            return set(A2), set(B2)

        best_w = float('inf')
        best_part = None
        for _ in range(self.kl_restarts):
            A, B = kl_once()
            if dummy is not None:
                if dummy in A: A.remove(dummy)
                if dummy in B: B.remove(dummy)
            w = self._cut_weight_of_partition(graph, A, B)
            if w < best_w:
                best_w, best_part = w, (sorted(A), sorted(B))

        if best_part is None:
            return [], [], 0
        return best_part[0], best_part[1], int(best_w)
    
    def graph_to_dict_format(self, graph: nx.Graph) -> Dict:
        """将NetworkX图转换为题目格式的字典"""
        num_nodes = len(graph.nodes)
        result = {}
        
        for i in range(num_nodes):
            result[str(i)] = {}
            for j in range(num_nodes):
                if i != j and graph.has_edge(i, j):
                    result[str(i)][str(j)] = graph[i][j]['weight']
                else:
                    result[str(i)][str(j)] = 0
        
        return result
    
    def generate_single_question(self) -> Tuple[Dict, List[List[int]], int]:
        """
        生成单个问题（平衡最小割）
        
        Returns:
            (graph_dict, answer_partition, cut_weight)
        """
        # 节点数量由 set_difficulty_params 控制
        num_nodes = self.num_nodes
        
        # 生成图
        max_attempts = 50
        for _ in range(max_attempts):
            # 使用难度对应的生成器
            graph = self.graph_generator()
            
            # ★ 使用“平衡最小割”而非全局最小割
            subset1, subset2, cut_weight = self.find_balanced_bisection(graph)
            
            # 检查是否满足最小割大小要求（过滤过易实例）
            if cut_weight >= self.min_cut_size and (abs(len(subset1) - len(subset2)) in (0, 1)):
                graph_dict = self.graph_to_dict_format(graph)
                answer = [sorted(subset1), sorted(subset2)]
                return graph_dict, answer, cut_weight
        
        # 回退：最后再生成一次
        graph = self.graph_generator()
        subset1, subset2, cut_weight = self.find_balanced_bisection(graph)
        graph_dict = self.graph_to_dict_format(graph)
        answer = [sorted(subset1), sorted(subset2)]
        return graph_dict, answer, cut_weight
    
    def set_difficulty_params(self, difficulty: str):
        """根据难度设置参数，主要控制图的结构"""
        if difficulty == "easy":
            # 目标成功率: ~0.4
            self.num_nodes = 42
            self.graph_generator = lambda: self._generate_hell_mode_graph(
                num_nodes=self.num_nodes, traitor_strength=3, noise_level=0.1)
            self.min_cut_size = 1
        elif difficulty == "medium":
            # 目标成功率: ~0.3
            self.num_nodes = 45
            self.graph_generator = lambda: self._generate_hell_mode_graph(
                num_nodes=self.num_nodes, traitor_strength=3, noise_level=0.1)
            self.min_cut_size = 1
        elif difficulty == "hard":
            # 目标成功率: ~0.3
            self.num_nodes = 45
            self.graph_generator = lambda: self._generate_hell_mode_graph(
                num_nodes=self.num_nodes, traitor_strength=3, noise_level=0.02)
        elif difficulty == "bench":
            # 目标成功率: ~0.3
            self.num_nodes = 50
            self.graph_generator = lambda: self._generate_hell_mode_graph(
                num_nodes=self.num_nodes, traitor_strength=3, noise_level=0.02)
    
    def generate_questions(self, num_questions: int, difficulty: str = "medium") -> Dict:
        """
        生成指定数量的问题（平衡最小割）
        
        Args:
            num_questions: 题目数量
            difficulty: 难度级别 ("easy", "medium", "hard")
        """
        # 根据难度调整参数
        self.set_difficulty_params(difficulty)
        
        questions = {}
        answers = {}
        
        for i in range(1, num_questions + 1):
            graph_dict, answer, cut_weight = self.generate_single_question()
            
            questions[f"question{i}"] = graph_dict
            answers[f"question{i}"] = {
                "answer": answer,
                "cut_weight": cut_weight
            }
        
        # 确定big_small标记
        avg_nodes = sum(len(q) for q in questions.values()) / len(questions) if questions else 0
        big_small = 'small'
        
        return {
            "big_small": big_small,
            "questions": questions,
            "answers": answers,  # 包含答案用于验证
            "metadata": {
                "difficulty": difficulty,
                "num_questions": num_questions,
                "avg_nodes": avg_nodes,
                "generation_params": {
                    "num_nodes_range": self.num_nodes_range,
                    "edge_density": self.edge_density,
                    "weight_range": self.weight_range,
                    "min_cut_size": self.min_cut_size,
                    "exact_threshold": self.exact_threshold,
                    "kl_restarts": self.kl_restarts
                }
            }
        }
    
    def generate_mixed_difficulty_questions(self, easy_count: int = 0, medium_count: int = 0, hard_count: int = 0, bench_count: int = 0) -> Dict:
        """
        生成混合难度的问题集（平衡最小割），顺序为easy->medium->hard->bench
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
            for i in range(1, easy_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (easy_{i})...")
                graph_dict, answer, cut_weight = self.generate_single_question()
                
                key = f"easy_question{i}"
                all_questions[key] = graph_dict
                all_answers[key] = {
                    "answer": answer,
                    "cut_weight": cut_weight,
                    "difficulty": "easy"
                }
            
            all_metadata["easy"] = {
                "count": easy_count,
                "params": {
                    "num_nodes": 30,
                    "structure": "polluted_community",
                    "intra_density": 0.8,
                    "inter_edges": 4,
                    "noise_level": 0.1
                }
            }
        
        # 生成中等题目
        if medium_count > 0:
            print(f"\n=== 生成 {medium_count} 道中等题目 ===")
            self.set_difficulty_params("medium")
            for i in range(1, medium_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (medium_{i})...")
                graph_dict, answer, cut_weight = self.generate_single_question()
                
                key = f"medium_question{i}"
                all_questions[key] = graph_dict
                all_answers[key] = {
                    "answer": answer,
                    "cut_weight": cut_weight,
                    "difficulty": "medium"
                }
            
            all_metadata["medium"] = {
                "count": medium_count,
                "params": {
                    "num_nodes": 42,
                    "structure": "very_blurry_community",
                    "intra_density": 0.7,
                    "inter_edges": 8,
                    "noise_level": 0.15
                }
            }
        
        # 生成困难题目
        if hard_count > 0:
            print(f"\n=== 生成 {hard_count} 道困难题目 ===")
            self.set_difficulty_params("hard")
            for i in range(1, hard_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (hard_{i})...")
                graph_dict, answer, cut_weight = self.generate_single_question()
                
                key = f"hard_question{i}"
                all_questions[key] = graph_dict
                all_answers[key] = {
                    "answer": answer,
                    "cut_weight": cut_weight,
                    "difficulty": "hard"
                }
            
            all_metadata["hard"] = {
                "count": hard_count,
                "params": {
                    "num_nodes": 42,
                    "structure": "reinforced_hell_mode",
                    "traitor_strength": 3,
                    "noise_level": 0.1
                }
            }
        
        # 生成基准题目
        if bench_count > 0:
            print(f"\n=== 生成 {bench_count} 道基准题目 ===")
            self.set_difficulty_params("bench")
            for i in range(1, bench_count + 1):
                current_count += 1
                print(f"生成第 {current_count}/{total_count} 题 (bench_{i})...")
                graph_dict, answer, cut_weight = self.generate_single_question()
                
                key = f"bench_question{i}"
                all_questions[key] = graph_dict
                all_answers[key] = {
                    "answer": answer,
                    "cut_weight": cut_weight,
                    "difficulty": "bench"
                }
            
            all_metadata["bench"] = {
                "count": bench_count,
                "params": {
                    "num_nodes": 50,
                    "structure": "reinforced_hell_mode",
                    "traitor_strength": 3,
                    "noise_level": 0.02
                }
            }
        
        # 计算平均节点数
        avg_nodes = sum(len(q) for q in all_questions.values()) / len(all_questions) if all_questions else 0
        big_small = "small"
        
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
                "avg_nodes": avg_nodes,
                "difficulties": all_metadata
            }
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='生成平衡最小割（Minimum Bisection）问题数据集',
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
    parser.add_argument('--output', type=str, default='generated_questions.json', help='输出文件名')
    
    # 高级参数
    parser.add_argument('--num_nodes_min', type=int, default=None, help='最小节点数 (覆盖默认值)')
    parser.add_argument('--num_nodes_max', type=int, default=None, help='最大节点数 (覆盖默认值)')
    parser.add_argument('--edge_density', type=float, default=None, help='边密度 (0-1) (覆盖默认值)')
    parser.add_argument('--weight_min', type=int, default=1, help='最小边权重')
    parser.add_argument('--weight_max', type=int, default=6, help='最大边权重')
    parser.add_argument('--min_cut_size', type=int, default=None, help='最小割的最小大小 (覆盖默认值)')
    
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
    
    # 创建生成器
    generator = MinimumCutGenerator(
        weight_range=(args.weight_min, args.weight_max)
    )
    
    # 应用自定义参数
    if args.num_nodes_min and args.num_nodes_max:
        generator.num_nodes_range = (args.num_nodes_min, args.num_nodes_max)
    if args.edge_density is not None:
        generator.edge_density = args.edge_density
    if args.min_cut_size is not None:
        generator.min_cut_size = args.min_cut_size
    
    print("="*60)
    print("平衡最小割（Minimum Bisection）问题生成器")
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
        
        # 保存答案文件
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
            output_data = {
                "big_small": dataset["big_small"],
                "questions": dataset["questions"]
            }
            save_json_compact(output_data, args.output)
            print(f"混合题目文件: {args.output}")
        
        # 总是生成包含答案的文件
        answer_file = args.output.replace('.json', '_with_answers.json')
        with open(answer_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"答案文件: {answer_file}")
    
    print(f"\n生成统计:")
    if use_traditional_mode:
        print(f"  难度: {dataset['metadata']['difficulty']}")
        print(f"  题目数量: {dataset['metadata']['num_questions']}")
        print(f"  平均节点数: {dataset['metadata']['avg_nodes']:.1f}")
    else:
        print(f"  简单题目: {dataset['metadata']['easy_count']}")
        print(f"  中等题目: {dataset['metadata']['medium_count']}")
        print(f"  困难题目: {dataset['metadata']['hard_count']}")
        print(f"  基准题目: {dataset['metadata']['bench_count']}")
        print(f"  总题目数: {dataset['metadata']['total_count']}")
        print(f"  平均节点数: {dataset['metadata']['avg_nodes']:.1f}")
    
    # 显示第一题的示例
    if dataset["questions"]:
        first_question_key = list(dataset["questions"].keys())[0]
        first_question = dataset["questions"][first_question_key]
        first_answer = dataset["answers"][first_question_key]
        print(f"\n示例题目 ({first_question_key}):")
        print(f"图节点数: {len(first_question)}")
        print(f"平衡最小割: {first_answer['answer']}")
        print(f"割权重: {first_answer['cut_weight']}")


if __name__ == "__main__":
    main()