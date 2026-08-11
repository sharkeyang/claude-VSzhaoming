# -*- coding: utf-8 -*-
"""按字符串标记删除日冲22态代码块（神谕.bas + ZPY接口.bas）"""
import io

def 删除块(path, 起始标记, 结束标记, 保留起始=False, 保留结束=False):
    """删除从起始标记到结束标记（含）之间的内容"""
    with io.open(path, encoding='utf-8') as f:
        lines = f.readlines()
    start_idx = None; end_idx = None
    for i, line in enumerate(lines):
        if start_idx is None and 起始标记 in line:
            start_idx = i
        if start_idx is not None and 结束标记 in line and i >= start_idx:
            end_idx = i
            break
    if start_idx is None or end_idx is None:
        return lines, f"未找到: {起始标记}~{结束标记}"
    # 保留起始/结束标记行的话，调整范围
    s = start_idx + (0 if 保留起始 else 1)
    e = end_idx + (1 if 保留结束 else 0)
    del lines[s:e]
    return lines, f"已删除 {start_idx+1}-{end_idx+1} 行"

# ========== 1. 神谕.bas 检测逻辑块 ==========
神谕 = '_主文档/../昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas'
# 用绝对路径
import os
神谕 = os.path.join(os.getcwd(), '昭明计划VS优化_vba', 'IQQQ跨码_D据擎2神谕.bas')
with io.open(神谕, encoding='utf-8') as f:
    content = f.read()

# 检测逻辑块：从 '日冲22态检测' 到 '谕组(X, 位谕of日冲22态) = 冲22态'
start_marker = "'日冲22态检测"
end_marker = "谕组(X, 位谕of日冲22态) = 冲22态"
si = content.find(start_marker)
ei = content.find(end_marker, si)
if si == -1 or ei == -1:
    print("检测块未找到")
else:
    # 删除从 si 到 ei+len(end_marker) 的整行
    line_start = content.rfind('\n', 0, si) + 1
    line_end = content.find('\n', ei + len(end_marker))
    if line_end == -1: line_end = len(content)
    content = content[:line_start] + content[line_end:]
    print("检测逻辑块已删除")

with io.open(神谕, 'w', encoding='utf-8') as f:
    f.write(content)