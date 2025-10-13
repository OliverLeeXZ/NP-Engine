def validation(graph, answer):
    """
    验证给定的答案是否是一个有效的图着色方案
    
    参数:
    graph: 图的表示，包含邻接表
    answer: 字符串答案，包含"Answer："后的着色方案
    
    返回:
    (bool, int, str): 布尔值表示答案是否有效，True代表无效，False代表有效，
                       整数表示使用的颜色数。如果答案无效，返回一个比任何可能解都大的值。
                       字符串提供错误或成功信息。
    """
    num_vertices = len(graph)
    # 定义一个惩罚值，用于无效答案。
    # 这个值比可能的最大颜色数（每个节点一种颜色）还要大1。
    penalty_value = num_vertices + 1

    # 解析answer字符串，提取"Answer:"后面的内容
    if "Answer:" in answer:
        color_str = answer.split("Answer:")[-1].strip()
    else:
        return True, penalty_value, "invalid answer: no 'Answer:' in answer"
    
    # 标准化颜色字符串格式
    color_str = color_str.strip()
    
    # 如果已经是 [x,x,x,...,x] 格式，直接使用
    if color_str.startswith('[') and color_str.endswith(']'):
        color_str = color_str[1:-1]  # 去掉方括号
    else:
        # 处理 -> 格式
        if '->' in color_str:
            # 分割并清理每个节点
            nodes = [node.strip() for node in color_str.split('->')]
            # 重新组合成标准格式
            color_str = ','.join(nodes)
        else:
            # 处理其他括号格式 {x,x,x} 或 (x,x,x) 或 ['x','x','x']
            # 移除所有引号
            color_str = color_str.replace("'", "").replace('"', '')
            
            # 使用正则表达式匹配括号内容
            import re
            pattern = r'[{\[\(]([^)}\]]*)[}\])]'
            match = re.search(pattern, color_str)
            
            if match:
                # 提取括号内的内容
                color_str = match.group(1)
            else:
                # 如果没有任何括号，假设是逗号分隔的列表
                pass
    
    # 尝试将颜色字符串转换为整数列表
    try:
        # 处理空字符串的情况
        if not color_str.strip():
            colors = []
        else:
            colors = [int(x.strip()) for x in color_str.split(',')] # 将颜色字符串转换为整数列表
    except (ValueError, IndexError):
        return True, penalty_value, "coloring must be a list of integers"
    
    if not colors:
        return True, penalty_value, "coloring cannot be empty"
    
    if -1 in colors:
        return True, penalty_value, "not valid response with -1 in coloring list, coloring must be a list of integers and bigger than 0"
    
    # 检查着色方案的节点数量是否与图匹配
    if len(colors) != num_vertices:
        return True, penalty_value, f"invalid coloring: not all vertices are colored, overall {num_vertices} vertices, got {len(colors)} vertices"
    
    # 检查是否是有效的着色方案
    
    # 1. 检查是否有相邻的顶点共享相同颜色
    for node_str, neighbors in graph.items():
        node = int(node_str)
        if colors[node] <= 0:
             return True, penalty_value, f"invalid color: color for node {node} is {colors[node]}, but must be a positive integer."
        node_color = colors[node]
        for neighbor_str in neighbors:
            neighbor = int(neighbor_str)
            neighbor_color = colors[neighbor]
            if node_color == neighbor_color:
                return True, penalty_value, f"invalid coloring: node {node} and node {neighbor} have the same color {node_color}"
    
    # 2. 如果所有检查都通过，返回有效的着色方案
    num_used_colors = len(set(colors))
    return False, num_used_colors, f"valid coloring with {num_used_colors} colors, try to use less color to assign"
