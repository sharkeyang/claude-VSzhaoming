# -*- coding: utf-8 -*-
"""
MC3.3_C6 第六章正文交叉引用重编号
规则：旧6.2→6.3, 旧6.3→6.4, ..., 旧6.7→6.8
处理 §6.x / §6.x.y 交叉引用（用(?<!\d)避免误匹配数据值）
"""
import sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 重编号映射（旧→新）
mapping = {'2':'3','3':'4','4':'5','5':'6','6':'7','7':'8'}

def renumber_ref(line):
    """重编号正文中的 §6.x / §6.x.y 交叉引用"""
    if 'A.6' in line:
        return line
    # 处理 §6.x.y（子引用）
    def sub_sub(m):
        x = m.group(1); y = m.group(2)
        return f'§6.{mapping.get(x, x)}.{y}'
    line = re.sub(r'§6\.(\d)\.(\d+)', sub_sub, line)
    # 处理 §6.x（主引用，避免 §6.x.y）
    def sub_main(m):
        x = m.group(1)
        return f'§6.{mapping.get(x, x)}'
    line = re.sub(r'§6\.(\d)(?![\d.])', sub_main, line)
    return line

new_lines = []
for line in lines:
    # 处理所有含 §6. 的行（交叉引用）
    if '§6.' in line:
        line = renumber_ref(line)
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('正文交叉引用重编号完成')