def validation(data, answer):
    """
    验证给定的答案是否是一个有效的集合覆盖
    参数:
    data: json中question1字段，包含全集U和子集S
    answer: 字符串答案，包含"Answer："后的子集ID列表
    返回:
    (bool, int, str): 布尔值表示答案是否有效，True代表无效，False代表有效，
                       整数表示使用的子集数量。如果答案无效，返回一个比任何可能解都大的值。
                       字符串提供错误或成功信息。
    """
    U = set(data["U"])
    S = data["S"]

    # 定义一个惩罚值，用于无效答案。
    # 这个值比可能的最大答案（使用所有子集）还要大1。
    penalty_value = len(S) + 1

    if "Answer:" in answer:
        solution_str = answer.split("Answer:")[-1].strip()
    else:
        return True, penalty_value, "invalid answer: no 'Answer:' in answer"

    try:
        if solution_str == "Impossible":
            # 检查声称"不可能"是否正确。
            # 如果用所有可用子集可以覆盖U，那么声称"不可能"就是错误的。
            all_subsets_cover = set()
            for subset in S.values():
                all_subsets_cover.update(subset)
            
            if all_subsets_cover == U:
                 return True, penalty_value, "Incorrect: A solution exists, but answer claims 'Impossible'."
            else:
                 # 声称"不可能"是正确的
                return False, 0, "Correctly identified as impossible."
        
        if solution_str.startswith('[') and solution_str.endswith(']'):
            solution_str = solution_str[1:-1]
        
        # 处理空列表的情况
        if not solution_str.strip():
            selected_subsets = []
        else:
            selected_subsets = [int(x.strip()) for x in solution_str.split(',')]

    except (ValueError, IndexError):
        return True, penalty_value, "Invalid answer format. Should be a list of integers or 'Impossible'."

    # 检查1：选择的子集ID是否都有效
    for subset_id in selected_subsets:
        if str(subset_id) not in S:
            return True, penalty_value, f"Invalid subset ID: {subset_id}"

    # 检查2：选择的子集是否覆盖了全集U
    covered_elements = set()
    for subset_id in selected_subsets:
        covered_elements.update(S[str(subset_id)])

    if covered_elements != U:
        missing_elements = U - covered_elements
        return True, penalty_value, f"Selected subsets do not cover the universal set U. Missing elements: {missing_elements}"

    # 如果所有检查都通过，返回成功
    return False, len(selected_subsets), f"Valid solution using {len(selected_subsets)} subsets."