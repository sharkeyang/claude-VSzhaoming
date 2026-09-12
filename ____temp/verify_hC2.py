# -*- coding: utf-8 -*-
import csv, glob, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')
pat = re.compile(r'[上中下忐忠忑]([-\d]+)')

# 猜想C: 转换态(上破DJA 1-2柱, 日ZA=1或2), 用推断DXZB
# DXZB符号: JZ>JA(日ZA>0)且JA>JB(DXAB>0)->DXZB>0; JZ<JA且JA<JB->DXZB<0
# 验证: DXZA>0且DXZB>0 vs DXZA>0且DXZB<0, 后续进入升管(5日仍站上DJA)概率
rC = defaultdict(lambda:[0,0])  # (DXZB符号) -> [样本, 5日仍升管]

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
        cur_za = int(row[13])
        hx = row[9]
        m = pat.search(hx)
        if not m: continue
        dxab = int(m.group(1))
        # 转换态: 上破DJA 1-2柱 (日ZA=1或2)
        if cur_za in (1,2):
            # 推断DXZB符号
            if cur_za > 0 and dxab > 0:
                dxzb = 'DXZB>0'
            elif cur_za > 0 and dxab < 0:
                dxzb = 'DXZB<0'
            else:
                continue  # 跳过不确定
            # 5日内仍升管(日ZA>0)
            still = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    still = 1
                    break
            rC[dxzb][0] += 1
            if still: rC[dxzb][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 猜想C: 转换态(上破DJA 1-2柱) 用推断DXZB 5日内仍升管概率 ===')
print(f"{'DXZB':<10}{'样本':>9}{'5日仍升管':>10}{'P':>8}")
for grp in ['DXZB>0','DXZB<0']:
    tot, still = rC[grp]
    if tot == 0: continue
    print(f"{grp:<10}{tot:>9}{still:>10}{still/tot*100:>7.2f}%")
