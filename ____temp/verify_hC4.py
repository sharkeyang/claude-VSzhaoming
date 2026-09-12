# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 完整猜想C: 转换态(上破DJA 1-2柱, 日ZA=1或2)
# 验证: DXZA>0且DXZB>0 vs DXZA>0且DXZB<0, 后续进入升管(5日仍站上DJA)概率
# 护级→DXZB: 上/中/忐->DXZB>0, 下/忠/忑->DXZB<0
rC = defaultdict(lambda:[0,0])  # (条件) -> [样本, 5日仍升管]

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
        if len(hx) < 4: continue
        huji = hx[3]
        # 转换态: 上破DJA 1-2柱
        if cur_za in (1,2):
            dxzb_pos = huji in ('上','中','忐')
            # 5日内仍升管
            still = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    still = 1
                    break
            if dxzb_pos:
                grp = 'DXZA>0且DXZB>0'
            else:
                grp = 'DXZA>0且DXZB<0'
            rC[grp][0] += 1
            if still: rC[grp][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 完整猜想C: 转换态(上破DJA 1-2柱) 5日内仍升管概率 ===')
print(f"{'条件':<20}{'样本':>9}{'5日仍升管':>10}{'P':>8}")
for grp in ['DXZA>0且DXZB>0','DXZA>0且DXZB<0']:
    tot, still = rC[grp]
    if tot == 0: continue
    print(f"{grp:<20}{tot:>9}{still:>10}{still/tot*100:>7.2f}%")
