# -*- coding: utf-8 -*-
"""清理第六章连续空行（≥2个合并为1个，跳过代码块内部）"""
import io

OUT = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'

with io.open(OUT, encoding='utf-8') as f:
    lines = f.readlines()

# 定位第六章区域
start = end = None
for i, l in enumerate(lines):
    if l.strip() == '## 六、操盘计划':
        start = i
    if l.strip() == '## 七、周级别映射 + 微观指标':
        end = i
        break
assert start is not None and end is not None, '定位第六章失败'
print(f'第六章: 第{start+1}行 到 第{end+1}行')

# 处理第六章区域内的连续空行（跳过代码块内部）
new_lines = lines[:start]
i = start
in_code = False
while i < end:
    line = lines[i]
    # 检测代码块边界
    if line.strip().startswith('```'):
        in_code = not in_code
        new_lines.append(line)
        i += 1
        continue
    if in_code:
        # 代码块内部，保留原样
        new_lines.append(line)
        i += 1
        continue
    # 非代码块：检测连续空行
    if line.strip() == '':
        # 找连续空行
        j = i
        while j < end and lines[j].strip() == '':
            j += 1
        # 合并为1个空行
        new_lines.append('\n')
        i = j
    else:
        new_lines.append(line)
        i += 1

# 保留第六章之后的内容
new_lines.extend(lines[end:])

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('清理完成')
print('总行数:', len(new_lines))