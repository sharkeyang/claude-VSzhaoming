# -*- coding: utf-8 -*-
"""
验证：用四土沃土替代四域多长作为周冲门槛
对比两者作为周冲门槛的区分度（下周冲高≥3%概率）

四域多长 = WXZC>0 + WXCD>0 + WXZB>0  (col15>0 + col24>0 + col14>0)
四土沃土 = WXZC>0 + WXAB护级∈{上,忐}  (col15>0 + col4[3]∈{上,忐})

评估口径：下周冲高≥3%概率（P(≥3%)），与 C7 §6.2.1.9 四域/四波对比一致
"""
import csv, glob, os, sys
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四土沃土vs四域多长_result.txt'

# 列索引（0-based，来自元数据）
COL_WXZC = 15   # ZC周
COL_WXCD = 24   # CD周
COL_WXZB = 14   # ZB周
COL_HX   = 4    # 周层护型
COL_HR   = 3    # 临高幅（下周冲高幅度）

# 统计容器
stats = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'gt0': 0})

def add(stats_key, hr):
    """hr = 下周冲高幅度（col3 临高幅）"""
    s = stats[stats_key]
    s['n'] += 1
    s['sum_hr'] += hr
    if hr >= 3.0:
        s['ge3'] += 1
    if hr > 0:
        s['gt0'] += 1

def fmt(key, s):
    n = s['n']
    if n == 0:
        return f"{key}: n=0"
    p_ge3 = s['ge3'] / n * 100
    p_gt0 = s['gt0'] / n * 100
    avg = s['sum_hr'] / n
    return f"{key}: n={n:>9,}  P(≥3%)={p_ge3:6.2f}%  P(>0)={p_gt0:6.2f}%  均高幅={avg:6.3f}%"

files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f"共 {len(files)} 个文件", flush=True)

processed = 0
for fi, fp in enumerate(files):
    with open(fp, encoding='gbk') as f:
        r = csv.reader(f)
        try:
            header = next(r)
        except StopIteration:
            continue
        for row in r:
            if len(row) < 25:
                continue
            try:
                wzc = int(row[COL_WXZC])
                wcd = int(row[COL_WXCD])
                wzb = int(row[COL_WXZB])
                hr = float(row[COL_HR])
            except (ValueError, IndexError):
                continue
            hx = row[COL_HX]
            huji = hx[3] if len(hx) >= 4 else '?'

            # 四域多长
            if wzc > 0 and wcd > 0 and wzb > 0:
                add('四域多长', hr)
            # 四土沃土
            if wzc > 0 and huji in ('上', '忐'):
                add('四土沃土', hr)
            # 交集（同时满足）
            if (wzc > 0 and wcd > 0 and wzb > 0) and (wzc > 0 and huji in ('上', '忐')):
                add('交集(多长∩沃土)', hr)
            # 四域多长 但 非四土沃土
            if (wzc > 0 and wcd > 0 and wzb > 0) and not (wzc > 0 and huji in ('上', '忐')):
                add('多长-非沃土', hr)
            # 四土沃土 但 非四域多长
            if (wzc > 0 and huji in ('上', '忐')) and not (wzc > 0 and wcd > 0 and wzb > 0):
                add('沃土-非多长', hr)
            # 全量基线
            add('全量基线', hr)
    processed += 1
    if processed % 1000 == 0:
        print(f"  已处理 {processed}/{len(files)}", flush=True)

lines = []
lines.append("=" * 70)
lines.append("四土沃土 vs 四域多长 作为周冲门槛对比")
lines.append("=" * 70)
lines.append("")
lines.append("定义：")
lines.append("  四域多长 = WXZC>0 + WXCD>0 + WXZB>0")
lines.append("  四土沃土 = WXZC>0 + WXAB护级∈{上,忐}")
lines.append("")
lines.append("评估口径：下周冲高≥3%概率 P(≥3%)")
lines.append("")
for key in ['全量基线', '四域多长', '四土沃土', '交集(多长∩沃土)', '多长-非沃土', '沃土-非多长']:
    lines.append(fmt(key, stats[key]))
lines.append("")

# 区分度计算
def p_ge3(key):
    s = stats[key]
    return s['ge3'] / s['n'] * 100 if s['n'] else 0

# 四域多长的区分度（多长 vs 非多长）
n_duo = stats['四域多长']['n']
n_not_duo = stats['全量基线']['n'] - n_duo
p_duo = p_ge3('四域多长')
p_not_duo = (stats['全量基线']['ge3'] - stats['四域多长']['ge3']) / n_not_duo * 100 if n_not_duo else 0
lines.append(f"四域多长区分度: 多长 {p_duo:.2f}% vs 非多长 {p_not_duo:.2f}% = {p_duo - p_not_duo:.2f}pp")

# 四土沃土的区分度（沃土 vs 非沃土）
n_wo = stats['四土沃土']['n']
n_not_wo = stats['全量基线']['n'] - n_wo
p_wo = p_ge3('四土沃土')
p_not_wo = (stats['全量基线']['ge3'] - stats['四土沃土']['ge3']) / n_not_wo * 100 if n_not_wo else 0
lines.append(f"四土沃土区分度: 沃土 {p_wo:.2f}% vs 非沃土 {p_not_wo:.2f}% = {p_wo - p_not_wo:.2f}pp")

lines.append("")
lines.append("关键对比：")
lines.append(f"  四域多长 P(≥3%) = {p_duo:.2f}%  (n={n_duo:,})")
lines.append(f"  四土沃土 P(≥3%) = {p_wo:.2f}%  (n={n_wo:,})")
lines.append(f"  差异 = {p_wo - p_duo:+.2f}pp")
lines.append("")
lines.append("交集分析：")
lines.append(f"  交集(多长∩沃土) 样本 = {stats['交集(多长∩沃土)']['n']:,}")
lines.append(f"  多长-非沃土 样本 = {stats['多长-非沃土']['n']:,}  P(≥3%)={p_ge3('多长-非沃土'):.2f}%")
lines.append(f"  沃土-非多长 样本 = {stats['沃土-非多长']['n']:,}  P(≥3%)={p_ge3('沃土-非多长'):.2f}%")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("\n完成，结果写入", OUT)