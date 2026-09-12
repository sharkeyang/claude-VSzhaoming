# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

def zhu_class(zhu):
    if zhu.startswith('升') and '连' in zhu: return '升连'
    if zhu.startswith('跌') and '孕' in zhu: return '跌孕'
    if zhu.startswith('(人)'): return '阴阳阴'
    if zhu.startswith('(升)人') or zhu.startswith('(跌)人'): return '人排'
    return '其他'

# 基线内, 按DTZA档位+柱排细分
r = defaultdict(lambda:[0,0])

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
        nxt = rows[i+1]
        dxcd = row[8]
        dxzc = int(row[14])
        hx0 = row[9][0]
        za = int(row[13])
        zhu = row[10]
        try:
            nxt_hr = float(nxt[26])
        except:
            continue
        p3 = 1 if nxt_hr >= 3 else 0
        if dxcd in ('上','忐') and dxzc > 0 and hx0 in ('a','b','r'):
            zc = zhu_class(zhu)
            # 按DTZA档位+柱排
            if za == 1:
                grp = f'DTZA=1:{zc}'
            elif za == 2:
                grp = f'DTZA=2:{zc}'
            elif za >= 3:
                grp = f'DTZA>=3:{zc}'
            else:
                continue
            r[grp][0] += 1
            if p3: r[grp][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 基线内按DTZA档位+柱排细分 P>=3% ===')
print(f"{'分组':<22}{'样本':>9}{'P>=3%':>8}{'P':>8}")
for k,(tot,hit) in sorted(r.items()):
    if tot < 1000: continue
    print(f"{k:<22}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%")
