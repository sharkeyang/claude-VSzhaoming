# -*- coding: utf-8 -*-
"""清理日冲22态VBA代码 — 按字符串标记精确删除"""
import os

BASE = os.path.join(os.getcwd(), '昭明计划VS优化_vba')
神谕 = os.path.join(BASE, 'IQQQ跨码_D据擎2神谕.bas')
ZPY = os.path.join(BASE, 'PX算研_ZPY接口.bas')

def 删行范围(path, 起始标记, 结束标记):
    """删除从含起始标记的行到含结束标记的行（含），返回消息"""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    si = None; ei = None
    for i, line in enumerate(lines):
        if si is None and 起始标记 in line: si = i
        if si is not None and 结束标记 in line and i >= si: ei = i; break
    if si is None: return f"未找到起始标记: {起始标记}"
    if ei is None: return f"未找到结束标记: {结束标记}"
    del lines[si:ei+1]
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return f"已删除 {si+1}-{ei+1} 行"

# ========== 1. 神谕.bas — 检测逻辑块 ==========
print(删行范围(神谕, "'日冲22态检测", "谕组(X, 位谕of日冲22态) = 冲22态"))

# ========== 2. 神谕.bas — 策略映射 ==========
print(删行范围(神谕, "谕组(X, 位谕of日层机警) = \"\"", "If 冲22态 = \"V2_跌_跌排\" Or 冲22态 = \"V4_人_ZA3外\" Then 谕组(X, 位谕of日层机警) = \"空仓观望\""))

# ========== 3. 神谕.bas — 列标题 ==========
print(删行范围(神谕, '.Cells(1, 位谕of日冲22态) = "日冲22态"', '.Cells(1, 位谕of日冲22态) = "日冲22态"'))

# ========== 4. 神谕.bas — 列格式 ==========
# 列宽和左对齐是两行，分别删
print(删行范围(神谕, '.Columns(位谕of日冲22态).ColumnWidth', '.Columns(位谕of日冲22态).ColumnWidth'))
print(删行范围(神谕, '.Columns(位谕of日冲22态).HorizontalAlignment', '.Columns(位谕of日冲22态).HorizontalAlignment'))

# ========== 5. ZPY接口.bas — 测试函数 ==========
print(删行范围(ZPY, "' 测试_日冲22态", "End Sub"))

print("\n清理完成！")