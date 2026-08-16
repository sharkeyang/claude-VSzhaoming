#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表日策分P2.txt
日策分P2查表文件，编码格式：期望HR取整 + 等级(A-F) + 策分取整（如"5B58"）
数据来源：硬编码（等高线+条件评分映射），与VBA中 IQQQ跨码工具_查日策分P2 对应

用法：
    python _产出物/_工具/vba表日策分P2.py
"""

import os

OUTDIR = r'_产出物/_工具'

def 等级(score):
    if score > 60: return 'A'
    if score >= 50: return 'B'
    if score >= 40: return 'C'
    if score >= 30: return 'D'
    return 'E'

# 策略名 → 策分（与VBA中等高线+条件评分映射一致）
strategies = [
    ('等3.偏5连门', 58),
    ('等3.偏5', 54),
    ('等3.偏3连门', 53),
    ('等3.连', 49),
    ('等3.层主', 44),
    ('等3.跌排', 37),
    ('等1.偏5连门', 61),
    ('等1.偏5', 56),
    ('等1.层主', 44),
    ('等2.偏5连门', 58),
    ('等2.偏5', 57),
    ('等2.偏3连门', 53),
    ('等2.偏3', 51),
    ('等2.连', 48),
    ('等2.层主升', 45),
    ('等2.升', 40),
    ('等2.跌排', 39),
    ('等5.偏5', 61),
    ('等5.偏3', 53),
    ('等6.偏5', 52),
    ('等6.偏3', 49),
    ('等7.偏5', 54),
    ('等7.偏3', 51),
]

lines = ['策略名\t编码']
for name, score in strategies:
    exp_hr = score // 10  # 期望HR近似
    grade = 等级(score)
    code = f'{exp_hr}{grade}{score}'
    lines.append(f'{name}\t{code}')

outpath = os.path.join(OUTDIR, 'vba表日策分P2.txt')
with open(outpath, 'w', encoding='gbk') as f:
    f.write('\n'.join(lines))
print(f'  共{len(strategies)}个组合 -> {outpath}')