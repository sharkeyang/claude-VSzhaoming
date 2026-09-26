# -*- coding: utf-8 -*-
"""更新 TOC 中 §6.4 条目 → §6.9（编号+锚点+标题）"""
import io, re

path = r'_主文档\MC3.3.5_甲乙己日等型交叉分析报告.md'
with io.open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 定位 TOC 中 §6.4 条目范围（从 "6.4 第3层" 到 "6.5 定型操作规则" 之前）
start = None
end = None
for i, line in enumerate(lines):
    if '6.4 第3层：介入时机' in line:
        start = i
    if start is not None and '6.5 定型操作规则' in line:
        end = i
        break
print(f'TOC §6.4 条目范围: line {start+1} ~ {end}')

# 处理每个 TOC 条目
for i in range(start, end):
    line = lines[i]
    # 编号 6.4.x → 6.9.x
    line = re.sub(r'6\.4\.', '6.9.', line)
    # 主标题
    line = line.replace('6.4 第3层：介入时机（选时机）', '6.9 旧版介入时机')
    # 锚点 64x → 69x（锚点格式 #64- / #641- / #6421- 等）
    line = re.sub(r'\(#64', '(#69', line)
    lines[i] = line

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('完成')
