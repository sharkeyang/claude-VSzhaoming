# -*- coding: utf-8 -*-
"""深入验证三连跌：
1. 三连跌后 DXZA 是否都会 <0
2. DXZC>0 时三连跌及以上的概率（重新确认）
"""
import csv, io, os
from collections import Counter

COL_ZA = 13     # 日ZA
COL_ZC = 14     # 日ZC
COL_ZHANGFU = 5 # 涨幅

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计
n_zc0 = 0           # DXZC>0 总柱数
n_zc0_3lian = 0     # DXZC>0 且处于三连跌及以上
# 三连跌段后 DXZA 状态
# 三连跌段：连续3天+下跌，段结束后下一柱的 DXZA
sanlian_after_za = Counter()  # 三连跌段结束后下一柱 DXZA 符号
sanlian_seg = 0     # 三连跌及以上段数
all_die_seg = 0     # 所有连续下跌段数

for fi, fname in enumerate(files):
    path = os.path.join('昭明算展/谕组日', fname)
    try:
        with io.open(path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader)
            rows = []
            for row in reader:
                if len(row) <= COL_ZHANGFU:
                    continue
                try:
                    za = float(row[COL_ZA])
                    zc = float(row[COL_ZC])
                    zf = float(row[COL_ZHANGFU])
                except (ValueError, IndexError):
                    continue
                rows.append((za, zc, zf))
            # 遍历找连续下跌段
            i = 0
            while i < len(rows):
                if rows[i][2] < 0:  # 下跌
                    j = i
                    while j < len(rows) and rows[j][2] < 0:
                        j += 1
                    length = j - i
                    all_die_seg += 1
                    if length >= 3:
                        sanlian_seg += 1
                        # 段结束后下一柱的 DXZA
                        if j < len(rows):
                            next_za = rows[j][0]
                            if next_za > 0:
                                sanlian_after_za['>0'] += 1
                            elif next_za < 0:
                                sanlian_after_za['<0'] += 1
                            else:
                                sanlian_after_za['=0'] += 1
                        # 段内每柱，若 DXZC>0 则计入
                        for k in range(i, j):
                            if rows[k][1] > 0:
                                n_zc0_3lian += 1
                    i = j
                else:
                    i += 1
            # DXZC>0 总柱数
            for za, zc, zf in rows:
                if zc > 0:
                    n_zc0 += 1
    except Exception:
        pass
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print(f'\n=== 三连跌后 DXZA 状态 ===')
print(f'三连跌及以上段数: {sanlian_seg}')
print(f'段结束后下一柱 DXZA>0: {sanlian_after_za.get(">0",0)} ({sanlian_after_za.get(">0",0)/sanlian_seg*100:.1f}%)')
print(f'段结束后下一柱 DXZA<0: {sanlian_after_za.get("<0",0)} ({sanlian_after_za.get("<0",0)/sanlian_seg*100:.1f}%)')
print(f'段结束后下一柱 DXZA=0: {sanlian_after_za.get("=0",0)} ({sanlian_after_za.get("=0",0)/sanlian_seg*100:.1f}%)')

print(f'\n=== 连续下跌段长度分布 ===')
print(f'所有连续下跌段数: {all_die_seg}')
print(f'三连跌及以上段数: {sanlian_seg} ({sanlian_seg/all_die_seg*100:.1f}%)')

print(f'\n=== DXZC>0 三连跌及以上概率 ===')
print(f'DXZC>0 总柱数: {n_zc0}')
print(f'DXZC>0 且处于三连跌及以上: {n_zc0_3lian}')
print(f'DXZC>0 三连跌及以上占比: {n_zc0_3lian/n_zc0*100:.2f}%')