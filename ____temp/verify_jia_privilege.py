# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')

# 验证甲的特权:
# 1. 甲机会段第一个阴柱: 看后续是否反弹(次日阳柱/3日重新站上DJA)
# 2. 甲护型结束后第一次下破DJA: 甲机会段结束后, 第一次日ZA<0, 看后续是否再次站上DJA

r = defaultdict(lambda: [0,0,0])

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    N = len(rows)
    for i in range(N):
        row = rows[i]
        hx0 = row[9][0]
        if hx0 != 'a': continue  # 只处理甲
        # 机会段起点(连续甲)
        j = i
        while j > 0:
            if rows[j-1][9][0] == 'a':
                j -= 1
            else:
                break
        # 1. 第一个阴柱
        is_first_yin = False
        if float(row[5]) < 0:
            is_first_yin = True
            for k in range(j, i):
                if float(rows[k][5]) < 0:
                    is_first_yin = False
                    break
        # 次日冲高
        nxt_hr = 0
        if i+1 < N:
            try: nxt_hr = float(rows[i+1][26])
            except: nxt_hr = 0
        p3 = 1 if nxt_hr >= 3 else 0
        # 3日重新站上DJA
        rest = 0
        for k in range(i+1, min(i+4, N)):
            if int(rows[k][13]) > 0:
                rest = 1
                break
        if is_first_yin:
            r['甲机会段第一个阴柱'][0] += 1
            if p3: r['甲机会段第一个阴柱'][1] += 1
            if rest: r['甲机会段第一个阴柱'][2] += 1
    n += 1

print('总文件:', n)
print('\n=== 甲的特权验证 ===')
for k,(tot,p3,rest) in r.items():
    print(f'{k}: n={tot}, 次日冲高P>=3%={p3/tot*100:.1f}%, 3日重新站上DJA={rest/tot*100:.1f}%')
