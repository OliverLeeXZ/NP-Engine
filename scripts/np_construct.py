import json
import re
import os
from pathlib import Path
import sys

def load_prompt_NP_template(prompt_type: str) -> dict:
    # load json
    json_path = 'scripts/prompt_NP.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        prompt_list = json.load(f)
    # find type
    for item in prompt_list:
        if item['type'] == prompt_type:
            prompt = item['prompt']
            break
    else:
        raise ValueError(f"Prompt type {prompt_type} not found in prompt_NP.json")
    return prompt

def compile_prompt_to_md(prompt, _header_depth: int = 1) -> str:
    if isinstance(prompt, str):
        return prompt.strip() + "\n"
    elif isinstance(prompt, list):
        return "\n".join([f"- {s.strip()}" for s in prompt] + ["\n"])

    out = []
    header_prefix = "#" * _header_depth
    for k, v in prompt.items():
        out.append(f"{header_prefix} {k}\n")
        out.append(compile_prompt_to_md(v, _header_depth=_header_depth + 1))
    return "\n".join(out)


def get_prompt(task_type, task_info, NP_question):
    # prompt = load_prompt_NP_template("cons_NP")
    prompt = load_prompt_NP_template("cons_NP")
    prompt["Introduction"] = prompt["Introduction"].format(task_type=task_type)
    prompt["Task description"] = prompt["Task description"].format(description=task_info["description"])
    prompt["Example Input and Output"] = prompt["Example Input and Output"].format(example_input=task_info["example_input"],example_output=task_info["example_output"])   
    prompt["Submission Format"] = prompt["Submission Format"].format(submission_format=task_info["submission_format"])
    prompt["Question"] = prompt["Question"].format(task_type=task_type,question=NP_question)
    
    prompt_md = compile_prompt_to_md(prompt)
    return prompt_md

def extract_markdown_content_NP(md_file_path: str) -> dict:
    # Read the content of the Markdown file
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define a dictionary to store the task description information
    task_des = {}

    # Match the content of each section (starting with '##' headers)
    sections = {
        "description": r"## Description\n(.*?)## Submission Format",
        "submission_format": r"## Submission Format\n(.*?)## Example Input",
        "example_input": r"## Example Input\n(.*?)## Example Output",
        "example_output": r"## Example Output\n(.*?)(##|$)",
    }

    # Extract and store the corresponding content for each section
    for key, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            task_des[key] = match.group(1).strip()
        else:
            task_des[key] = None

    return task_des

def create_md_dict():
    """创建文件夹名称到markdown文件路径的映射字典"""
    base_path = 'NP_tasks'
    
    md_dict = {
        'GCP-D': f'{base_path}/GCP_D/GCP-D.md',
        'hamiltonian-cycle': f'{base_path}/hamiltonian_cycle/hamiltonian-cycle.md', 
        'knapsack': f'{base_path}/knapsack/knapsack.md',
        'maximum_clique_problem': f'{base_path}/maximum_clique_problem/maximum_clique_problem.md',
        'maximum-set': f'{base_path}/maximum_set/maximum-set.md',
        'meeting-schedule': f'{base_path}/meeting_schedule/meeting-schedule.md',
        'minimum-cut': f'{base_path}/minimum_cut/minimum-cut.md',
        'set-cover': f'{base_path}/set_cover/set-cover.md',
        'subset-sum': f'{base_path}/subset_sum/subset-sum.md',
        'TSP': f'{base_path}/TSP/TSP.md'
    }
    return md_dict

def extract_task_type_from_folder_name(folder_name):
    """从文件夹名称中提取任务类型"""
    # 文件夹名称格式通常是: 2-deepseek-reasoner-subset-sum-False-refine-0.5-1
    # 需要提取其中的任务类型部分
    md_dict = create_md_dict()
    
    # 特殊处理一些常见的匹配
    folder_lower = folder_name.lower()
    
    if 'subset' in folder_lower and 'sum' in folder_lower:
        return 'subset-sum'
    elif 'maximum' in folder_lower and 'clique' in folder_lower:
        return 'maximum_clique_problem'
    elif 'hamiltonian' in folder_lower:
        return 'hamiltonian-cycle'
    elif 'minimum' in folder_lower and 'cut' in folder_lower:
        return 'minimum-cut'
    elif 'set' in folder_lower and 'cover' in folder_lower:
        return 'set-cover'
    elif 'maximum' in folder_lower and 'set' in folder_lower:
        return 'maximum-set'
    elif 'meeting' in folder_lower:
        return 'meeting-schedule'
    elif 'gcp' in folder_lower:
        return 'GCP-D'
    elif 'tsp' in folder_lower:
        return 'TSP'
    elif 'knapsack' in folder_lower:
        return 'knapsack'
    
    return None

def process_logs_directory(logs_path):
    """
    遍历logs目录，处理每个子文件夹，生成对应的prompt
    
    Args:
        logs_path (str): logs目录路径
    
    Returns:
        dict: 包含每个文件夹处理结果的字典
    """
    logs_path = Path(logs_path)
    md_dict = create_md_dict()
    results = {}
    
    print(f"🔍 开始处理logs目录: {logs_path}")
    print("=" * 70)
    for folder in logs_path.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            print(f"\n📁 处理文件夹: {folder_name}")
            
            # 1. 根据文件夹名称匹配对应的markdown文件
            task_type = extract_task_type_from_folder_name(folder_name)
            
            if task_type is None:
                print(f"   ❌ 未找到匹配的任务类型")
                results[folder_name] = {"error": "未找到匹配的任务类型"}
                continue
                
            if task_type not in md_dict:
                print(f"   ❌ 任务类型 {task_type} 不在md_dict中")
                results[folder_name] = {"error": f"任务类型 {task_type} 不在md_dict中"}
                continue
            
            md_file_path = md_dict[task_type]
            print(f"   ✅ 匹配任务类型: {task_type}")
            print(f"   📄 Markdown文件: {md_file_path}")
            
            # 2. 检查markdown文件是否存在
            if not os.path.exists(md_file_path):
                print(f"   ❌ Markdown文件不存在: {md_file_path}")
                results[folder_name] = {"error": f"Markdown文件不存在: {md_file_path}"}
                continue
            
                        # 3. 提取任务信息
            try:
                task_info = extract_markdown_content_NP(md_file_path)
                print(f"   ✅ 成功提取任务信息")
            except Exception as e:
                print(f"   ❌ 提取任务信息失败: {e}")
                results[folder_name] = {"error": f"提取任务信息失败: {e}"}
                continue
            
            # 4. 读取results.json文件
            results_file = folder / "results.json"
            if not results_file.exists():
                print(f"   ❌ results.json文件不存在")
                results[folder_name] = {"error": "results.json文件不存在"}
                continue
            
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
                print(f"   ✅ 成功读取results.json，包含 {len(results_data)} 个问题")
            except Exception as e:
                print(f"   ❌ 读取results.json失败: {e}")
                results[folder_name] = {"error": f"读取results.json失败: {e}"}
                continue
            
            # 5. 遍历results.json，生成每个问题的prompt
            folder_prompts = {}
            for question_key, question_data in results_data.items():
                if isinstance(question_data, dict) and 'question' in question_data:
                    NP_question = question_data['question']
                    
                    try:
                        # 生成prompt
                        prompt = get_prompt(task_type, task_info, NP_question)
                        folder_prompts[question_key] = {
                            "task_type": task_type,
                            "prompt": prompt,
                            "answer": question_data.get('answer', None),
                            "metric": question_data.get('metric', None),
                            "question": question_data.get('question', None)
                        }
                        print(f"   ✅ 生成prompt: {question_key}")
                        
                    except Exception as e:
                        print(f"   ❌ 生成prompt失败 {question_key}: {e}")
                        folder_prompts[question_key] = {"error": f"生成prompt失败: {e}"}
                else:
                    print(f"   ⚠️  问题格式不正确: {question_key}")
                    folder_prompts[question_key] = {"error": "问题格式不正确"}
            
            # 6. 保存folder_prompts到final_task.json
            final_task_file = folder / "final_task.json"
            try:
                with open(final_task_file, 'w', encoding='utf-8') as f:
                    json.dump(folder_prompts, f, ensure_ascii=False, indent=2)
                print(f"   💾 已保存到: {final_task_file}")
            except Exception as e:
                print(f"   ❌ 保存final_task.json失败: {e}")
            
            results[folder_name] = {
                "task_type": task_type,
                "md_file": md_file_path,
                "question_count": len(results_data),
                "prompts": folder_prompts,
                "final_task_file": str(final_task_file)
            }
            
            print(f"   🎉 完成处理，生成 {len(folder_prompts)} 个prompt")
    
    print(f"\n🏁 处理完成！总共处理了 {len(results)} 个文件夹")
    return results

def save_processing_results(results, output_file="processing_results.json"):
    """保存处理结果到JSON文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")
        return False

def verify_final_task_files(logs_path):
    """验证生成的final_task.json文件"""
    logs_path = Path(logs_path)
    verified_files = []
    missing_files = []
    
    print(f"\n🔍 验证final_task.json文件...")
    print("=" * 70)
    
    for folder in logs_path.iterdir():
        if folder.is_dir():
            final_task_file = folder / "final_task.json"
            
            if final_task_file.exists():
                try:
                    with open(final_task_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    prompt_count = sum(1 for item in data.values() if isinstance(item, dict) and 'prompt' in item)
                    verified_files.append({
                        'folder': folder.name,
                        'file': str(final_task_file),
                        'question_count': len(data),
                        'prompt_count': prompt_count
                    })
                    print(f"✅ {folder.name}: {prompt_count} prompts")
                    
                except Exception as e:
                    print(f"❌ {folder.name}: 文件损坏 - {e}")
                    missing_files.append(folder.name)
            else:
                print(f"⚠️  {folder.name}: final_task.json不存在")
                missing_files.append(folder.name)
    
    print(f"\n📊 验证结果:")
    print(f"成功验证: {len(verified_files)} 个文件")
    print(f"问题文件: {len(missing_files)} 个")
    
    return verified_files, missing_files

def get_prompt_for_specific_folder_question(logs_path, folder_name, question_key):
    """
    为特定文件夹的特定问题生成prompt
    
    Args:
        logs_path (str): logs目录路径
        folder_name (str): 文件夹名称
        question_key (str): 问题键名
    
    Returns:
        dict: 包含prompt和相关信息的字典
    """
    folder_path = Path(logs_path) / folder_name
    
    if not folder_path.exists():
        return {"error": f"文件夹不存在: {folder_name}"}
    
    # 获取任务类型
    task_type = extract_task_type_from_folder_name(folder_name)
    if task_type is None:
        return {"error": "未找到匹配的任务类型"}
    
    # 获取markdown文件路径
    md_dict = create_md_dict()
    if task_type not in md_dict:
        return {"error": f"任务类型 {task_type} 不在md_dict中"}
    
    md_file_path = md_dict[task_type]
    if not os.path.exists(md_file_path):
        return {"error": f"Markdown文件不存在: {md_file_path}"}
    
    # 提取任务信息
    try:
        task_info = extract_markdown_content_NP(md_file_path)
    except Exception as e:
        return {"error": f"提取任务信息失败: {e}"}
    
    # 读取results.json
    results_file = folder_path / "results.json"
    if not results_file.exists():
        return {"error": "results.json文件不存在"}
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
    except Exception as e:
        return {"error": f"读取results.json失败: {e}"}
    
    # 获取特定问题
    if question_key not in results_data:
        return {"error": f"问题 {question_key} 不存在"}
    
    question_data = results_data[question_key]
    if not isinstance(question_data, dict) or 'question' not in question_data:
        return {"error": "问题格式不正确"}
    
    NP_question = question_data['question']
    
    # 生成prompt
    try:
        prompt = get_prompt(task_type, task_info, NP_question)
        return {
            "prompt": prompt,
            "task_type": task_type,
            "question": NP_question,
            # "answer": question_data.get('answer', None),
            # "metric": question_data.get('metric', None)
        }
    except Exception as e:
        return {"error": f"生成prompt失败: {e}"}

def process_single_results_json(results_json_path):
    """
    输入一个results.json路径，根据其上级目录名推断任务类型，
    生成prompt，只保留prompt和question字段，输出final_task.json。
    支持外层有questions字段的结构。
    """
    import os
    results_json_path = os.path.abspath(results_json_path)
    folder_path = os.path.dirname(results_json_path)
    folder_name = os.path.basename(folder_path)
    name = os.path.basename(results_json_path)
    # 1. 推断任务类型
    task_type = extract_task_type_from_folder_name(folder_name)
    if task_type is None:
        print(f"❌ 未找到匹配的任务类型: {folder_name}")
        return
    md_dict = create_md_dict()
    if task_type not in md_dict:
        print(f"❌ 任务类型 {task_type} 不在md_dict中")
        return
    md_file_path = md_dict[task_type]
    if not os.path.exists(md_file_path):
        print(f"❌ Markdown文件不存在: {md_file_path}")
        return
    # 2. 提取任务信息
    try:
        task_info = extract_markdown_content_NP(md_file_path)
    except Exception as e:
        print(f"❌ 提取任务信息失败: {e}")
        return
    # 3. 读取results.json
    if not os.path.exists(results_json_path):
        print(f"❌ results.json文件不存在: {results_json_path}")
        return
    try:
        with open(results_json_path, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取results.json失败: {e}")
        return

    # 新增：如果有questions字段，就只遍历它
    if 'questions' in results_data and isinstance(results_data['questions'], dict):
        questions_data = results_data['questions']
    else:
        questions_data = results_data

    # 4. 遍历每个问题，生成prompt，只保留prompt和question
    final_data = {}
    for key, value in questions_data.items():
        # value 就是邻接表
        try:
            # 排除ground_truth字段，只保留问题数据
            question_data = {k: v for k, v in value.items() if k != 'ground_truth'}
            prompt = get_prompt(task_type, task_info, question_data)
            final_data[key] = {
                "prompt": prompt,
                "question": question_data,
                "task_type": task_type,
                "ground_truth": value.get('ground_truth', None)
            }
        except Exception as e:
            print(f"❌ 生成prompt失败 {key}: {e}")
    # 5. 输出到final_task.json
    final_task_path = os.path.join(folder_path, name)
    try:
        with open(final_task_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存到: {final_task_path}")
    except Exception as e:
        print(f"❌ 保存final_task.json失败: {e}")

if __name__ == "__main__":
    # 新增命令行参数支持：输入results.json路径，处理单个json
    if len(sys.argv) == 2 and sys.argv[1].endswith('.json'):
        process_single_results_json(sys.argv[1])
        # 单文件模式，处理完直接退出