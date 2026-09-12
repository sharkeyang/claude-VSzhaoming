# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证DJA之下升排/上破DJA是否诱多
# 1. DJA之下升排: 后续是否真正上破DJA(日ZA>0)并站稳, 还是诱多(又跌回)
# 2. 上破DJA(日ZA=1/2)后: 是否站稳(5日仍升管)还是诱多(又跌破)
r = defaultdict(lambda:[0,0,0])  # (信号) -> [样本, 上破DJA, 站稳(5日仍升管)]

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
        if hx0 not in ('a','b','r','c','y','z'): continue
        # DJA之下升排
        if za < 0 and zhu.startswith('升'):
            # 后续是否上破DJA
            up = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    up = 1
                    break
            r['DJA之下升排'][0] += 1
            if up: r['DJA之下升排'][1] += 1
        # 上破DJA(日ZA=1/2)后是否站稳
        if za in (1,2):
            still = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    still = 1
                    break
            r['上破DJA(ZA=1/2)'][0] += 1
            if still: r['上破DJA(ZA=1/2)'][1] += 1
    n += 1

print('总文件:', n)
print('\n=== DJA之下升排/上破DJA 是否诱多 ===')
print(f"{'信号':<24}{'样本':>9}{'上破/站稳':>10}{'P':>8}")
for k,(tot,up,still) in r.items():
    print(f"{k:<24}{tot:>9}{up:>10}{up/tot*100:>7.2f}%")
