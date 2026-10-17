# -*- coding: utf-8 -*-
"""
扩展赛马：门槛（四土沃土/四域多长）× 微观条件（柱排升/非孕/盈提示/龙猪龙管/ZA）
吸取 C8 最早赛马组合思路（75组条件组合），用 P(≥3%) 赛马选出最优组合
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_扩展赛马_result.txt'

COL_WXZC = 15
COL_WXCD = 24
COL_WXZB = 14
COL_HX   = 4
COL_HR   = 3
COL_SX   = 9
COL_BX   = 5   # 波型
COL_ZP   = 6   # 柱排
COL_ZX   = 7   # 柱型
COL_YT   = 12  # 盈提示
COL_ZA   = 13  # ZA

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

            # 微观条件
            zp_sheng = zp.startswith('升')  # 柱排升
            fei_yun = '孕' not in zx  # 非孕
            yt_you = len(yt) > 0  # 盈提示有
            long_zhu = '龙扩猪' in bx  # 龙猪
            long_guan = '龙扩管' in bx  # 龙管
            long_zg = long_zhu or long_guan  # 龙猪/龙管
            za_510 = 5 <= za <= 10  # ZA 5~10

            # 门槛 × 微观条件
            for gate_name, gate in [('沃土', is_wo), ('多长', is_duo)]:
                if not gate: continue
                # 单条件
                if zp_sheng: add(f'{gate_name}+升排', hr)
                if fei_yun: add(f'{gate_name}+非孕', hr)
                if yt_you: add(f'{gate_name}+盈有', hr)
                if long_zg: add(f'{gate_name}+龙猪管', hr)
                if za_510: add(f'{gate_name}+ZA5-10', hr)
                # 双条件
                if zp_sheng and fei_yun: add(f'{gate_name}+升排非孕', hr)
                if zp_sheng and yt_you: add(f'{gate_name}+升排盈有', hr)
                if zp_sheng and long_zg: add(f'{gate_name}+升排龙猪管', hr)
                if fei_yun and yt_you: add(f'{gate_name}+非孕盈有', hr)
                if yt_you and long_zg: add(f'{gate_name}+盈有龙猪管', hr)
                if zp_sheng and za_510: add(f'{gate_name}+升排ZA5-10', hr)
                # 三条件
                if zp_sheng and fei_yun and yt_you: add(f'{gate_name}+升排非孕盈有', hr)
                if zp_sheng and fei_yun and long_zg: add(f'{gate_name}+升排非孕龙猪管', hr)
                if zp_sheng and yt_you and long_zg: add(f'{gate_name}+升排盈有龙猪管', hr)
                if fei_yun and yt_you and long_zg: add(f'{gate_name}+非孕盈有龙猪管', hr)
                # 四条件
                if zp_sheng and fei_yun and yt_you and long_zg: add(f'{gate_name}+升排非孕盈有龙猪管', hr)

            # 门槛本身
            if is_wo: add('沃土(门槛)', hr)
            if is_duo: add('多长(门槛)', hr)
            add('全量基线', hr)
    if fi % 1000 == 0 and fi > 0:
        print(f"  已处理 {fi}/{len(files)}", flush=True)

# 收集并按 P(≥3%) 排序
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
lines.append("扩展赛马：门槛 × 微观条件（按 P(≥3%) 降序）")
lines.append("=" * 80)
lines.append("")
lines.append(f"{'条件':<34}{'n':>12}{'P(≥3%)':>10}{'P(>0)':>9}{'均高幅':>9}")
lines.append("-" * 80)
for key, n, p_ge3, p_gt0, avg in results:
    lines.append(f"{key:<34}{n:>12,}{p_ge3:>9.2f}%{p_gt0:>8.2f}%{avg:>8.3f}%")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)