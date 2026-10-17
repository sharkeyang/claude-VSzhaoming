# -*- coding: utf-8 -*-
"""
赛马验证：所有候选周冲门槛组合条件，用 P(≥3%) 赛马选出最优
覆盖维度：四土 × 四波 × 金/银 × 护型 × 势型
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_赛马门槛_result.txt'

COL_WXZC = 15
COL_WXCD = 24
COL_WXZB = 14
COL_WXAB = 19
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

            # 四波判定
            if wab > 0 and wzb > 0: sibo = '龙'
            elif wab < 0 and wzb > 0: sibo = '武'
            elif wab < 0 and wzb < 0: sibo = '虎'
            elif wab > 0 and wzb < 0: sibo = '雀'
            else: sibo = '?'

            # 候选门槛条件（赛马）
            # 基础
            add('全量基线', hr)
            # 四域
            if is_duo: add('四域多长', hr)
            # 四土
            add(f'四土:{situ}', hr)
            # 四土×四波
            add(f'四土:{situ}×{sibo}', hr)
            # 金/银
            if is_jin: add('金+甲乙己', hr)
            if (not is_duo) and wzc > 0: add('银(非多长+ZC>0)', hr)
            # 沃土×龙/武
            if is_wo and sibo == '龙': add('沃土×龙', hr)
            if is_wo and sibo == '武': add('沃土×武', hr)
            # 多长×龙/武
            if is_duo and sibo == '龙': add('多长×龙', hr)
            if is_duo and sibo == '武': add('多长×武', hr)
            # 沃土+金
            if is_wo and is_jin: add('沃土+金+甲乙己', hr)
            # 沃土+银
            if is_wo and (not is_jin): add('沃土+非金', hr)
            # 鸡肋土×龙/武/虎
            if situ == '鸡肋土' and sibo in ('龙', '武', '虎'):
                add(f'鸡肋土×{sibo}', hr)
    if fi % 1000 == 0 and fi > 0:
        print(f"  已处理 {fi}/{len(files)}", flush=True)

# 收集所有 key，按 P(≥3%) 排序
results = []
for key, s in stats.items():
    n = s['n']
    if n == 0: continue
    p_ge3 = s['ge3'] / n * 100
    p_gt0 = s['gt0'] / n * 100
    avg = s['sum_hr'] / n
    results.append((key, n, p_ge3, p_gt0, avg))

results.sort(key=lambda x: -x[2])

lines = []
lines.append("=" * 80)
lines.append("赛马：所有候选周冲门槛组合条件（按 P(≥3%) 降序）")
lines.append("=" * 80)
lines.append("")
lines.append(f"{'条件':<28}{'n':>12}{'P(≥3%)':>10}{'P(>0)':>9}{'均高幅':>9}")
lines.append("-" * 80)
for key, n, p_ge3, p_gt0, avg in results:
    lines.append(f"{key:<28}{n:>12,}{p_ge3:>9.2f}%{p_gt0:>8.2f}%{avg:>8.3f}%")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)