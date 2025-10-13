# 子集和问题生成器

一个功能强大的子集和（Subset Sum Problem）问题生成器，支持多种难度级别和灵活的参数配置。该工具专门生成"最大基数变体"的子集和问题，即找到和为目标值且包含元素数量最多的子集。

## 🌟 主要特性

- **混合难度生成**: 支持同时生成简单、中等、困难三种难度的题目
- **最大基数变体**: 专注于寻找包含最多元素的目标和子集
- **智能问题构造**: 预先构建解集确保每个问题都有有效解
- **灵活输出**: 支持混合文件或分离文件输出
- **可调参数**: 支持自定义数字总数、解集大小、数值范围等参数
- **紧凑格式**: 优化的 JSON 输出格式，节省存储空间
- **解答保证**: 确保生成的每个问题都有唯一最优解

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

| 难度 | 数字总数 | 解集大小 | 数值范围 | 说明 |
|------|----------|----------|----------|------|
| **简单** | 8-15 | 3-5 | 1-20 | 小规模问题，较小数值 |
| **中等** | 15-25 | 5-8 | 1-50 | 中等规模，适中数值 |
| **困难** | 25-40 | 8-12 | 1-100 | 大规模问题，较大数值 |

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
# 自定义数字总数范围
python generate_questions.py --easy 5 --num_total_min 10 --num_total_max 20

# 自定义解集大小和数值范围
python generate_questions.py --medium 5 --solution_size_min 4 --solution_size_max 6 --value_min 5 --value_max 30
```

## 📋 命令行参数

### 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--easy N` | 生成 N 个简单题目 | 0 |
| `--medium M` | 生成 M 个中等题目 | 0 |
| `--hard P` | 生成 P 个困难题目 | 0 |
| `--output FILE` | 输出文件名 | `generated_subset_sum_questions.json` |
| `--separate` | 为每个难度生成单独文件 | False |

### 兼容性参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num_questions N` | 题目数量（传统模式） | None |
| `--difficulty LEVEL` | 难度级别（传统模式） | medium |

### 高级参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num_total_min N` | 数字总数最小值 | 根据难度自动设置 |
| `--num_total_max N` | 数字总数最大值 | 根据难度自动设置 |
| `--solution_size_min N` | 解集大小最小值 | 根据难度自动设置 |
| `--solution_size_max N` | 解集大小最大值 | 根据难度自动设置 |
| `--value_min N` | 数值范围最小值 | 根据难度自动设置 |
| `--value_max N` | 数值范围最大值 | 根据难度自动设置 |

## 📊 输出格式

### 题目文件格式

```json
{
  "big_small": "big",
  "questions": {
    "easy_question1": {
      "target": 45,
      "numbers": {
        "0": 12, "1": 8, "2": 15, "3": 20,
        "4": 3, "5": 7, "6": 25, "7": 11
      }
    },
    "medium_question1": {
      "target": 78,
      "numbers": {
        "0": 15, "1": 22, "2": 8, "3": 33,
        ...
      }
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
      "answer": [0, 2, 3],
      "difficulty": "easy"
    }
  },
  "metadata": {
    "total_count": 10,
    "easy_count": 5,
    "medium_count": 3,
    "hard_count": 2,
    "avg_numbers": 18.5
  }
}
```

## 🧩 算法原理

### 子集和问题（最大基数变体）
这是经典子集和问题的一个特殊变体，目标是在所有和为目标值的子集中找到包含元素最多的那个。

**问题定义**：
- 给定数字集合 S = {s₁, s₂, ..., sₙ}
- 给定目标和 T
- 找到子集 A ⊆ S，使得：
  1. ∑(a ∈ A) a = T
  2. |A| 最大（包含元素数量最多）

### 生成算法

1. **解集优先构造**: 首先生成期望的解集，确保问题可解
2. **目标和计算**: 根据解集计算目标和
3. **干扰项添加**: 添加不影响最优解的干扰数字
4. **随机打乱**: 打乱数字顺序，隐藏解的结构
5. **质量验证**: 确保生成的问题有唯一最优解

### 算法特点

- **解的唯一性**: 通过精心设计确保最大基数解的唯一性
- **难度控制**: 通过调整数字范围和干扰项控制求解难度
- **可扩展性**: 支持大规模问题生成

## 🎯 使用场景

- **动态规划算法测试**: 测试子集和动态规划解法
- **启发式算法验证**: 验证贪心和近似算法效果
- **算法教学**: 组合优化课程的实例生成
- **竞赛训练**: 算法竞赛的子集和问题练习
- **性能基准测试**: 不同算法的效率对比

## 📈 性能特点

- **解答保证**: 100% 的问题都有有效解
- **最优性保证**: 确保解的最大基数特性
- **高效生成**: 优化的问题构造算法
- **内存友好**: 紧凑的数据表示

## 🔧 自定义扩展

### 添加新难度级别

```python
def set_difficulty_params(self, difficulty: str):
    if difficulty == "extreme":
        self.total_numbers_range = (40, 60)
        self.solution_size_range = (12, 18)
        self.value_range = (1, 200)
```

### 自定义解集生成策略

```python
def custom_solution_generator(self, solution_size: int):
    # 实现自定义解集生成逻辑
    # 例如：基于特定分布的数值选择
    pass
```

## 🐛 故障排除

### 常见问题

1. **解集冲突**: 生成器会自动调整确保解的唯一性
2. **数值溢出**: 调整数值范围避免过大的目标和
3. **生成时间过长**: 降低难度或减少题目数量

### 调试建议

```bash
# 使用较小参数测试
python generate_questions.py --easy 1 --num_total_max 10 --output test.json

# 检查生成的问题有效性
python -c "
import json
with open('test.json') as f:
    data = json.load(f)
    q = list(data['questions'].values())[0]
    print(f'目标和: {q[\"target\"]}')
    print(f'数字: {q[\"numbers\"]}')
"
```

## 📊 算法复杂度分析

### 时间复杂度
- **问题生成**: O(n)，其中 n 是数字总数
- **验证阶段**: O(n × target)，动态规划验证

### 空间复杂度
- **存储空间**: O(n)
- **生成过程**: O(n) 额外空间

## 💡 问题特点

### 与标准子集和问题的区别

1. **标准子集和**: 只需找到任一和为 T 的子集
2. **最大基数变体**: 在所有和为 T 的子集中选择元素最多的

### 实际应用价值

- **资源分配**: 在预算约束下最大化资源利用
- **组合优化**: 多目标优化问题的简化模型
- **算法设计**: 测试贪心策略的有效性

## 📄 示例文件

运行示例：
```bash
python generate_questions.py --easy 2 --medium 2 --hard 1 --output example.json
```

这将生成包含 5 个不同难度题目的数据集，每个问题都保证有最大基数解。

## 🔬 理论背景

### NP-完全性
子集和问题是经典的 NP-完全问题，最大基数变体增加了额外的优化目标。

### 解法策略
- **动态规划**: O(n × target) 的精确解法
- **贪心近似**: 基于数值密度的启发式方法
- **分支限界**: 适用于小规模精确求解

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个工具！

### 开发建议
- 添加更多约束条件的变体
- 优化大规模问题的生成效率
- 增加解的多样性验证功能

## 📜 许可证

MIT License

---

**子集和问题生成器** - 为组合优化研究和算法教学提供高质量的最大基数子集和问题生成工具。 