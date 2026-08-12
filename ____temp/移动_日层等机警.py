# -*- coding: utf-8 -*-
"""移动位谕of日层等机警：族日层+6 → 族策+17（日冲22态腾出的空位），格式化同步迁移"""
import os
BASE = os.path.join(os.getcwd(), '昭明计划VS优化_vba')
神谕 = os.path.join(BASE, 'IQQQ跨码_D据擎2神谕.bas')

with open(神谕, 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 1. 常量定义：删除原定义（含注释行） ==========
old_const = """'等高线机会与警示（在神谕中计算，筛选直接读取）
Public Const 位谕of日层等机警 = 位谕始of族日层 + 6
"""
if old_const in content:
    content = content.replace(old_const, "", 1)
    print("1) 常量定义原位置已删除")
else:
    print("1) 未找到常量定义原位置！")

# ========== 2. 位谕终of族日层 +6 → +5 ==========
old_term = "Public Const 位谕终of族日层 = 位谕始of族日层 + 6"
new_term = "Public Const 位谕终of族日层 = 位谕始of族日层 + 5"
if old_term in content:
    content = content.replace(old_term, new_term, 1)
    print("2) 位谕终of族日层 +6→+5 已改")
else:
    print("2) 未找到 位谕终of族日层！")

# ========== 3. 常量定义：插入到 位谕of日层机警 前 ==========
anchor = "Public Const 位谕of日层机警 = 位谕始of族策 + 18     '原+16，后移"
new_const = """'等高线机会与警示（在神谕中计算，筛选直接读取）
Public Const 位谕of日层等机警 = 位谕始of族策 + 17     '原族日层+6，移至日冲22态空位
"""
if anchor in content:
    content = content.replace(anchor, new_const + anchor, 1)
    print("3) 常量定义已插入 位谕of日层机警 前")
else:
    print("3) 未找到 位谕of日层机警 常量！")

# ========== 4. 列标题：删除原位置 ==========
old_hdr = '        .Cells(1, 位谕of日层等机警) = "等机警"\n'
if old_hdr in content:
    content = content.replace(old_hdr, "", 1)
    print("4) 列标题原位置已删除")
else:
    print("4) 未找到列标题原位置！")

# ========== 5. 列标题：插入到 日层机警列标题 前 ==========
anchor_hdr = '        .Cells(1, 位谕of日层机警) = "日机警"'
new_hdr = '        .Cells(1, 位谕of日层等机警) = "等机警"\n' + anchor_hdr
if anchor_hdr in content:
    content = content.replace(anchor_hdr, new_hdr, 1)
    print("5) 列标题已插入 日机警 前")
else:
    print("5) 未找到 日机警 列标题！")

# ========== 6. 列宽：删除原位置 ==========
old_w = '        .Columns(位谕of日层等机警).ColumnWidth = 8\n'
if old_w in content:
    content = content.replace(old_w, "", 1)
    print("6) 列宽原位置已删除")
else:
    print("6) 未找到列宽原位置！")

# ========== 7. 列宽：插入到 日层机警列宽 前 ==========
anchor_w = '        .Columns(位谕of日层机警).ColumnWidth = 15'
new_w = '        .Columns(位谕of日层等机警).ColumnWidth = 8\n' + anchor_w
if anchor_w in content:
    content = content.replace(anchor_w, new_w, 1)
    print("7) 列宽已插入 日机警 前")
else:
    print("7) 未找到 日机警 列宽！")

with open(神谕, 'w', encoding='utf-8') as f:
    f.write(content)
print("\n完成！")