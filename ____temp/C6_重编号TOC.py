# -*- coding: utf-8 -*-
"""
MC3.3_C6 第六章 TOC 重编号：更新目录编号和锚点
规则：旧6.2→6.3, 旧6.3→6.4, ..., 旧6.7→6.8
处理 TOC 行（- [6.x ...]）的编号和锚点（#62-...）
锚点只改主章节号（#6X → #6{new}），子章节号不变
"""
import sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 重编号映射（旧→新）
mapping = {'2':'3','3':'4','4':'5','5':'6','6':'7','7':'8'}

def renumber_toc(line):
    """重编号 TOC 行的编号和锚点"""
    if 'A.6' in line:
        return line
    # 1. 处理编号部分 [6.x ...] 或 [6.x.y ...]（保留 [）
    def sub_num(m):
        x = m.group(1)
        return f'[6.{mapping.get(x, x)}'
    line = re.sub(r'\[6\.(\d)(?![\d.])', sub_num, line)  # 主编号 6.x
    def sub_num_sub(m):
        x = m.group(1); y = m.group(2)
        return f'[6.{mapping.get(x, x)}.{y}'
    line = re.sub(r'\[6\.(\d)\.(\d+)', sub_num_sub, line)  # 子编号 6.x.y
    # 2. 处理锚点部分 (#62-... 或 #621-...)，只改主章节号，保留 #6 和 -
    def sub_anchor(m):
        x = m.group(1)
        return f'#6{mapping.get(x, x)}'
    line = re.sub(r'#6(\d)', sub_anchor, line)  # #62 → #63, #621 → #631, #6441 → #6541
    return line

new_lines = []
for line in lines:
    # 只处理 TOC 行（- [6.x ...]）
    if re.match(r'^\s*- \[6\.', line):
        line = renumber_toc(line)
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('TOC重编号完成')