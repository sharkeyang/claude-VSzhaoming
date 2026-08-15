#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表月策分命.txt
从昭明花册.xlsx 提取命分数据
命分 = 几何均值 = (∏(1+每次收益))^(1/交易次数) - 1
输出：代码\t命分
"""

import pandas as pd, os, numpy as np

OUTDIR = r'_产出物/_工具'
SRC = r'D:/zdata/昭明花册.xlsx'

print('=== 生成 vba表月策分命.txt ===')

# 读取花册
df = pd.read_excel(SRC, sheet_name=1)
print(f'  花册行数: {len(df)}')

# 查找命分相关列
命分列 = None
for c in df.columns:
    if '命' in str(c):
        命分列 = c
        print(f'  找到命分列: {repr(c)}')
        break

if 命分列 is None:
    # 没有命分列，从收益数据计算几何均值
    # 查找PR1-PR9列
    pr_cols = [c for c in df.columns if 'PR' in str(c) and str(c).replace('PR', '').isdigit()]
    if pr_cols:
        print(f'  从{len(pr_cols)}个PR列计算几何均值')
        # 计算几何均值
        def 几何均值(row):
            vals = []
            for c in pr_cols:
                v = row[c]
                if pd.notna(v) and v != 0:
                    vals.append(1 + v/100)
            if len(vals) >= 3:
                return round((np.prod(vals))**(1/len(vals)) - 1, 4)
            return 0
        df['命分'] = df.apply(几何均值, axis=1)
        命分列 = '命分'
    else:
        print('  ❌ 未找到命分列或PR列，无法生成')
        exit(1)

# 输出
lines = ['代码\t命分']
for _, row in df.iterrows():
    cid = row['CIDL']
    mf = row[命分列]
    if pd.notna(mf) and mf != 0:
        lines.append(f'{cid}\t{mf}')

outpath = os.path.join(OUTDIR, 'vba表月策分命.txt')
with open(outpath, 'w', encoding='gbk') as f:
    f.write('\n'.join(lines))
print(f'  共{len(lines)-1}条 -> {outpath}')