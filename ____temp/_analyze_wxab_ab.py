# -*- coding: utf-8 -*-
"""分析 WXAB 持续周数(AB周) 各区间 下周冲高(HR>=3%) 概率
谕组周CSV: 主期[0] 周涨[1] PR[2] HR[3] AB周[21] ZC周[16]
下周冲高 = 同一股票下一行的 HR >= 3
"""
import sys, csv, glob
sys.stdout.reconfigure(encoding='utf-8')

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
print(f'股票数: {len(files)}')

# 区间定义
bins = [
    ('AB=1(刚转正交)', 1, 1),
    ('AB=2', 2, 2),
    ('AB=3', 3, 3),
    ('AB=4-6', 4, 6),
    ('AB=7-10', 7, 10),
    ('AB=11-20', 11, 20),
    ('AB>20', 21, 999),
    ('AB<0(负交)', -999, -1),
]
stats = {k: [0, 0] for k, _, _ in bins}  # [冲高次数, 总次数]

for f in files:
    with open(f, encoding='gbk') as fh:
        # 增量读取，只取需要的列
        reader = csv.reader(fh)
        next(reader)  # 跳过表头
        prev_ab = None
        for row in reader:
            if len(row) < 22:
                prev_ab = None
                continue
            try:
                ab = int(row[21])
                hr = float(row[3])
            except:
                prev_ab = None
                continue
            # 用上一行的AB周，看本周HR是否>=3（即上周AB周对应的下周冲高）
            if prev_ab is not None:
                for k, lo, hi in bins:
                    if lo <= prev_ab <= hi:
                        stats[k][1] += 1
                        if hr >= 3:
                            stats[k][0] += 1
                        break
            prev_ab = ab

print()
print(f'{"区间":<16}{"样本":>8}{"下周HR≥3%":>10}{"概率":>8}')
for k, _, _ in bins:
    hit, total = stats[k]
    pct = hit / total * 100 if total else 0
    print(f'{k:<16}{total:>8}{hit:>10}{pct:>7.1f}%')