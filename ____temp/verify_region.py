# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证操作区域定型: DXCD=上忐 + DXZC>0, 各护型获利性
# 指标: P>=3%, 3日下破DJA, 5日收益
r = defaultdict(lambda:[0,0,0,0.0])  # (护型) -> [样本, P>=3%, 3日下破, 5日收益和]

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
        dxcd = row[8]; dxzc = int(row[14]); hx0 = row[9][0]; za = int(row[13])
        if dxcd not in ('上','忐') or dxzc <= 0: continue
        try:
            nxt_hr = float(rows[i+1][26])
        except:
            continue
        # 护型分类
        if hx0 == 'a': hx = '甲'
        elif hx0 == 'b': hx = '乙ZA>0' if za > 0 else '乙ZA<0'
        elif hx0 == 'r': hx = '己'
        elif hx0 == 'c': hx = '丙'
        elif hx0 == 'y': hx = '戊ZA>0' if za > 0 else '戊ZA<0'
        elif hx0 == 'z': hx = '丁'
        else: continue
        p3 = 1 if nxt_hr >= 3 else 0
        brk = 0
        for j in range(i+1, min(i+4, len(rows))):
            if int(rows[j][13]) < 0:
                brk = 1
                break
        ret5 = 0.0
        try:
            entry = float(row[1])
            exit5 = float(rows[min(i+5, len(rows)-1)][1])
            ret5 = (exit5 - entry) / entry * 100
        except:
            pass
        r[hx][0] += 1
        if p3: r[hx][1] += 1
        if brk: r[hx][2] += 1
        r[hx][3] += ret5
    n += 1

print('总文件:', n)
print('\n=== 操作区域(DXCD=上忐+DXZC>0) 各护型获利性 ===')
print(f"{'护型':<10}{'样本':>9}{'P>=3%':>8}{'P':>8}{'3日下破':>9}{'P下破':>8}{'5日收益':>9}")
for hx in ['甲','乙ZA>0','乙ZA<0','己','丙','戊ZA>0','戊ZA<0','丁']:
    tot, p3, brk, sret = r[hx]
    if tot == 0: continue
    print(f"{hx:<10}{tot:>9}{p3:>8}{p3/tot*100:>7.2f}%{brk:>9}{brk/tot*100:>7.2f}%{sret/tot:>8.3f}%")
