# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证"立刻开始下一个DJA丘": 升管中(日ZA>0)出现跌排/跌吞后
# 1. 是否下破DJA(日ZA<0) 2. 下破后是否在N日内重新站上DJA(日ZA>0)形成新丘
# 3. 下破后重新站上的时间(1/2/3/4/5日)
r = defaultdict(lambda:[0,0,0,0,0,0])  # (护型,柱排)->[样本,下破,重站,1日,2日,3日]

def zhu_dir_class(zhu):
    if zhu.startswith('升'): return '升排'
    if zhu.startswith('跌'):
        return '跌吞' if '吞' in zhu else '跌排'
    return '其他'

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
        cur_hx = row[9][0]
        zhu = row[10]
        if cur_za > 0 and cur_hx in ('a','b','r'):
            zc = zhu_dir_class(zhu)
            if zc not in ('升排','跌排','跌吞'): continue
            # 找下破点(日ZA<0)
            brk = -1
            for j in range(i+1, min(i+10, len(rows))):
                if int(rows[j][13]) < 0:
                    brk = j
                    break
            r[(cur_hx,zc)][0] += 1
            if brk != -1:
                r[(cur_hx,zc)][1] += 1
                # 下破后是否重新站上(日ZA>0)
                rest = -1
                for j in range(brk+1, min(brk+6, len(rows))):
                    if int(rows[j][13]) > 0:
                        rest = j
                        break
                if rest != -1:
                    r[(cur_hx,zc)][2] += 1
                    days = rest - brk
                    if days <= 1: r[(cur_hx,zc)][3] += 1
                    elif days <= 2: r[(cur_hx,zc)][4] += 1
                    else: r[(cur_hx,zc)][5] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己'}
print('总文件:', n)
print('\n=== 升管中跌排/跌吞后: 下破DJA→重新站上(新DJA丘) ===')
print(f"{'护型':<4}{'柱排':<6}{'样本':>8}{'下破':>7}{'P下破':>7}{'重站':>7}{'P重站':>8}{'1日':>6}{'2日':>6}{'3日+':>7}")
for hx in ['a','b','r']:
    for zc in ['升排','跌排','跌吞']:
        tot, brk, rest, d1, d2, d3 = r[(hx,zc)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{zc:<6}{tot:>8}{brk:>7}{brk/tot*100:>6.1f}%{rest:>7}{rest/brk*100:>7.1f}%{d1:>6}{d2:>6}{d3:>7}")
