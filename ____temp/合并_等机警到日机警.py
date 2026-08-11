# -*- coding: utf-8 -*-
"""把等机警数据写入日机警，删等机警列"""
import os
BASE = os.path.join(os.getcwd(), '昭明计划VS优化_vba')
神谕 = os.path.join(BASE, 'IQQQ跨码_D据擎2神谕.bas')
筛选 = os.path.join(BASE, 'IQQQ跨码_P展擎1筛选.bas')

with open(神谕, 'r', encoding='utf-8') as f:
    s = f.read()

# 1. 常量：删等机警行，日机警+18→+17
old_const = """Public Const 位谕of日层等机警 = 位谕始of族策 + 17     '原族日层+6，移至日冲22态空位
Public Const 位谕of日层机警 = 位谕始of族策 + 18     '原+16，后移"""
new_const =   "Public Const 位谕of日层机警 = 位谕始of族策 + 17     '原+18，由等机警数据写入"
s = s.replace(old_const, new_const, 1)
print("1) 常量已合并：日层机警=+17，等机警已删")

# 2. 写入：等机警→日机警
s = s.replace("谕组(X, 位谕of日层等机警) = 等机警", "谕组(X, 位谕of日层机警) = 等机警", 1)
print("2) 写入已改：谕组(X, 位谕of日层机警) = 等机警")

# 3. 列标题：删等机警行
s = s.replace('        .Cells(1, 位谕of日层等机警) = "等机警"\n', "", 1)
print("3) 列标题等机警已删")

# 4. 列宽：删等机警列宽行
s = s.replace('        .Columns(位谕of日层等机警).ColumnWidth = 8\n', "", 1)
print("4) 列宽等机警已删")

with open(神谕, 'w', encoding='utf-8') as f:
    f.write(s)

# 5. 筛选.bas：读取改常量名
with open(筛选, 'r', encoding='utf-8') as f:
    ss = f.read()
ss = ss.replace("位谕of日层等机警", "位谕of日层机警", 1)
with open(筛选, 'w', encoding='utf-8') as f:
    f.write(ss)
print("5) 筛选.bas 读取已改")

print("\n完成！")