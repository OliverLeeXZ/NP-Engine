# 集合覆盖问题生成器

一个功能强大的集合覆盖（Set Cover Problem）问题生成器，支持多种难度级别和灵活的参数配置。该工具可以生成用于算法训练和测试的高质量集合覆盖问题数据集。

## 🌟 主要特性

- **混合难度生成**: 支持同时生成简单、中等、困难三种难度的题目
- **智能问题构造**: 自动生成可解的集合覆盖问题实例
- **灵活输出**: 支持混合文件或分离文件输出
- **可调参数**: 支持自定义全集大小、子集数量、覆盖密度等参数
- **紧凑格式**: 优化的 JSON 输出格式，节省存储空间
- **解答保证**: 确保生成的每个问题都有有效解

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

| 难度 | 全集大小 | 子集数量 | 子集大小因子 | 说明 |
|------|----------|----------|--------------|------|
| **简单** | 10-20 | 5-10 | 0.5 | 小规模问题，子集覆盖度高 |
| **中等** | 20-40 | 10-25 | 0.3 | 中等规模，适中覆盖密度 |
| **困难** | 40-80 | 25-50 | 0.15 | 大规模问题，稀疏覆盖 |

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

## 📋 命令行参数

### 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--easy N` | 生成 N 个简单题目 | 0 |
| `--medium M` | 生成 M 个中等题目 | 0 |
| `--hard P` | 生成 P 个困难题目 | 0 |
| `--output FILE` | 输出文件名 | `generated_set_cover_questions.json` |
| `--separate` | 为每个难度生成单独文件 | False |

### 兼容性参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num_questions N` | 题目数量（传统模式） | None |
| `--difficulty LEVEL` | 难度级别（传统模式） | medium |

## 📊 输出格式

### 题目文件格式

```json
{
  "big_small": "small",
  "questions": {
    "easy_question1": {
      "U": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
      "S": {
        "0": [0, 2, 4, 6, 8],
        "1": [1, 3, 5, 7, 9],
        "2": [0, 1, 2, 3],
        "3": [6, 7, 8, 9]
      }
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
      "answer": [0, 1],
      "difficulty": "easy"
    }
  },
  "metadata": {
    "total_count": 10,
    "easy_count": 5,
    "medium_count": 3,
    "hard_count": 2,
    "avg_elements": 25.8
  }
}
```

## 🧩 算法原理

### 集合覆盖问题
集合覆盖问题是计算机科学中的经典 NP-完全问题，目标是找到最少数量的子集来覆盖全集中的所有元素。

**问题定义**：
- 给定全集 U = {1, 2, ..., n}
- 给定子集族 S = {S₁, S₂, ..., Sₘ}，其中每个 Sᵢ ⊆ U
- 找到最小的子集合 C ⊆ S，使得 ∪(Sᵢ ∈ C) Sᵢ = U

### 生成算法

1. **随机子集生成**: 根据难度参数生成随机大小的子集
2. **覆盖保证**: 确保所有元素都被至少一个子集覆盖
3. **解的存在性**: 通过补充机制保证问题可解
4. **质量验证**: 检查生成问题的有效性

## 🎯 使用场景

- **算法研究**: NP-完全问题的近似算法测试
- **性能评估**: 贪心算法、启发式算法的基准测试
- **教学演示**: 组合优化课程的实例生成
- **竞赛训练**: 算法竞赛的集合覆盖问题准备

## 📈 性能特点

- **可解保证**: 所有生成的问题都保证有解
- **参数控制**: 精确控制问题规模和复杂度
- **高效生成**: 优化的问题构造算法
- **内存友好**: 紧凑的数据表示

## 🔧 自定义扩展

### 添加新难度级别

```python
def set_difficulty_params(self, difficulty: str):
    if difficulty == "extreme":
        self.num_elements_range = (80, 150)
        self.num_subsets_range = (50, 100)
        self.subset_size_factor = 0.1
```

### 自定义子集生成策略

```python
def custom_subset_generator(self, num_elements: int):
    # 实现自定义子集生成逻辑
    # 例如：基于特定分布的子集大小
    pass
```

## 🐛 故障排除

### 常见问题

1. **无解问题**: 生成器会自动修复，确保所有元素被覆盖
2. **内存不足**: 减少全集大小或子集数量
3. **生成时间过长**: 降低难度或减少题目数量

### 调试建议

```bash
# 使用较小参数测试
python generate_questions.py --easy 1 --output test.json

# 检查生成的问题完整性
python -c "
import json
with open('test.json') as f:
    data = json.load(f)
    q = list(data['questions'].values())[0]
    print(f'全集: {q[\"U\"]}')
    print(f'子集: {q[\"S\"]}')
"
```

## 📊 算法复杂度分析

### 时间复杂度
- **问题生成**: O(m × k)，其中 m 是子集数，k 是平均子集大小
- **覆盖检查**: O(n + m × k)，其中 n 是全集大小

### 空间复杂度
- **存储空间**: O(n + m × k)
- **生成过程**: O(n) 额外空间

## 💡 优化建议

### 针对不同应用场景的参数调优

**贪心算法测试**:
```bash
python generate_questions.py --medium 10 --output greedy_test.json
```

**精确算法测试**:
```bash
python generate_questions.py --easy 5 --output exact_test.json
```

**大规模近似算法测试**:
```bash
python generate_questions.py --hard 3 --output approx_test.json
```

## 📄 示例文件

运行示例：
```bash
python generate_questions.py --easy 2 --medium 2 --hard 1 --output example.json
```

这将生成包含 5 个不同难度题目的数据集，涵盖从小规模到大规模的集合覆盖问题。

## 🔬 理论背景

### NP-完全性
集合覆盖问题是 Karp 21 个 NP-完全问题之一，在组合优化和理论计算机科学中具有重要地位。

### 近似算法
- **贪心算法**: 达到 ln(n) 近似比
- **线性规划松弛**: 提供下界估计
- **原始对偶算法**: 理论保证的近似方案

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个工具！

### 开发建议
- 添加新的子集生成策略
- 优化大规模问题的生成效率
- 增加问题验证和质量检查功能

## 📜 许可证

MIT License

---

**集合覆盖问题生成器** - 为组合优化研究和教学提供高质量数据集生成工具。 