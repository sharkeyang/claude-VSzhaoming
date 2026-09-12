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

# 用户规则: 每个DTZA档位, 选中 vs 排除
# DTZA=1: 选中=升连, 排除=其他
# DTZA=2: 选中=升连/跌孕, 排除=其他
# DTZA=3: 选中=非阴阳阴, 排除=阴阳阴
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
            if za == 1:
                sel = (zc == '升连')
                grp = 'DTZA=1选中(升连)' if sel else 'DTZA=1排除'
            elif za == 2:
                sel = (zc in ('升连','跌孕'))
                grp = 'DTZA=2选中(升连/跌孕)' if sel else 'DTZA=2排除'
            elif za >= 3:
                sel = (zc != '阴阳阴')
                grp = 'DTZA>=3选中(非阴阳阴)' if sel else 'DTZA>=3排除(阴阳阴)'
            else:
                continue
            r[grp][0] += 1
            if p3: r[grp][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 用户规则: 每个DTZA档位 选中 vs 排除 P>=3% ===')
print(f"{'分组':<26}{'样本':>9}{'P>=3%':>8}{'P':>8}")
for k,(tot,hit) in sorted(r.items()):
    print(f"{k:<26}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%")
