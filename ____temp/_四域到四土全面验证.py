# -*- coding: utf-8 -*-
"""
全面验证：四域 → 四土 替代方案数据支撑
回答"应该怎么改"——C8 中所有用到四域的地方，用四土替代后的数据对比

金条件 = col9势型=金 + col4护型∈{甲乙己}
银条件 = 四域不在金区但 WXZC>0（原定义）
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四域到四土全面验证_result.txt'

COL_WXZC = 15
COL_WXCD = 24
COL_WXZB = 14
COL_WXAB = 19
COL_HX   = 4
COL_HR   = 3
COL_SX   = 9   # 周势型

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
            sx_jin = (len(sx) >= 2 and sx[1] == '金')  # 势型=金
            jyj = hx_letter in ('a', 'b', 'r')  # 甲乙己

            # 金条件 = 势型金 + 甲乙己
            is_jin = sx_jin and jyj
            # 四域多长
            is_duo = (wzc > 0 and wcd > 0 and wzb > 0)
            # 四土沃土
            is_wo = (wzc > 0 and huji in ('上', '忐'))

            # 入场门槛对比
            if is_duo: add('门槛:四域多长', hr)
            if is_wo: add('门槛:四土沃土', hr)

            # <金长> = 金+甲乙己+多长  vs  <金沃> = 金+甲乙己+沃土
            if is_jin and is_duo: add('<金长>=金+甲乙己+多长', hr)
            if is_jin and is_wo: add('<金沃>=金+甲乙己+沃土', hr)

            # 银条件：原定义=四域不在金区但WXZC>0
            # 金区 = 势型金+甲乙己（即 is_jin）
            # 银条件 = 非金 + WXZC>0
            if (not is_jin) and wzc > 0:
                add('银条件(原):非金+WXZC>0', hr)
            # 银条件用四土表达：非沃土 + WXZC>0（即执念土）
            if (not is_wo) and wzc > 0:
                add('银条件(四土):非沃土+WXZC>0', hr)

            # 四域 vs 四土 全量
            add('全量基线', hr)
    if fi % 1000 == 0 and fi > 0:
        print(f"  已处理 {fi}/{len(files)}", flush=True)

lines = []
lines.append("=" * 72)
lines.append("四域 → 四土 替代方案数据支撑（全量周类）")
lines.append("=" * 72)
lines.append("")
lines.append("定义：")
lines.append("  金条件 = 势型金 + 甲乙己")
lines.append("  四域多长 = WXZC>0 + WXCD>0 + WXZB>0")
lines.append("  四土沃土 = WXZC>0 + 护级∈{上,忐}")
lines.append("")
lines.append("评估口径：下周冲高≥3%概率 P(≥3%)")
lines.append("")
lines.append("--- ① 入场门槛 ---")
lines.append(fmt('门槛:四域多长', stats['门槛:四域多长']))
lines.append(fmt('门槛:四土沃土', stats['门槛:四土沃土']))
lines.append("")
lines.append("--- ② <金长> vs <金沃> ---")
lines.append(fmt('<金长>=金+甲乙己+多长', stats['<金长>=金+甲乙己+多长']))
lines.append(fmt('<金沃>=金+甲乙己+沃土', stats['<金沃>=金+甲乙己+沃土']))
lines.append("")
lines.append("--- ③ 银条件 ---")
lines.append(fmt('银条件(原):非金+WXZC>0', stats['银条件(原):非金+WXZC>0']))
lines.append(fmt('银条件(四土):非沃土+WXZC>0', stats['银条件(四土):非沃土+WXZC>0']))
lines.append("")
lines.append("--- 全量基线 ---")
lines.append(fmt('全量基线', stats['全量基线']))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)