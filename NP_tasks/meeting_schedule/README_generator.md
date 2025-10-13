# 会议安排问题（MSP）造题脚本使用说明

## 概述

这是一个基于规则的会议安排问题（Meeting Scheduling Problem）造题脚本。它为该问题的一个特定变体生成题目：**在满足所有约束（时间、人员、房间容量）的前提下，制定一个时间表，以最大化所有已安排会议的总参与人数**。

此脚本通过一个贪心算法来找到一个有效的（但不一定是最优的）解，从而确保每个生成的问题都至少有一个有效的解。

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
# - generated_meeting_schedule_questions_easy.json
# - generated_meeting_schedule_questions_medium.json  
# - generated_meeting_schedule_questions_hard.json
```

### 🎛️ **自定义输出文件名**

```bash
python generate_questions.py --easy 3 --medium 2 --hard 1 --output my_msp_dataset.json
```

## 难度级别详解

### 🟢 **简单（Easy）**
- **会议数量**: 3-5个
- **参会者数量**: 5-8人
- **房间数量**: 2-3间
- **每会议最大参会者**: 4人
- **时间碎片化**: 20%的参会者有午休时间
- **特点**: 大多数参会者有完整的可用时间，冲突较少

### 🟡 **中等（Medium）**  
- **会议数量**: 5-8个
- **参会者数量**: 8-15人
- **房间数量**: 3-5间
- **每会议最大参会者**: 6人
- **时间碎片化**: 50%的参会者有午休时间
- **特点**: 适度的时间和资源冲突，需要合理规划

### 🔴 **困难（Hard）**
- **会议数量**: 8-12个
- **参会者数量**: 15-25人
- **房间数量**: 4-6间
- **每会议最大参会者**: 8人
- **时间碎片化**: 80%的参会者有午休时间
- **特点**: 大量时间冲突，资源竞争激烈，安排复杂

## 核心参数

- `--easy N`: 生成N道简单题目 (默认: 0)
- `--medium M`: 生成M道中等题目 (默认: 0)
- `--hard P`: 生成P道困难题目 (默认: 0)
- `--output FILE`: 指定输出文件名 (默认: `generated_meeting_schedule_questions.json`)
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
python generate_questions.py --easy 5 --medium 5 --hard 5 --output research_msp_set.json
```

## 输出文件

脚本会生成以下文件：

### 📄 **题目文件** 
- **混合模式**: `output_name.json`
- **分离模式**: `output_name_easy.json`, `output_name_medium.json`, `output_name_hard.json`
- 包含会议信息、参会者可用性、房间容量等数据
- 提供给解答者的文件

### 📋 **答案文件**
- `output_name_with_answers.json`
- 包含完整题目、贪心算法生成的有效解和元数据
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
平均会议数量: 6.3
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
      "meetings": {
        "0": {"attendees": [1, 4], "duration": 60},
        "1": {"attendees": [2, 3], "duration": 30}
      },
      "attendee_availability": {
        "0": [[540, 1020]],
        "1": [[540, 720], [780, 1020]],
        "2": [[540, 1020]],
        "3": [[540, 1020]],
        "4": [[540, 720], [780, 1020]]
      },
      "rooms": {
        "0": 5,
        "1": 3
      }
    },
    "medium_question1": {
      ...
    }
  }
}
```

## 算法详解

### 🔧 **贪心调度算法**
1. **资源分配**: 为每个会议找到容量足够的房间
2. **时间窗口**: 计算所有参会者的共同可用时间
3. **冲突检测**: 检查房间和参会者的时间冲突
4. **增量安排**: 按30分钟时间槽逐步尝试安排会议
5. **解决方案**: 返回可行的会议时间表

### 📅 **时间表示系统**
- **时间单位**: 分钟（从午夜开始计算）
- **工作时间**: 9:00-17:00 (540-1020分钟)
- **午休时间**: 12:00-13:00 (720-780分钟)
- **会议时长**: 30分钟、60分钟、90分钟

### 📈 **难度控制机制**
- **碎片化概率**: 控制有午休时间的参会者比例
- **资源压力**: 通过会议数量与房间数量比例调节
- **人员冲突**: 通过参会者数量和每会议参会人数控制

## 注意事项

- **🔒 解的保证**: 通过贪心算法确保每个问题至少有一个可行解
- **⚖️ 最优性**: 提供的解是有效的，但不一定是最优的（总参会人数最大化）
- **⏰ 时间表示**: 所有时间以"从午夜开始的分钟数"表示（如9:00 = 540分钟）
- **🎲 随机性**: 每次运行都会生成不同的问题
- **⚠️ 参数检查**: 必须至少指定一种难度的题目数量 > 0
- **🏢 房间约束**: 房间容量必须满足会议的参会者数量要求 