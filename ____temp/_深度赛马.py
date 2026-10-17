# -*- coding: utf-8 -*-
"""
深度赛马：沃土门槛内，叠加 ZA 区间 / 波型细分 / 盈提示细分 / 柱排细分
对比多长门槛，找出最优微观条件组合
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_深度赛马_result.txt'

COL_WXZC = 15
COL_WXCD = 24
COL_WXZB = 14
COL_HX   = 4
COL_HR   = 3
COL_BX   = 5
COL_ZP   = 6
COL_ZX   = 7
COL_YT   = 12
COL_ZA   = 13

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
                hr = float(row[COL_HR])
                za = int(row[COL_ZA])
            except (ValueError, IndexError):
                continue
            hx = row[COL_HX]
            huji = hx[3] if len(hx) >= 4 else '?'
            bx = row[COL_BX]
            zp = row[COL_ZP]
            zx = row[COL_ZX]
            yt = row[COL_YT]

            is_duo = (wzc > 0 and wcd > 0 and wzb > 0)
            is_wo = (wzc > 0 and huji in ('上', '忐'))

            # ZA 区间
            if za <= 0: za_grp = 'ZA≤0'
            elif za <= 2: za_grp = 'ZA1-2'
            elif za <= 4: za_grp = 'ZA3-4'
            elif za <= 10: za_grp = 'ZA5-10'
            else: za_grp = 'ZA>10'

            # 波型细分
            if '龙扩猪' in bx: bx_grp = '龙扩猪'
            elif '龙扩管' in bx: bx_grp = '龙扩管'
            elif '龙震' in bx: bx_grp = '龙震'
            elif '龙头' in bx: bx_grp = '龙头'
            elif '虎' in bx: bx_grp = '虎'
            elif '雀' in bx: bx_grp = '雀'
            elif '武' in bx: bx_grp = '武'
            else: bx_grp = '其他'

            # 盈提示细分
            if '高' in yt: yt_grp = '盈高'
            elif '宽' in yt: yt_grp = '盈宽'
            elif len(yt) > 0: yt_grp = '盈其他'
            else: yt_grp = '盈无'

            # 柱排
            if zp.startswith('升'): zp_grp = '升排'
            elif zp.startswith('跌'): zp_grp = '跌排'
            else: zp_grp = '人排'

            # 非孕
            fei_yun = '孕' not in zx

            # 在沃土/多长门槛内叠加
            for gate_name, gate in [('沃土', is_wo), ('多长', is_duo)]:
                if not gate: continue
                # ZA 区间
                add(f'{gate_name}+{za_grp}', hr)
                # 波型细分
                add(f'{gate_name}+{bx_grp}', hr)
                # 盈提示细分
                add(f'{gate_name}+{yt_grp}', hr)
                # 柱排
                add(f'{gate_name}+{zp_grp}', hr)
                # 非孕
                if fei_yun: add(f'{gate_name}+非孕', hr)
                # 组合：ZA5-10 + 波型
                if za_grp == 'ZA5-10' and bx_grp in ('龙扩猪', '龙扩管'):
                    add(f'{gate_name}+ZA5-10龙猪管', hr)
                # 组合：升排 + ZA5-10
                if zp_grp == '升排' and za_grp == 'ZA5-10':
                    add(f'{gate_name}+升排ZA5-10', hr)
                # 组合：盈高 + 龙猪管
                if yt_grp == '盈高' and bx_grp in ('龙扩猪', '龙扩管'):
                    add(f'{gate_name}+盈高龙猪管', hr)

            if is_wo: add('沃土(门槛)', hr)
            if is_duo: add('多长(门槛)', hr)
            add('全量基线', hr)
    if fi % 1000 == 0 and fi > 0:
        print(f"  已处理 {fi}/{len(files)}", flush=True)

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
lines.append("深度赛马：沃土/多长门槛 × ZA区间/波型细分/盈提示细分/柱排（按 P(≥3%) 降序）")
lines.append("=" * 80)
lines.append("")
lines.append(f"{'条件':<34}{'n':>12}{'P(≥3%)':>10}{'P(>0)':>9}{'均高幅':>9}")
lines.append("-" * 80)
for key, n, p_ge3, p_gt0, avg in results:
    lines.append(f"{key:<34}{n:>12,}{p_ge3:>9.2f}%{p_gt0:>8.2f}%{avg:>8.3f}%")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)