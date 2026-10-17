# -*- coding: utf-8 -*-
"""
深入验证：银条件在四土中的分布 + 完全去掉四域的替代方案
核心发现：四域多长 = 金+甲乙己（完全相等）
银条件 = 非多长 + WXZC>0，需理解其在四土中的分布
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_银条件四土分布_result.txt'

COL_WXZC = 15
COL_WXCD = 24
COL_WXZB = 14
COL_HX   = 4
COL_HR   = 3
COL_SX   = 9

stats = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'gt0': 0})

def add(key, hr):
    s = stats[key]
    s['n'] += 1
    s['sum_hr'] += hr
    if hr >= 3.0: s['ge3'] += 1
    if hr > 0: s['gt0'] += 1

def fmt(key, s):
    n = s['n']
    if n == 0: return f"{key}: n=0"
    return f"{key}: n={n:>9,}  P(≥3%)={s['ge3']/n*100:6.2f}%  P(>0)={s['gt0']/n*100:6.2f}%  均高幅={s['sum_hr']/n:6.3f}%"

files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f"共 {len(files)} 个文件", flush=True)

for fi, fp in enumerate(files):
    with open(fp, encoding='gbk') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) < 25: continue
            try:
                wzc = int(row[COL_WXZC])
                wcd = int(row[COL_WXCD])
                wzb = int(row[COL_WXZB])
                hr = float(row[COL_HR])
            except (ValueError, IndexError):
                continue
            hx = row[COL_HX]
            huji = hx[3] if len(hx) >= 4 else '?'
            hx_letter = hx[0] if len(hx) >= 1 else '?'
            sx = row[COL_SX]
            sx_jin = (len(sx) >= 2 and sx[1] == '金')
            jyj = hx_letter in ('a', 'b', 'r')
            is_jin = sx_jin and jyj
            is_duo = (wzc > 0 and wcd > 0 and wzb > 0)
            is_wo = (wzc > 0 and huji in ('上', '忐'))

            # 四土判定
            if wzc > 0 and huji in ('上', '忐'): situ = '沃土'
            elif wzc < 0 and huji in ('下', '忑'): situ = '禁土'
            elif wzc > 0: situ = '执念土'
            else: situ = '鸡肋土'

            # 银条件 = 非多长 + WXZC>0
            if (not is_duo) and wzc > 0:
                add('银条件(非多长+ZC>0)', hr)
                add(f'银条件×{situ}', hr)

            # 金条件 = 金+甲乙己
            if is_jin:
                add('金条件(金+甲乙己)', hr)

            # 四土各区域
            add(f'四土:{situ}', hr)

            add('全量基线', hr)
    if fi % 1000 == 0 and fi > 0:
        print(f"  已处理 {fi}/{len(files)}", flush=True)

lines = []
lines.append("=" * 72)
lines.append("银条件在四土中的分布 + 完全去掉四域替代方案")
lines.append("=" * 72)
lines.append("")
lines.append("核心发现：四域多长 = 金+甲乙己（完全相等）")
lines.append("")
lines.append("--- 金条件 vs 四域多长 ---")
lines.append(fmt('金条件(金+甲乙己)', stats['金条件(金+甲乙己)']))
lines.append("")
lines.append("--- 四土各区域 ---")
for s in ['沃土', '鸡肋土', '执念土', '禁土']:
    lines.append(fmt(f'四土:{s}', stats[f'四土:{s}']))
lines.append("")
lines.append("--- 银条件(非多长+ZC>0) 在四土中的分布 ---")
lines.append(fmt('银条件(非多长+ZC>0)', stats['银条件(非多长+ZC>0)']))
for s in ['沃土', '鸡肋土', '执念土', '禁土']:
    lines.append(fmt(f'银条件×{s}', stats[f'银条件×{s}']))
lines.append("")
lines.append("--- 全量基线 ---")
lines.append(fmt('全量基线', stats['全量基线']))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)