# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证操作区域(DXCD=上忐+DXZC>0+甲乙己乙ZA<0) 阴柱vs阳柱接入获利性
# 阴柱=涨幅<0, 阳柱=涨幅>0
# 指标: P>=3%(次日高幅), 3日下破DJA, 5日收益
r = defaultdict(lambda:[0,0,0,0.0])  # (护型,阴阳) -> [样本, P>=3%, 3日下破, 5日收益和]

def is_op_region(row):
    dxcd = row[8]; dxzc = int(row[14]); hx0 = row[9][0]; za = int(row[13])
    if dxcd not in ('上','忐') or dxzc <= 0: return False
    # 甲乙己 + 乙ZA<0
    if hx0 in ('a','b','r'): return True
    if hx0 == 'b' and za < 0: return True
    return False

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
        if not is_op_region(row): continue
        try:
            amp = float(row[5])  # 涨幅
            nxt_hr = float(rows[i+1][26])
        except:
            continue
        hx0 = row[9][0]
        yin = '阴柱' if amp < 0 else '阳柱'
        # P>=3%
        p3 = 1 if nxt_hr >= 3 else 0
        # 3日下破
        brk = 0
        for j in range(i+1, min(i+4, len(rows))):
            if int(rows[j][13]) < 0:
                brk = 1
                break
        # 5日收益
        ret5 = 0.0
        try:
            entry = float(row[1])
            exit5 = float(rows[min(i+5, len(rows)-1)][1])
            ret5 = (exit5 - entry) / entry * 100
        except:
            pass
        r[(hx0, yin)][0] += 1
        if p3: r[(hx0, yin)][1] += 1
        if brk: r[(hx0, yin)][2] += 1
        r[(hx0, yin)][3] += ret5
    n += 1

HX = {'a':'甲','b':'乙','r':'己'}
print('总文件:', n)
print('\n=== 操作区域(DXCD=上忐+DXZC>0+甲乙己乙ZA<0) 阴柱vs阳柱接入 ===')
print(f"{'护型':<4}{'阴阳':<6}{'样本':>9}{'P>=3%':>8}{'P':>8}{'3日下破':>9}{'P下破':>8}{'5日收益':>9}")
for hx in ['a','b','r']:
    for yin in ['阴柱','阳柱']:
        tot, p3, brk, sret = r[(hx,yin)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{yin:<6}{tot:>9}{p3:>8}{p3/tot*100:>7.2f}%{brk:>9}{brk/tot*100:>7.2f}%{sret/tot:>8.3f}%")
