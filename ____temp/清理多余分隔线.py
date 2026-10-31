# -*- coding: utf-8 -*-
"""删除6.2节后多余的连续---，只保留一个。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到"网越大"行和"### 6.3"行之间的区域，清理多余的---
out = []
i = 0
while i < len(lines):
    line = lines[i]
    # 检测连续 --- 块（含空行间隔），压缩为单个 ---
    if line.strip() == '---':
        # 收集连续的 --- 和空行
        j = i
        while j < len(lines) and (lines[j].strip() == '---' or lines[j].strip() == ''):
            j += 1
        # 只保留一个 --- 和一个空行
        out.append('---\n')
        # 跳过所有 --- 和空行
        i = j
        # 如果下一个非空行不是标题，补一个空行
        if i < len(lines) and lines[i].strip() != '':
            out.append('\n')
        continue
    out.append(line)
    i += 1

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(out)

print('清理完成')