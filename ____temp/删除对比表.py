# -*- coding: utf-8 -*-
"""删除6.1-6.2各方法是否必赢对比表块（833-851行附近）。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到对比表块的起止
start = None
end = None
for i, line in enumerate(lines):
    if '6.1-6.2 各方法"是否必赢"对比' in line:
        start = i
    if start is not None and '6.2 方法日C冲 不是可执行策略' in line and i > start:
        end = i
        break

if start is not None and end is not None:
    # 删除 start 到 end（含），保留 end+1 之后的
    del lines[start:end+1]
    with io.open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'已删除对比表块（行{start+1}-{end+1}）')
else:
    print(f'未找到对比表块 start={start} end={end}')