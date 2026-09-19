# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')

# 验证甲护型结束后第一次下破DJA是否再次站上
# 找甲机会段, 记录其结束位置; 结束后第一次日ZA<0, 看后续是否再次站上DJA
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
    # 找所有甲机会段
    i = 0
    while i < N:
        if rows[i][9][0] == 'a':
            # 甲机会段起点
            j = i
            while j < N and rows[j][9][0] == 'a':
                j += 1
            # 甲机会段结束于j-1, 从j开始找第一次日ZA<0
            k = j
            while k < N:
                if int(rows[k][13]) < 0:
                    # 找到第一次下破DJA
                    # 次日冲高
                    nxt_hr = 0
                    if k+1 < N:
                        try: nxt_hr = float(rows[k+1][26])
                        except: nxt_hr = 0
                    p3 = 1 if nxt_hr >= 3 else 0
                    # 3日重新站上DJA
                    rest = 0
                    for m in range(k+1, min(k+4, N)):
                        if int(rows[m][13]) > 0:
                            rest = 1
                            break
                    r['甲结束后第一次下破DJA'][0] += 1
                    if p3: r['甲结束后第一次下破DJA'][1] += 1
                    if rest: r['甲结束后第一次下破DJA'][2] += 1
                    break
                k += 1
            i = j
        else:
            i += 1
    n += 1

print('总文件:', n)
print('\n=== 甲护型结束后第一次下破DJA ===')
for k,(tot,p3,rest) in r.items():
    print(f'{k}: n={tot}, 次日冲高P>=3%={p3/tot*100:.1f}%, 3日重新站上DJA={rest/tot*100:.1f}%')
