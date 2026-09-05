# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.1_研究月基策略.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

def find_line(prefix):
    for i, l in enumerate(lines):
        if l.startswith(prefix):
            return i
    return -1

# 定位
i_431 = find_line('#### 4.1.3.1 宽范围表')
i_432 = find_line('#### 4.1.3.2 禁区范围')
i_433 = find_line('#### 4.1.3.3 剩余范围')
i_414 = find_line('#### 4.1.4 本章小结')

print(f'4.1.3.1: {i_431}')
print(f'4.1.3.2: {i_432}')
print(f'4.1.3.3: {i_433}')
print(f'4.1.4: {i_414}')

# 当前顺序: 4.1.3.1(宽范围表) → 4.1.3.2 → 4.1.3.3 → ② → ③ → 4.1.4
# 目标顺序: 4.1.3.1(宽范围表+②+③) → 4.1.3.2 → 4.1.3.3 → 4.1.4

# 4.1.3.1 宽范围表块: 从 i_431 到 i_432 (不含)
block_431_table = lines[i_431:i_432]
# 4.1.3.2 块: 从 i_432 到 i_433 (不含)
block_432 = lines[i_432:i_433]
# 4.1.3.3 块: 从 i_433 到 ② (不含) — ② 在 4.1.3.3 之后
i_2 = find_line('**② WXCD 优选等级')
block_433 = lines[i_433:i_2]
# ② + ③ 块: 从 ② 到 4.1.4 (不含)
block_23 = lines[i_2:i_414]

# 新顺序: 4.1.3.1(宽范围表) + ②③ + 4.1.3.2 + 4.1.3.3 + 4.1.4
new_lines = lines[:i_431] + block_431_table + block_23 + block_432 + block_433 + lines[i_414:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('已调整: 4.1.3.1(宽范围表+②③) → 4.1.3.2 → 4.1.3.3')
