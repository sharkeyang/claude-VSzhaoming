# -*- coding: utf-8 -*-
"""
重新编号 6.3-6.7 → 6.2-6.6。
只替换章节编号（标题行、TOC行、交叉引用），不替换数据。
用占位符避免冲突。
"""
import io
import re

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 替换映射（从大到小，用占位符）
# 匹配章节编号：标题行(### 6.x / #### 6.x.y)、TOC行(- [6.x / - [6.x.y)、交叉引用(6.x 方法/见 6.x/6.x 不是/6.x 非必赢)
def repl_line(line):
    # 用占位符避免冲突
    # 先替换大的
    line = re.sub(r'6\.7', '6X7', line)
    line = re.sub(r'6\.6', '6X6', line)
    line = re.sub(r'6\.5', '6X5', line)
    line = re.sub(r'6\.4', '6X4', line)
    line = re.sub(r'6\.3', '6X3', line)
    # 占位符替换回目标
    line = line.replace('6X7', '6.6')
    line = line.replace('6X6', '6.5')
    line = line.replace('6X5', '6.4')
    line = line.replace('6X4', '6.3')
    line = line.replace('6X3', '6.2')
    return line

new_lines = []
for line in lines:
    # 只处理章节编号行：标题行、TOC行、交叉引用
    if (line.startswith('### 6.') or line.startswith('#### 6.') or
        line.startswith('- [6.') or line.startswith('        - [6.') or
        ' 方法日C冲' in line or ' 方法日H冲' in line or ' 方法日I冲' in line or
        ' 方法日J漏' in line or ' 方法日K漏' in line or
        ' 不是可执行策略' in line or ' 非必赢' in line or
        '见 6.' in line or '（见 6.' in line or '6.1-6.3' in line or '6.1-6.2' in line):
        new_lines.append(repl_line(line))
    else:
        new_lines.append(line)

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('编号替换完成')