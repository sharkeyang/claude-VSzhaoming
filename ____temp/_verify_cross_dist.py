# -*- coding: utf-8 -*-
"""统计 DXCD<0（忐忠忑）vs DXCD>0（上中下）段内 DXZC 交叉次数分布
最多/最少/平均/中位
"""
import io, os, glob, sys
from collections import defaultdict
import statistics

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

NEG_CD = {'忐', '忠', '忑'}
POS_CD = {'上', '中', '下'}

# 收集每个段的 DXZC 交叉次数
cross_counts = defaultdict(list)  # group -> [交叉次数列表]
seg_days = defaultdict(list)      # group -> [段天数列表]

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        rows = []
        for line in f:
            row = line.strip().split(',')
            if len(row) < 15:
                continue
            rows.append(row)

    i = 0
    n = len(rows)
    while i < n:
        cd = rows[i][8]
        if cd in NEG_CD:
            group = 'DXCD<0(忐忠忑)'
            group_set = NEG_CD
        elif cd in POS_CD:
            group = 'DXCD>0(上中下)'
            group_set = POS_CD
        else:
            i += 1
            continue
        j = i
        while j < n and rows[j][8] in group_set:
            j += 1
        seg = rows[i:j]
        # 统计段内 DXZC 交叉次数
        crosses = 0
        prev_sign = None
        for r in seg:
            try:
                zc = int(r[14])
            except:
                continue
            sign = 1 if zc > 0 else (-1 if zc < 0 else 0)
            if sign != 0:
                if prev_sign is not None and prev_sign != sign:
                    crosses += 1
                prev_sign = sign
        cross_counts[group].append(crosses)
        seg_days[group].append(len(seg))
        i = j

print('\n=== DXCD<0 vs DXCD>0 段内 DXZC 交叉次数分布 ===')
for group in ('DXCD<0(忐忠忑)', 'DXCD>0(上中下)'):
    counts = cross_counts[group]
    days = seg_days[group]
    total = len(counts)
    if total == 0:
        print(f'\n{group}: 无样本')
        continue
    print(f'\n{group}: {total} 个连续段')
    print(f'  交叉次数: 最少 {min(counts)}, 最多 {max(counts)}, 平均 {statistics.mean(counts):.2f}, 中位 {statistics.median(counts)}')
    print(f'  段天数: 最少 {min(days)}, 最多 {max(days)}, 平均 {statistics.mean(days):.1f}, 中位 {statistics.median(days)}')
    # 交叉次数分布（0,1,2,3,4,5+）
    from collections import Counter
    dist = Counter(counts)
    print(f'  交叉次数分布:')
    for k in sorted(dist.keys()):
        if k <= 5:
            print(f'    交叉{k}次: {dist[k]} ({dist[k]/total*100:.1f}%)')
        else:
            break
    # 5次以上合计
    over5 = sum(v for k, v in dist.items() if k > 5)
    if over5 > 0:
        print(f'    交叉5+次: {over5} ({over5/total*100:.1f}%)')