# -*- coding: utf-8 -*-
"""验证 DXZC>0 三连跌及以上的概率
三连跌 = 连续3天及以上收盘下跌(涨幅<0)
"""
import csv, io, os
from collections import Counter

COL_ZC = 14     # 日ZC
COL_ZHANGFU = 5 # 涨幅

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计 DXZC>0 时，连续下跌天数分布
# 连续下跌段：涨幅<0 的连续天数
# 统计：DXZC>0 的柱中，处于"三连跌及以上"的比例
n_zc0 = 0           # DXZC>0 总柱数
n_zc0_3lian = 0     # DXZC>0 且处于三连跌及以上的柱数
# 连续下跌段长度分布
lian_die_len = Counter()  # 连续下跌段长度 -> 段数

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
                    zc = float(row[COL_ZC])
                    zf = float(row[COL_ZHANGFU])
                except (ValueError, IndexError):
                    continue
                rows.append((zc, zf))
            # 统计连续下跌段
            i = 0
            while i < len(rows):
                if rows[i][1] < 0:  # 下跌
                    j = i
                    while j < len(rows) and rows[j][1] < 0:
                        j += 1
                    length = j - i
                    lian_die_len[length] += 1
                    i = j
                else:
                    i += 1
            # 统计 DXZC>0 且处于三连跌及以上的柱数
            # 遍历，找连续下跌段，标记段内每柱是否 DXZC>0
            i = 0
            while i < len(rows):
                if rows[i][1] < 0:
                    j = i
                    while j < len(rows) and rows[j][1] < 0:
                        j += 1
                    length = j - i
                    if length >= 3:
                        # 段内每柱，若 DXZC>0 则计入
                        for k in range(i, j):
                            if rows[k][0] > 0:
                                n_zc0_3lian += 1
                    i = j
                else:
                    i += 1
            # 统计 DXZC>0 总柱数
            for zc, zf in rows:
                if zc > 0:
                    n_zc0 += 1
    except Exception:
        pass
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print(f'\n=== DXZC>0 三连跌及以上概率 ===')
print(f'DXZC>0 总柱数: {n_zc0}')
print(f'DXZC>0 且处于三连跌及以上: {n_zc0_3lian}')
print(f'DXZC>0 三连跌及以上占比: {n_zc0_3lian/n_zc0*100:.2f}%')

print(f'\n=== 连续下跌段长度分布(全部) ===')
total_seg = sum(lian_die_len.values())
for length in sorted(lian_die_len.keys()):
    print(f'  {length}连跌: {lian_die_len[length]} 段 ({lian_die_len[length]/total_seg*100:.1f}%)')