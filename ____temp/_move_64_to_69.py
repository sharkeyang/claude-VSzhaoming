# -*- coding: utf-8 -*-
"""把 §6.4 章节整体移到 §6.9（标题+子节编号+文档引用）
只处理 §6.4 章节范围（### 6.4 到 ### 6.5 之间）的标题，以及文档中对 §6.4 的引用。
"""
import io, re

path = r'_主文档\MC3.3.5_甲乙己日等型交叉分析报告.md'
with io.open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 定位 §6.4 章节范围
start = None
end = None
for i, line in enumerate(lines):
    if line.startswith('### 6.4 '):
        start = i
    if start is not None and line.startswith('### 6.5 '):
        end = i
        break
print(f'§6.4 章节范围: line {start+1} ~ {end}')

# 1. 处理 §6.4 章节内的标题（###/####/##### 6.4.x → 6.9.x）
for i in range(start, end):
    m = re.match(r'^(#{2,5}) 6\.4\.', lines[i])
    if m:
        lines[i] = re.sub(r'^(#{2,5}) 6\.4\.', r'\1 6.9.', lines[i])
# 章节主标题
lines[start] = lines[start].replace('### 6.4 第3层：介入时机（选时机）', '### 6.9 旧版介入时机')

# 2. 处理文档中对 §6.4 的引用（§6.4 → §6.9），但排除 2.6.4 等非§6.4
for i, line in enumerate(lines):
    if i == start:  # 跳过章节标题本身（已处理）
        continue
    # 只替换 "§6.4" 和 "6.4 " 引用，不替换 "2.6.4" "6.4.x"（章节内已处理）
    new = line.replace('§6.4', '§6.9')
    if new != line:
        lines[i] = new

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('完成')
