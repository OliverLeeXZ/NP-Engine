def validation(problem, answer):
    """
    验证子集和问题的答案是否是一个合法的可行解（和为 target）。
    返回子集长度作为参考，但不强制要求是最长解。
    
    参数:
        problem: 包含 "target" 和 "numbers" 两个字段的字典。
        answer: 字符串形式的解，形如 "Answer: [1, 2, 4]"
    
    返回:
        (bool, int, str): 
            - bool 表示是否有错误（True 代表有错）；
            - int 为子集长度（如无效则为 -1）；
            - str 为说明信息。
    """
    if "Answer:" in answer:
        indices_str = answer.split("Answer:")[-1].strip()
    else:
        return True, -1, "invalid answer: no 'Answer:' in answer"

    import re

    indices_str = indices_str.strip().replace("'", "").replace('"', '')
    pattern = r'[{\[\(]([^)}\]]*)[}\])]'
    match = re.search(pattern, indices_str)
    if match:
        indices_str = match.group(1)

    try:
        indices = [int(x.strip()) for x in indices_str.split(',') if x.strip() != '']
    except:
        return True, -1, "invalid index list: should be a list of integers"

    if not indices:
        return True, -1, "index list is empty"

    numbers = problem.get("numbers", {})
    target = problem.get("target", None)

    if target is None or not isinstance(numbers, dict):
        return True, -1, "invalid problem format"

    for idx in indices:
        if str(idx) not in numbers:
            return True, -1, f"index {idx} not found in input numbers"

    submitted_sum = sum(numbers[str(i)] for i in indices)
    if submitted_sum != target:
        return True, -1, f"subset sum {submitted_sum} does not match target {target}"

    return False, len(indices), f"valid subset of length {len(indices)} with correct sum {target}"
