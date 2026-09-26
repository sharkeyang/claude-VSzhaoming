# -*- coding: utf-8 -*-
"""把 TOC 中 §6.9 条目从 §6.3 之后移到 §6.8 之后、§6.12 之前"""
import io

path = r'_主文档\MC3.3.5_甲乙己日等型交叉分析报告.md'
with io.open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 定位 TOC 中 §6.9 条目范围（从 "6.9 旧版介入时机" 到 "6.5 定型操作规则" 之前）
s = e = None
for i, line in enumerate(lines):
    if '6.9 旧版介入时机' in line:
        s = i
    if s is not None and '6.5 定型操作规则' in line:
        e = i
        break
block = lines[s:e]
print(f'TOC §6.9 条目: line {s+1} ~ {e} (共{e-s}行)')

# 定位 §6.8 最后一条（6.8.6）之后、§6.12 之前
s12 = None
for i, line in enumerate(lines):
    if '6.12 旧内容' in line:
        s12 = i
        break
print(f'§6.12 TOC 起始: line {s12+1}')

# 删除 §6.9 条目
del lines[s:e]

# 重新定位 §6.12
s12 = None
for i, line in enumerate(lines):
    if '6.12 旧内容' in line:
        s12 = i
        break

# 在 §6.12 前插入 §6.9 条目
lines[s12:s12] = block

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('完成')