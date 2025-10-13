def validation(data, answer):
    """
    验证给定的答案是否是一个有效的背包解

    参数
    ----
    data : dict
        JSON 对象，字段:
          • "capacity" : int
          • "items"    : dict[str | int, {"weight": int, "value": int}]
    answer : str
        字符串答案，形如 "Answer: [0, 2, 3]"

    返回
    ----
    (bool, int | float, str)
        第 1 个元素: True  表示答案无效，False 表示答案有效  
        第 2 个元素: 当无效时给 -1；当有效时给出选择物品的总价值  
        第 3 个元素: 说明信息
    """
    # 1. 提取 capacity 与 items
    if not isinstance(data, dict):
        return True, -1, "input must be a dict / JSON object"

    if "capacity" not in data or "items" not in data:
        return True, -1, "input must contain 'capacity' and 'items' keys"

    try:
        capacity = int(data["capacity"])
        assert capacity >= 0
    except Exception:
        return True, -1, "invalid capacity"

    items = data["items"]
    if not isinstance(items, dict) or len(items) == 0:
        return True, -1, "'items' must be a non-empty dict"

    # 把物品键转换为字符串方便统一比较
    items = {str(k): v for k, v in items.items()}

    # 2. 解析 answer 字符串，抽出 [ … ] 内的内容
    if "Answer:" not in answer:
        return True, -1, "invalid answer: no 'Answer:' in answer"

    item_str = answer.split("Answer:")[-1].strip()

    # 去掉首尾方括号或其它括号/箭头等格式差异
    if item_str.startswith("[") and item_str.endswith("]"):
        item_str = item_str[1:-1]
    else:
        # 兼容 "0 -> 1 -> 3" 等格式
        if "->" in item_str:
            item_str = ",".join([x.strip() for x in item_str.split("->")])
        else:
            # 去引号再尝试取括号内容
            import re
            tmp = item_str.replace("'", "").replace('"', "")
            match = re.search(r"[{\[\(]([^)}\]]*)[}\])]", tmp)
            item_str = match.group(1) if match else tmp

    # 拆分并转 int
    try:
        chosen = [int(x.strip()) for x in item_str.split(",") if x.strip() != ""]
    except Exception:
        return True, -1, "answer list must contain integers only"

    if len(chosen) == 0:
        return True, -1, "answer list cannot be empty"

    # 3. 检查是否有重复
    if len(chosen) != len(set(chosen)):
        return True, -1, "duplicate item IDs in answer"

    # 4. 检查物品是否存在，同时累计重量/价值
    total_weight = 0
    total_value = 0
    for idx in chosen:
        key = str(idx)
        if key not in items:
            return True, -1, f"item {idx} does not exist in input"
        item_info = items[key]
        try:
            w = int(item_info["weight"])
            v = int(item_info["value"])
            assert w >= 0 and v >= 0
        except Exception:
            return True, -1, f"item {idx} has invalid weight/value"
        total_weight += w
        total_value += v

    # 5. 检查是否超容量
    if total_weight > capacity:
        return True, -1, f"total weight {total_weight} exceeds capacity {capacity}"

    # 通过全部校验 → 有效
    return False, total_value, f"total weight: {total_weight}, total value: {total_value}"
