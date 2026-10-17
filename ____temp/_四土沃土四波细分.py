# -*- coding: utf-8 -*-
"""
扩展验证：四土沃土内部四波细分 + 与四域多长对比
确认：四土沃土 = 四土×四波交叉（沃土=龙+武）？
以及：沃土内部 龙 vs 武 的差异（是否应只取龙）
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四土沃土四波细分_result.txt'

COL_WXZC = 15
COL_WXCD = 24
COL_WXZB = 14
COL_WXAB = 19   # AB周（JA vs JB 交叉天数）
COL_HX   = 4
COL_HR   = 3

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
                wab = int(row[COL_WXAB])
                hr = float(row[COL_HR])
            except (ValueError, IndexError):
                continue
            hx = row[COL_HX]
            huji = hx[3] if len(hx) >= 4 else '?'

            # 四波判定（WXAB×WXZB）
            # 龙=AB>0且ZB>0, 武=AB<0且ZB>0, 虎=AB<0且ZB<0, 雀=AB>0且ZB<0
            if wab > 0 and wzb > 0: sibo = '龙'
            elif wab < 0 and wzb > 0: sibo = '武'
            elif wab < 0 and wzb < 0: sibo = '虎'
            elif wab > 0 and wzb < 0: sibo = '雀'
            else: sibo = '?'

            # 四域多长
            is_duo = (wzc > 0 and wcd > 0 and wzb > 0)
            # 四土沃土
            is_wo = (wzc > 0 and huji in ('上', '忐'))

            if is_duo: add('四域多长', hr)
            if is_wo: add('四土沃土', hr)
            if is_wo:
                add(f'沃土×{sibo}', hr)
            if is_duo:
                add(f'多长×{sibo}', hr)
            add('全量基线', hr)
    if fi % 1000 == 0 and fi > 0:
        print(f"  已处理 {fi}/{len(files)}", flush=True)

lines = []
lines.append("=" * 70)
lines.append("四土沃土内部四波细分 + 与四域多长对比")
lines.append("=" * 70)
lines.append("")
lines.append("四波 = WXAB×WXZB：龙=AB>0且ZB>0, 武=AB<0且ZB>0, 虎=AB<0且ZB<0, 雀=AB>0且ZB<0")
lines.append("")
for key in ['全量基线', '四域多长', '四土沃土']:
    lines.append(fmt(key, stats[key]))
lines.append("")
lines.append("--- 四土沃土内部四波细分 ---")
for sibo in ['龙', '武', '虎', '雀', '?']:
    lines.append(fmt(f'沃土×{sibo}', stats[f'沃土×{sibo}']))
lines.append("")
lines.append("--- 四域多长内部四波细分 ---")
for sibo in ['龙', '武', '虎', '雀', '?']:
    lines.append(fmt(f'多长×{sibo}', stats[f'多长×{sibo}']))
lines.append("")
lines.append("--- 关键对比 ---")
def p(key):
    s = stats[key]
    return s['ge3']/s['n']*100 if s['n'] else 0
lines.append(f"沃土×龙  P(≥3%) = {p('沃土×龙'):.2f}%  (n={stats['沃土×龙']['n']:,})")
lines.append(f"沃土×武  P(≥3%) = {p('沃土×武'):.2f}%  (n={stats['沃土×武']['n']:,})")
lines.append(f"多长×龙  P(≥3%) = {p('多长×龙'):.2f}%  (n={stats['多长×龙']['n']:,})")
lines.append(f"多长×武  P(≥3%) = {p('多长×武'):.2f}%  (n={stats['多长×武']['n']:,})")
lines.append("")
lines.append("沃土×龙 vs 沃土×武 差异 = " + f"{p('沃土×龙') - p('沃土×武'):+.2f}pp")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)