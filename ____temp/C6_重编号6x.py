# -*- coding: utf-8 -*-
"""
MC3.3_C6 第六章重编号：新增6.2 DXAB微观特征分析，其余顺延
规则：6.0/6.1不变；旧6.2→6.3, 旧6.3→6.4, ..., 旧6.7→6.8
只处理标题行（### 6.x / #### 6.x.y），用(?<!\d)避免误匹配数据值(26.2%)
用替换函数一次性处理，避免连续替换
"""
import sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 重编号映射（旧→新）
mapping = {'2':'3','3':'4','4':'5','5':'6','6':'7','7':'8'}

def renumber_title(line):
    """重编号标题行中的 6.x / 6.x.y（一次性替换，避免连续替换）"""
    if 'A.6' in line:
        return line
    # 处理 6.x.y（子标题）：6.{x}.{y} → 6.{new_x}.{y}
    def sub_sub(m):
        x = m.group(1)
        y = m.group(2)
        new_x = mapping.get(x, x)
        return f'6.{new_x}.{y}'
    line = re.sub(r'(?<!\d)6\.(\d)\.(\d+)', sub_sub, line)
    # 处理 6.x（主标题）：6.{x} → 6.{new_x}（避免 6.x.y）
    def sub_main(m):
        x = m.group(1)
        new_x = mapping.get(x, x)
        return f'6.{new_x}'
    # 主标题：6.x 后面不是数字也不是点（避免 6.x.y）
    line = re.sub(r'(?<!\d)6\.(\d)(?![\d.])', sub_main, line)
    return line

new_lines = []
for line in lines:
    # 只处理标题行（### 6.x / #### 6.x.y）
    if re.match(r'^#{2,4} 6\.', line):
        line = renumber_title(line)
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('标题重编号完成')