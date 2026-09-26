# -*- coding: utf-8 -*-
"""把 §6.9 块（原§6.4位置）移动到 §6.8 之后、§6.12 之前"""
import io

path = r'_主文档\MC3.3.5_甲乙己日等型交叉分析报告.md'
with io.open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 定位 §6.9 块（### 6.9 到 ### 6.5 之前）
s = e = None
for i, line in enumerate(lines):
    if line.startswith('### 6.9 '):
        s = i
    if s is not None and line.startswith('### 6.5 '):
        e = i
        break
block = lines[s:e]
print(f'§6.9 块: line {s+1} ~ {e} (共{e-s}行)')

# 定位 §6.12 起始（### 6.12 之前）
s12 = None
for i, line in enumerate(lines):
    if line.startswith('### 6.12 '):
        s12 = i
        break
print(f'§6.12 起始: line {s12+1}')

# 删除 §6.9 块
del lines[s:e]

# 重新定位 §6.12（删除后行号变化）
s12 = None
for i, line in enumerate(lines):
    if line.startswith('### 6.12 '):
        s12 = i
        break

# 在 §6.12 前插入 §6.9 块
lines[s12:s12] = block

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('完成')
