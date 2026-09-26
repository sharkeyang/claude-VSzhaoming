# -*- coding: utf-8 -*-
"""验证忠/中方向倾向：DXCD维持状态时，DXZC交叉次数对比
统计 DXCD=忠/中 连续段内，DXZC 符号变化的次数
"""
import io, os, glob, sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# col8=DXCD, col14=日ZC
# 统计每个 DXCD=忠/中 连续段内，DXZC 符号变化次数
# 交叉次数 = 段内 DXZC 符号（>0 或 <0）变化的次数
seg_stats = defaultdict(lambda: {'segments': 0, 'cross_0': 0, 'cross_1': 0, 'cross_2': 0, 'cross_3plus': 0, 'total_days': 0, 'zc_pos_days': 0, 'zc_neg_days': 0})

for fi, fp in enumerate(files):
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()  # 跳过表头
        rows = []
        for line in f:
            row = line.strip().split(',')
            if len(row) < 15:
                continue
            rows.append(row)

    # 按 DXCD 分段
    i = 0
    n = len(rows)
    while i < n:
        cd = rows[i][8]
        if cd in ('忠', '中'):
            # 找到连续段
            j = i
            while j < n and rows[j][8] == cd:
                j += 1
            seg = rows[i:j]
            # 统计段内 DXZC 符号变化次数
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
            st = seg_stats[cd]
            st['segments'] += 1
            st['total_days'] += len(seg)
            if crosses == 0:
                st['cross_0'] += 1
            elif crosses == 1:
                st['cross_1'] += 1
            elif crosses == 2:
                st['cross_2'] += 1
            else:
                st['cross_3plus'] += 1
            # 统计段内 DXZC 正/负天数
            for r in seg:
                try:
                    zc = int(r[14])
                except:
                    continue
                if zc > 0:
                    st['zc_pos_days'] += 1
                elif zc < 0:
                    st['zc_neg_days'] += 1
            i = j
        else:
            i += 1

# 输出结果
print()
print('='*70)
print('DXCD 维持状态时，DXZC 交叉次数对比')
print('='*70)
for cd in ('忠', '中'):
    st = seg_stats[cd]
    total = st['segments']
    if total == 0:
        print(f'\nDXCD={cd}: 无样本')
        continue
    print(f'\nDXCD={cd}: {total} 个连续段, 共 {st["total_days"]} 天')
    print(f'  交叉0次: {st["cross_0"]} ({st["cross_0"]/total*100:.1f}%)')
    print(f'  交叉1次: {st["cross_1"]} ({st["cross_1"]/total*100:.1f}%)')
    print(f'  交叉2次: {st["cross_2"]} ({st["cross_2"]/total*100:.1f}%)')
    print(f'  交叉3+次: {st["cross_3plus"]} ({st["cross_3plus"]/total*100:.1f}%)')
    print(f'  有交叉(≥1次)占比: {(st["cross_1"]+st["cross_2"]+st["cross_3plus"])/total*100:.1f}%')
    print(f'  段内DXZC正天数: {st["zc_pos_days"]} ({st["zc_pos_days"]/st["total_days"]*100:.1f}%)')
    print(f'  段内DXZC负天数: {st["zc_neg_days"]} ({st["zc_neg_days"]/st["total_days"]*100:.1f}%)')