# 最大团（Maximum Clique）问题造题脚本使用说明

## 概述

这是一个基于规则的最大团问题（Maximum Clique Problem）造题脚本。其目标是生成一个无向图，并要求解答者找到其中最大的顶点集合（即"团"），使得集合中任意两个不同的顶点之间都有一条边直接相连。

为了确保每个生成的问题都必然有解，此脚本采用了基于图的"补"运算的巧妙策略。该策略利用了最大团问题与最大独立集问题的对偶关系：**一个图 G 的最大团，等于其补图 G' 的最大独立集**。

生成过程如下：
1.  首先，使用"植入解"的方法生成一个图 `G`，并确保其中包含一个已知大小的最大独立集 `I`。
2.  然后，计算图 `G` 的补图 `G'`。在补图 `G'` 中，原图 `G` 中任意两个未连接的顶点现在都将是连接的。
3.  因此，原图中的独立集 `I`（其中所有顶点两两不相连）在补图 `G'` 中就变成了一个团（其中所有顶点两两相连）。
4.  最终输出的题目就是这个补图 `G'`，其保证解就是我们预先植入的集合 `I`。

## 使用方法

### 🎯 **灵活的混合难度生成** (推荐)

脚本支持同时生成不同难度的题目，你可以按需指定每种难度的数量：

```bash
# 生成5道简单、3道中等、2道困难题目（混合到一个文件）
python generate_questions.py --easy 5 --medium 3 --hard 2

# 生成10道简单题目和5道困难题目
python generate_questions.py --easy 10 --hard 5

# 只生成8道中等题目
python generate_questions.py --medium 8
```

### 📁 **分离输出模式**

使用 `--separate` 参数可以为每种难度生成单独的文件：

```bash
# 为每种难度生成独立文件
python generate_questions.py --easy 5 --medium 3 --hard 2 --separate

# 这将生成：
# - generated_maximum_clique_questions_easy.json
# - generated_maximum_clique_questions_medium.json  
# - generated_maximum_clique_questions_hard.json
```

### 🎛️ **自定义输出文件名**

```bash
python generate_questions.py --easy 3 --medium 2 --hard 1 --output my_clique_dataset.json
```

## 难度级别详解

### 🟢 **简单（Easy）**
- **顶点数量**: 15-25个
- **团大小**: 3-5个顶点
- **特点**: 补图相对稀疏，团结构比较明显，容易识别

### 🟡 **中等（Medium）**  
- **顶点数量**: 35-50个
- **团大小**: 5-8个顶点
- **特点**: 图复杂度适中，需要一定的搜索技巧

### 🔴 **困难（Hard）**
- **顶点数量**: 55-70个
- **团大小**: 8-12个顶点
- **特点**: 补图相对稠密，在大量边中识别最大全连接子图变得更加困难

## 核心参数

- `--easy N`: 生成N道简单题目 (默认: 0)
- `--medium M`: 生成M道中等题目 (默认: 0)
- `--hard P`: 生成P道困难题目 (默认: 0)
- `--output FILE`: 指定输出文件名 (默认: `generated_maximum_clique_questions.json`)
- `--separate`: 为每种难度生成单独文件 (可选)

## 使用示例

### 1. 快速开始 - 生成混合难度数据集
```bash
python generate_questions.py --easy 10 --medium 5 --hard 3
```

### 2. 单一难度大量生成
```bash
python generate_questions.py --medium 20
```

### 3. 分离输出 - 便于分类使用
```bash
python generate_questions.py --easy 15 --hard 10 --separate
```

### 4. 研究型用途 - 精确控制
```bash
python generate_questions.py --easy 5 --medium 5 --hard 5 --output research_clique_set.json
```

## 输出文件

脚本会生成以下文件：

### 📄 **题目文件** 
- **混合模式**: `output_name.json`
- **分离模式**: `output_name_easy.json`, `output_name_medium.json`, `output_name_hard.json`
- 包含图的邻接表表示，采用紧凑JSON格式
- 提供给解答者的文件

### 📋 **答案文件**
- `output_name_with_answers.json`
- 包含完整题目、标准答案和元数据
- 用于验证和评估

### 📊 **生成统计**

脚本运行后会显示详细统计信息：
```
生成完成!
题目文件: my_dataset.json
答案文件: my_dataset_with_answers.json
简单题目: 5 道
中等题目: 3 道
困难题目: 2 道
总题目数: 10 道
平均顶点数: 22.3
```

### 题目命名规则

- **混合模式**: `easy_question1`, `medium_question1`, `hard_question1`, ...
- **分离模式**: `question1`, `question2`, `question3`, ...

## 输出格式示例

```json
{
  "big_small": "big",
  "questions": {
    "easy_question1": {
      "0": [1, 2, 3],
      "1": [0, 2],
      "2": [0, 1],
      "3": [0, 4],
      "4": [3]
    },
    "medium_question1": {
      ...
    }
  }
}
```

## 注意事项

- **🔒 解的保证**: 通过补图转换确保每个问题至少有一个已知大小的团
- **✅ 最优性**: 提供的解是有效的，且是生成时预设的最大团
- **🎲 随机性**: 每次运行都会生成不同的问题
- **⚠️ 参数检查**: 必须至少指定一种难度的题目数量 > 0 