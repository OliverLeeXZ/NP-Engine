# 🚗 旅行商问题生成器 (TSP Generator)

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个强大的旅行商问题（Traveling Salesman Problem, TSP）数据集生成器，支持多难度级别和灵活的参数配置。

## 📋 功能特点

- ✨ **多难度支持**: 简单、中等、困难三个难度级别
- 🎯 **混合生成**: 可同时生成不同难度的题目
- 📂 **灵活输出**: 支持混合文件或分离文件输出
- ⚙️ **参数可调**: 城市数量、距离范围完全可定制
- 🔄 **向后兼容**: 保持传统单一难度生成模式

## 🏗️ 算法原理

### 旅行商问题简介
旅行商问题（TSP）是一个经典的NP完全问题：给定一系列城市和每对城市之间的距离，求解访问每个城市一次并回到起始城市的最短可能路线。

### 生成算法
1. **城市数量确定**: 根据难度级别随机选择城市数量
2. **距离矩阵生成**: 创建对称的距离矩阵，城市间距离随机生成
3. **数据格式化**: 转换为标准的JSON格式输出

## 🎮 难度级别

| 难度 | 城市数量 | 复杂度特点 |
|------|----------|------------|
| **Easy** | 8-15 | 小规模，适合初学者 |
| **Medium** | 15-25 | 中等规模，平衡挑战性 |
| **Hard** | 35-45 | 大规模，高计算复杂度 |

## 🚀 快速开始

### 安装依赖
```bash
# 仅需要Python标准库，无额外依赖
python3 --version  # 确保Python 3.7+
```

### 基本使用

#### 1. 混合难度生成
```bash
# 生成5个简单、3个中等、2个困难题目
python generate_questions.py --easy 5 --medium 3 --hard 2 --output mixed_questions.json
```

#### 2. 单一难度生成
```bash
# 只生成10个简单题目
python generate_questions.py --easy 10 --output easy_questions.json

# 只生成5个困难题目
python generate_questions.py --hard 5 --output hard_questions.json
```

#### 3. 分离文件输出
```bash
# 为每个难度生成单独文件
python generate_questions.py --easy 5 --medium 5 --hard 5 --separate --output tsp_questions
# 输出: tsp_questions_easy.json, tsp_questions_medium.json, tsp_questions_hard.json
```

## 📚 详细用法

### 命令行参数

#### 核心参数
- `--easy N`: 生成 N 个简单难度题目
- `--medium M`: 生成 M 个中等难度题目  
- `--hard P`: 生成 P 个困难难度题目
- `--output FILE`: 指定输出文件名
- `--separate`: 为每个难度生成单独文件

#### 传统模式（兼容性）
- `--num_questions N`: 生成 N 个题目（传统模式）
- `--difficulty LEVEL`: 指定难度级别（easy/medium/hard）

#### 高级参数
- `--num_cities_min N`: 自定义最小城市数
- `--num_cities_max M`: 自定义最大城市数
- `--dist_min X`: 最小距离值（默认：10）
- `--dist_max Y`: 最大距离值（默认：100）

### 使用示例

#### 🎯 场景1：研究实验
```bash
# 生成大量不同难度的数据用于模型训练
python generate_questions.py --easy 100 --medium 50 --hard 20 --output research_dataset.json
```

#### 🎯 场景2：教学使用  
```bash
# 为不同学习阶段生成题目
python generate_questions.py --easy 20 --medium 10 --separate --output teaching_materials
```

#### 🎯 场景3：算法测试
```bash
# 生成特定规模的题目
python generate_questions.py --medium 10 --num_cities_min 12 --num_cities_max 12 --output test_12cities.json
```

#### 🎯 场景4：传统模式
```bash
# 使用旧版本兼容语法
python generate_questions.py --num_questions 5 --difficulty medium --output legacy_output.json
```

## 📄 输出格式

### 标准JSON格式
```json
{
  "big_small": "small",
  "questions": {
    "easy_question1": {
      "0": {"0": 0, "1": 45, "2": 32, "3": 78},
      "1": {"0": 45, "1": 0, "2": 56, "3": 23},
      "2": {"0": 32, "1": 56, "2": 0, "3": 41},
      "3": {"0": 78, "1": 23, "2": 41, "3": 0}
    },
    "medium_question1": {
      "0": {"0": 0, "1": 23, "2": 67, "3": 12, "4": 89, "5": 34},
      "1": {"0": 23, "1": 0, "2": 45, "3": 78, "4": 56, "5": 91},
      // ...更多城市
    }
  }
}
```

### 文件命名规则

#### 混合模式
- 输入：`--output dataset.json`
- 输出：`dataset.json`（包含所有难度）

#### 分离模式
- 输入：`--output dataset --separate`  
- 输出：
  - `dataset_easy.json`
  - `dataset_medium.json`
  - `dataset_hard.json`

## 🔧 高级配置

### 自定义难度参数
```bash
# 生成特定规模的题目
python generate_questions.py \
  --easy 5 --medium 3 --hard 2 \
  --num_cities_min 8 --num_cities_max 12 \
  --dist_min 1 --dist_max 50 \
  --output custom_tsp.json
```

### 批量生成脚本
```bash
#!/bin/bash
# 批量生成不同配置的数据集

# 小规模数据集
python generate_questions.py --easy 20 --output small_dataset.json

# 中规模数据集  
python generate_questions.py --medium 15 --output medium_dataset.json

# 大规模数据集
python generate_questions.py --hard 10 --output large_dataset.json

# 混合数据集
python generate_questions.py --easy 10 --medium 10 --hard 10 --separate --output mixed_dataset
```

## 📊 生成统计示例

```
============================================================
旅行商问题生成器
============================================================
模式: 混合难度模式
简单题目: 5
中等题目: 3
困难题目: 2
总计: 10

=== 生成 5 道简单题目 ===
生成第 1/10 题 (easy_1, 城市数范围: (4, 8))...
生成第 2/10 题 (easy_2, 城市数范围: (4, 8))...
...

=== 生成 3 道中等题目 ===
生成第 6/10 题 (medium_1, 城市数范围: (8, 15))...
...

=== 生成 2 道困难题目 ===
生成第 9/10 题 (hard_1, 城市数范围: (15, 25))...
...

混合题目文件: mixed_questions.json

生成统计:
  简单题目: 5
  中等题目: 3  
  困难题目: 2
  总题目数: 10
  平均城市数: 11.2

示例题目 (easy_question1):
城市数量: 6
```

## 🤝 贡献指南

欢迎提交问题报告和功能请求！

### 开发环境设置
```bash
git clone <repository>
cd TSP
python generate_questions.py --help
```

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🔗 相关资源

- [旅行商问题 - 维基百科](https://zh.wikipedia.org/wiki/%E6%97%85%E8%A1%8C%E6%8E%A8%E9%94%80%E5%91%98%E9%97%AE%E9%A2%98)
- [TSP算法实现参考](https://github.com/topics/traveling-salesman-problem)
- [图论与组合优化](https://en.wikipedia.org/wiki/Travelling_salesman_problem) 