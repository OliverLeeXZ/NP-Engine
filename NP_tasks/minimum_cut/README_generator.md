# 最小割问题生成器

一个功能强大的最小割（Minimum Cut）问题生成器，支持多种难度级别和灵活的参数配置。该工具可以生成用于算法训练和测试的高质量最小割问题数据集。

## 🌟 主要特性

- **混合难度生成**: 支持同时生成简单、中等、困难三种难度的题目
- **智能图生成**: 自动生成连通图并确保有效的最小割
- **灵活输出**: 支持混合文件或分离文件输出
- **高质量算法**: 使用 Stoer-Wagner 算法精确计算最小割
- **紧凑格式**: 优化的 JSON 输出格式，节省存储空间
- **参数可调**: 支持自定义节点数、边密度、权重等参数

## 📦 依赖安装

```bash
pip install networkx
```

## 🚀 快速开始

### 基本用法

```bash
# 生成混合难度题目（推荐）
python generate_questions.py --easy 5 --medium 3 --hard 2

# 只生成简单题目
python generate_questions.py --easy 10 --output easy_questions.json

# 传统模式（兼容旧版本）
python generate_questions.py --num_questions 5 --difficulty medium
```

## 🎯 难度级别

| 难度 | 节点数范围 | 边密度 | 最小割大小 | 说明 |
|------|------------|--------|------------|------|
| **简单** | 7-12 | 0.3 | ≥1 | 小规模图，稀疏连接 |
| **中等** | 12-18 | 0.5 | ≥2 | 中等规模，适中连接 |
| **困难** | 18-25 | 0.7 | ≥3 | 大规模图，密集连接 |

## 📝 详细用法

### 混合难度模式（推荐）

```bash
# 生成 5 个简单 + 3 个中等 + 2 个困难题目
python generate_questions.py --easy 5 --medium 3 --hard 2 --output mixed_questions.json

# 为每个难度生成单独文件
python generate_questions.py --easy 5 --medium 5 --hard 5 --separate --output questions

# 只生成特定难度
python generate_questions.py --medium 8 --output medium_only.json
```

### 传统模式（兼容性）

```bash
# 生成指定数量的单一难度题目
python generate_questions.py --num_questions 10 --difficulty hard --output hard_questions.json
```

### 高级参数配置

```bash
# 自定义节点数范围
python generate_questions.py --easy 5 --num_nodes_min 3 --num_nodes_max 8

# 自定义边密度和权重
python generate_questions.py --medium 5 --edge_density 0.6 --weight_min 1 --weight_max 10

# 设置最小割大小要求
python generate_questions.py --hard 3 --min_cut_size 5
```

## 📋 命令行参数

### 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--easy N` | 生成 N 个简单题目 | 0 |
| `--medium M` | 生成 M 个中等题目 | 0 |
| `--hard P` | 生成 P 个困难题目 | 0 |
| `--output FILE` | 输出文件名 | `generated_questions.json` |
| `--separate` | 为每个难度生成单独文件 | False |

### 兼容性参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num_questions N` | 题目数量（传统模式） | None |
| `--difficulty LEVEL` | 难度级别（传统模式） | medium |

### 高级参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num_nodes_min N` | 最小节点数 | 根据难度自动设置 |
| `--num_nodes_max N` | 最大节点数 | 根据难度自动设置 |
| `--edge_density F` | 边密度 (0-1) | 根据难度自动设置 |
| `--weight_min N` | 最小边权重 | 1 |
| `--weight_max N` | 最大边权重 | 6 |
| `--min_cut_size N` | 最小割的最小大小 | 根据难度自动设置 |

## 📊 输出格式

### 题目文件格式

```json
{
  "big_small": "small",
  "questions": {
    "easy_question1": {
      "0": {"1": 3, "2": 0, "3": 2},
      "1": {"0": 3, "2": 1, "3": 0},
      "2": {"0": 0, "1": 1, "3": 4},
      "3": {"0": 2, "1": 0, "2": 4}
    },
    "medium_question1": {
      ...
    }
  }
}
```

### 答案文件格式

答案文件包含完整的解题信息：

```json
{
  "questions": { ... },
  "answers": {
    "easy_question1": {
      "answer": [[0, 1], [2, 3]],
      "cut_weight": 4,
      "difficulty": "easy"
    }
  },
  "metadata": {
    "total_count": 10,
    "easy_count": 5,
    "medium_count": 3,
    "hard_count": 2,
    "avg_nodes": 8.5
  }
}
```

## 🧩 算法原理

### 最小割问题
最小割问题是图论中的经典问题，目标是找到将图分成两个连通分量的最小权重边集。

**问题定义**：
- 给定无向带权图 G = (V, E)
- 找到顶点集的划分 (S, T)，使得割集的总权重最小
- 割集 = {(u,v) ∈ E | u ∈ S, v ∈ T}

### 算法实现
1. **Stoer-Wagner 算法**：全局最小割的精确算法
2. **连通性保证**：使用最小生成树确保图连通
3. **密度控制**：根据边密度参数添加额外边
4. **质量验证**：确保生成的割满足大小要求

## 🎯 使用场景

- **算法研究**：生成标准测试集
- **性能评估**：不同规模和复杂度的基准测试
- **教学演示**：图论课程的实例生成
- **竞赛训练**：算法竞赛题目准备

## 📈 性能特点

- **高效生成**：优化的图构造算法
- **质量保证**：多次尝试确保问题有效性
- **内存友好**：紧凑的数据表示
- **可扩展性**：支持大规模图生成

## 🔧 自定义扩展

### 添加新难度级别

```python
def set_difficulty_params(self, difficulty: str):
    if difficulty == "extreme":
        self.num_nodes_range = (20, 30)
        self.edge_density = 0.8
        self.min_cut_size = 5
```

### 自定义图生成策略

```python
def custom_graph_generator(self, num_nodes: int):
    # 实现自定义图生成逻辑
    pass
```

## 🐛 故障排除

### 常见问题

1. **生成失败**：检查参数是否合理，特别是 `min_cut_size`
2. **内存不足**：减少节点数或边密度
3. **生成时间过长**：降低难度或减少题目数量

### 调试建议

```bash
# 使用较小参数测试
python generate_questions.py --easy 1 --num_nodes_max 5

# 检查生成的图连通性
python -c "import networkx as nx; # 验证代码"
```

## 📄 示例文件

运行示例：
```bash
python generate_questions.py --easy 2 --medium 2 --hard 1 --output example.json
```

这将生成包含 5 个不同难度题目的数据集。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个工具！

## 📜 许可证

MIT License

---

**最小割问题生成器** - 为图论算法研究和教学提供高质量数据集生成工具。 