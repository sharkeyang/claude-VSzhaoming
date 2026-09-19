# -*- coding: utf-8 -*-
"""深入验证三连跌：段数口径 vs 柱数口径
1. 三连跌段中 DXZC>0 的占比
2. DXZC>0 时三连跌段数频率
"""
import csv, io, os

COL_ZA = 13
COL_ZC = 14
COL_ZHANGFU = 5

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计
n_zc0 = 0
n_zc0_3lian = 0
# 三连跌段（全部）
sanlian_seg_all = 0
# 三连跌段中，段内至少1柱 DXZC>0 的段数
sanlian_seg_has_zc0 = 0
# 三连跌段中，段内所有柱 DXZC>0 的段数
sanlian_seg_all_zc0 = 0
# 三连跌段中，段内柱数
sanlian_seg_zc0_zhushu = 0
sanlian_seg_total_zhushu = 0

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
            i = 0
            while i < len(rows):
                if rows[i][2] < 0:
                    j = i
                    while j < len(rows) and rows[j][2] < 0:
                        j += 1
                    length = j - i
                    if length >= 3:
                        sanlian_seg_all += 1
                        sanlian_seg_total_zhushu += length
                        # 段内 DXZC>0 柱数
                        zc0_in_seg = sum(1 for k in range(i, j) if rows[k][1] > 0)
                        sanlian_seg_zc0_zhushu += zc0_in_seg
                        if zc0_in_seg > 0:
                            sanlian_seg_has_zc0 += 1
                        if zc0_in_seg == length:
                            sanlian_seg_all_zc0 += 1
                        # 段内每柱若 DXZC>0 计入
                        for k in range(i, j):
                            if rows[k][1] > 0:
                                n_zc0_3lian += 1
                    i = j
                else:
                    i += 1
            for za, zc, zf in rows:
                if zc > 0:
                    n_zc0 += 1
    except Exception:
        pass
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print(f'\n=== 三连跌段分析 ===')
print(f'三连跌及以上段数(全部): {sanlian_seg_all}')
print(f'三连跌段中至少1柱DXZC>0: {sanlian_seg_has_zc0} ({sanlian_seg_has_zc0/sanlian_seg_all*100:.1f}%)')
print(f'三连跌段中所有柱DXZC>0: {sanlian_seg_all_zc0} ({sanlian_seg_all_zc0/sanlian_seg_all*100:.1f}%)')
print(f'三连跌段总柱数: {sanlian_seg_total_zhushu}')
print(f'三连跌段中DXZC>0柱数: {sanlian_seg_zc0_zhushu} ({sanlian_seg_zc0_zhushu/sanlian_seg_total_zhushu*100:.1f}%)')

print(f'\n=== DXZC>0 三连跌及以上概率 ===')
print(f'DXZC>0 总柱数: {n_zc0}')
print(f'DXZC>0 且处于三连跌及以上: {n_zc0_3lian}')
print(f'DXZC>0 三连跌及以上占比(柱数口径): {n_zc0_3lian/n_zc0*100:.2f}%')