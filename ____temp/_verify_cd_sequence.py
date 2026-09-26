# -*- coding: utf-8 -*-
"""验证 DXCD 护型变化序列：DXCD<0（忐忠忑）段内护型反复变换次数
+ DXCD>0（上中下）段内护型反复变换次数
"""
import io, os, glob, sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

NEG_CD = {'忐', '忠', '忑'}
POS_CD = {'上', '中', '下'}

# 统计 DXCD<0 和 DXCD>0 段内，护型变化次数
seg_stats = defaultdict(lambda: {'segments': 0, 'change_0': 0, 'change_1': 0, 'change_2': 0, 'change_3plus': 0, 'total_days': 0})

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
        # 找到连续段（同符号组）
        j = i
        while j < n and rows[j][8] in group_set:
            j += 1
        seg = rows[i:j]
        # 统计段内护型变化次数（相邻不同）
        changes = 0
        prev_cd = None
        for r in seg:
            cur_cd = r[8]
            if prev_cd is not None and cur_cd != prev_cd:
                changes += 1
            prev_cd = cur_cd
        st = seg_stats[group]
        st['segments'] += 1
        st['total_days'] += len(seg)
        if changes == 0:
            st['change_0'] += 1
        elif changes == 1:
            st['change_1'] += 1
        elif changes == 2:
            st['change_2'] += 1
        else:
            st['change_3plus'] += 1
        i = j

print('\n=== DXCD<0 vs DXCD>0 段内护型变化次数 ===')
for group in ('DXCD<0(忐忠忑)', 'DXCD>0(上中下)'):
    st = seg_stats[group]
    total = st['segments']
    if total == 0:
        print(f'\n{group}: 无样本')
        continue
    print(f'\n{group}: {total} 个连续段, 共 {st["total_days"]} 天')
    print(f'  护型变化0次: {st["change_0"]} ({st["change_0"]/total*100:.1f}%)')
    print(f'  护型变化1次: {st["change_1"]} ({st["change_1"]/total*100:.1f}%)')
    print(f'  护型变化2次: {st["change_2"]} ({st["change_2"]/total*100:.1f}%)')
    print(f'  护型变化3+次: {st["change_3plus"]} ({st["change_3plus"]/total*100:.1f}%)')
    print(f'  有变化(≥1次)占比: {(st["change_1"]+st["change_2"]+st["change_3plus"])/total*100:.1f}%')