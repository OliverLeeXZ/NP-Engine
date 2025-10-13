# 最大独立集（MIS）问题造题脚本使用说明

## 概述

这是一个基于规则的最大独立集问题（Maximum Independent Set Problem）造题脚本。其目标是生成一个无向图，并要求解答者找到其中最大的顶点集合，使得集合中任意两个顶点之间都没有边直接相连。

为了确保每个生成的问题都必然有解，此脚本采用了"植入解"的策略。具体步骤如下：
1.  首先确定一个预设大小的顶点集合，作为"保证的"独立集（我们称之为`I`）。
2.  然后生成图中的其他顶点（我们称之为`O`）。
3.  在顶点集`O`内部随机添加边。
4.  在`I`和`O`之间添加边，同时确保`I`内部的顶点之间绝不添加任何边。

通过这种方法，我们预先植入的集合`I`就是一个有效的独立集，从而保证了问题有解。

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
# - generated_maximum_set_questions_easy.json
# - generated_maximum_set_questions_medium.json  
# - generated_maximum_set_questions_hard.json
```

### 🎛️ **自定义输出文件名**

```bash
python generate_questions.py --easy 3 --medium 2 --hard 1 --output my_mis_dataset.json
```

## 难度级别详解

### 🟢 **简单（Easy）**
- **顶点数量**: 8-15个
- **独立集大小**: 3-5个顶点
- **特点**: 图相对稠密，干扰项较少，独立集结构比较明显

### 🟡 **中等（Medium）**  
- **顶点数量**: 15-25个
- **独立集大小**: 5-8个顶点
- **特点**: 图复杂度适中，需要一定的搜索技巧来识别最大独立集

### 🔴 **困难（Hard）**
- **顶点数量**: 25-40个
- **独立集大小**: 8-12个顶点
- **特点**: 图相对稀疏，在众多看似独立的顶点中找到最大的真实独立集变得更加困难

## 核心参数

- `--easy N`: 生成N道简单题目 (默认: 0)
- `--medium M`: 生成M道中等题目 (默认: 0)
- `--hard P`: 生成P道困难题目 (默认: 0)
- `--output FILE`: 指定输出文件名 (默认: `generated_maximum_set_questions.json`)
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
python generate_questions.py --easy 5 --medium 5 --hard 5 --output research_mis_set.json
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
平均顶点数: 18.7
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
      "0": { "3": 1, "4": 1 },
      "1": { "3": 1 },
      "2": { "4": 1 },
      "3": { "0": 1, "1": 1 },
      "4": { "0": 1, "2": 1 }
    },
    "medium_question1": {
      ...
    }
  }
}
```

## 算法详解

### 🔧 **生成过程**
1. **确定独立集**: 随机选择指定数量的顶点作为目标独立集 `I`
2. **分配其他顶点**: 剩余顶点构成集合 `O`
3. **内部连边**: 在集合 `O` 内部按边密度参数随机添加边
4. **跨集连边**: 在 `I` 和 `O` 之间添加边，确保每个 `O` 中的顶点至少与一个 `I` 中的顶点相连
5. **保证独立性**: `I` 内部顶点之间绝不添加边，确保其独立集性质

### 📈 **难度控制参数**
- **edge_density_O**: 其他顶点内部的边密度
- **edge_density_IO**: 独立集与其他顶点间的边密度
- 难度越高，边密度越低，识别难度越大

## 注意事项

- **🔒 解的保证**: 通过"植入解"策略确保每个问题至少有一个已知大小的独立集
- **✅ 最优性**: 提供的解是有效的，且是生成时预设的最大独立集
- **🎲 随机性**: 每次运行都会生成不同的问题
- **⚠️ 参数检查**: 必须至少指定一种难度的题目数量 > 0
- **🔄 独立集性质**: 植入的独立集保证任意两个顶点之间无边连接 