# -*- coding: utf-8 -*-
"""删除维持列，加粗自转移"""
with open('_主文档/MC3.1.0_周级别WXZC×WXAB护型总结一页纸.md', 'rb') as f:
    data = f.read()

# 1. 删除所有表格中的"维持"列头
data = data.replace(b'| \xe7\xbb\xb4\xe6\x8c\x81 |', b'|')
data = data.replace(b'| \xe7\xbb\xb4\xe6\x8c\x81\xe7\x8e\x87 |', b'|')

# 2. 删除所有表格行中的维持率数据（最后一列）
lines = data.split(b'\n')
new_lines = []
for line in lines:
    if line.startswith(b'|') and line.count(b'|') >= 3:
        parts = line.split(b'|')
        # 删除最后一个非空列
        for i in range(len(parts)-1, 0, -1):
            if parts[i].strip():
                parts[i] = b''
                break
        line = b'|'.join(parts)
    new_lines.append(line)

data = b'\n'.join(new_lines)

# 3. 加粗自转移（自己转移到自己）
# 甲行中的→甲，乙(ZA>0)行中的→乙(ZA>0)，己行中的→己
# 用**加粗**表示
# 模式：当前护型在行首，对应的自转移在列中
# 甲行：| **甲** | **83.0%** |  → 加粗83.0%
# 乙(ZA>0)行：| **乙(ZA>0)** | — | **80.0%** |  → 加粗80.0%
# 乙(ZA≤0)行：| **乙(ZA≤0)** | — | 28.2% | **33.4%** |  → 加粗33.4%
# 丙行：| **丙** | — | 14.4% | 7.4% | **46.0%** |  → 加粗46.0%
# 丁行：| **丁** | 11.0% | — | — | — | **70.4%** |  → 加粗70.4%
# 戊(ZA>0)行：| **戊(ZA>0)** | 13.6% | — | — | — | — | **16.3%** |  → 加粗16.3%
# 戊(ZA≤0)行：| **戊(ZA≤0)** | 13.3% | — | — | — | — | 7.4% | **62.8%** |  → 加粗62.8%
# 己行：| **己** | **60.5%** |  → 加粗60.5%

# 对于每个护型，找到其自转移的列位置并加粗
# 甲：第2列（→甲）
# 乙(ZA>0)：第3列（→乙(ZA>0)）
# 乙(ZA≤0)：第4列（→乙(ZA≤0)）
# 丙：第5列（→丙）
# 丁：第6列（→丁）
# 戊(ZA>0)：第7列（→戊(ZA>0)）
# 戊(ZA≤0)：第8列（→戊(ZA≤0)）
# 己：第9列（→己）

# 用正则替换：在表格行中找到对应列的值并加粗
import re

# 处理所有表格行
lines = data.split(b'\n')
new_lines = []
for line in lines:
    if not line.startswith(b'|') or line.count(b'|') < 3:
        new_lines.append(line)
        continue

    parts = line.split(b'|')
    # 第1部分是护型名
    hu = parts[1].strip()

    # 确定自转移的列索引
    col_map = {
        b'**\xe7\x94\xb2**': 2,  # 甲→甲
        b'**\xe4\xb9\x99(ZA>0)**': 3,  # 乙(ZA>0)→乙(ZA>0)
        b'**\xe4\xb9\x99(ZA\xe2\x89\xa40)**': 4,  # 乙(ZA≤0)→乙(ZA≤0)
        b'**\xe4\xb8\x99**': 5,  # 丙→丙
        b'**\xe4\xb8\x81**': 6,  # 丁→丁
        b'**\xe6\x88\x8a(ZA>0)**': 7,  # 戊(ZA>0)→戊(ZA>0)
        b'**\xe6\x88\x8a(ZA\xe2\x89\xa40)**': 8,  # 戊(ZA≤0)→戊(ZA≤0)
        b'**\xe5\xb7\xb1**': 9,  # 己→己
    }

    col_idx = col_map.get(hu, -1)
    if col_idx > 0 and col_idx < len(parts):
        val = parts[col_idx].strip()
        # 如果值不是"—"且没有加粗，则加粗
        if val and val != b'\xe2\x80\x94' and not val.startswith(b'**'):
            parts[col_idx] = b'**' + val.strip() + b'**'
        line = b'|'.join(parts)

    new_lines.append(line)

data = b'\n'.join(new_lines)

with open('_主文档/MC3.1.0_周级别WXZC×WXAB护型总结一页纸.md', 'wb') as f:
    f.write(data)

print('完成')