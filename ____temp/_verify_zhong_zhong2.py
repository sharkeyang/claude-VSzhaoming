# -*- coding: utf-8 -*-
"""重新验证忠/中方向倾向：
1. 确认 DXCD 各值的 DXZC 符号
2. DXCD<0（忐/忠/忑）连续段内 DXZC 交叉次数
3. DXCD>0（上/中/下）连续段内 DXZC 交叉次数
4. DXCD 护型变化序列（忐/忠/忑 之间反复变换）
"""
import io, os, glob, sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# col8=DXCD, col14=日ZC
# 先确认 DXCD 各值的 DXZC 符号
cd_zc_sign = defaultdict(Counter)  # cd -> {正/负: 天数}
for fp in files[:200]:  # 抽样200个文件确认
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 15:
                continue
            cd = row[8]
            try:
                zc = int(row[14])
            except:
                continue
            if zc > 0:
                cd_zc_sign[cd]['正'] += 1
            elif zc < 0:
                cd_zc_sign[cd]['负'] += 1

print('\n=== DXCD 各值的 DXZC 符号（抽样200文件）===')
for cd in ('上', '中', '下', '忐', '忠', '忑'):
    st = cd_zc_sign[cd]
    total = st['正'] + st['负']
    if total > 0:
        print(f'  DXCD={cd}: 正{st["正"]}({st["正"]/total*100:.1f}%) 负{st["负"]}({st["负"]/total*100:.1f}%)')

# ============ 统计 DXCD<0（忐/忠/忑）和 DXCD>0（上/中/下）连续段内 DXZC 交叉次数 ============
# DXCD<0 = 均线空头 = 忐/忠/忑
# DXCD>0 = 均线多头 = 上/中/下
NEG_CD = {'忐', '忠', '忑'}
POS_CD = {'上', '中', '下'}

seg_stats = defaultdict(lambda: {'segments': 0, 'cross_0': 0, 'cross_1': 0, 'cross_2': 0, 'cross_3plus': 0, 'total_days': 0})

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
        # 判断当前段属于 DXCD<0 还是 DXCD>0
        if cd in NEG_CD:
            group = 'DXCD<0(忐忠忑)'
        elif cd in POS_CD:
            group = 'DXCD>0(上中下)'
        else:
            i += 1
            continue
        # 找到连续段（同符号组）
        j = i
        while j < n and (rows[j][8] in NEG_CD if group.startswith('DXCD<0') else rows[j][8] in POS_CD):
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
        st = seg_stats[group]
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
        i = j

print('\n=== DXCD<0 vs DXCD>0 连续段内 DXZC 交叉次数 ===')
for group in ('DXCD<0(忐忠忑)', 'DXCD>0(上中下)'):
    st = seg_stats[group]
    total = st['segments']
    if total == 0:
        print(f'\n{group}: 无样本')
        continue
    print(f'\n{group}: {total} 个连续段, 共 {st["total_days"]} 天')
    print(f'  交叉0次: {st["cross_0"]} ({st["cross_0"]/total*100:.1f}%)')
    print(f'  交叉1次: {st["cross_1"]} ({st["cross_1"]/total*100:.1f}%)')
    print(f'  交叉2次: {st["cross_2"]} ({st["cross_2"]/total*100:.1f}%)')
    print(f'  交叉3+次: {st["cross_3plus"]} ({st["cross_3plus"]/total*100:.1f}%)')
    print(f'  有交叉(≥1次)占比: {(st["cross_1"]+st["cross_2"]+st["cross_3plus"])/total*100:.1f}%')