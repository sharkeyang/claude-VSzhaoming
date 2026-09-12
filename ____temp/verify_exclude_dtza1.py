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

# 对比: 基线 / 用户原规则(DTZA=1升连) / 修正1(DTZA=1不过滤=保留) / 修正2(DTZA=1排除=不考虑入管)
r = defaultdict(lambda:[0,0,0])  # (规则) -> [样本, P>=3%, 3日下破]

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
        if dxcd in ('上','忐') and dxzc > 0 and hx0 in ('a','b','r'):
            try:
                nxt_hr = float(nxt[26])
            except:
                continue
            p3 = 1 if nxt_hr >= 3 else 0
            brk = 0
            for j in range(i+1, min(i+4, len(rows))):
                if int(rows[j][13]) < 0:
                    brk = 1
                    break
            # 基线
            r['基线'][0] += 1
            if p3: r['基线'][1] += 1
            if brk: r['基线'][2] += 1
            zc = zhu_class(zhu)
            # 用户原规则
            ok_user = False
            if za == 1: ok_user = (zc == '升连')
            elif za == 2: ok_user = (zc in ('升连','跌孕'))
            elif za >= 3: ok_user = (zc != '阴阳阴')
            if ok_user:
                r['用户原规则'][0] += 1
                if p3: r['用户原规则'][1] += 1
                if brk: r['用户原规则'][2] += 1
            # 修正1: DTZA=1不过滤(保留)
            ok_fix1 = False
            if za == 1: ok_fix1 = True
            elif za == 2: ok_fix1 = (zc in ('升连','跌孕'))
            elif za >= 3: ok_fix1 = (zc != '阴阳阴')
            if ok_fix1:
                r['修正1(DTZA=1保留)'][0] += 1
                if p3: r['修正1(DTZA=1保留)'][1] += 1
                if brk: r['修正1(DTZA=1保留)'][2] += 1
            # 修正2: DTZA=1排除(不考虑入管)
            ok_fix2 = False
            if za == 1: ok_fix2 = False
            elif za == 2: ok_fix2 = (zc in ('升连','跌孕'))
            elif za >= 3: ok_fix2 = (zc != '阴阳阴')
            if ok_fix2:
                r['修正2(DTZA=1排除)'][0] += 1
                if p3: r['修正2(DTZA=1排除)'][1] += 1
                if brk: r['修正2(DTZA=1排除)'][2] += 1
    n += 1

print('总文件:', n)
print('\n=== 对比: 基线 / 用户原规则 / 修正1(保留DTZA=1) / 修正2(排除DTZA=1) ===')
print(f"{'规则':<24}{'样本':>9}{'P>=3%':>8}{'P':>8}{'3日下破':>9}{'P下破':>8}")
for k,(tot,hit,brk) in r.items():
    print(f"{k:<24}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%{brk:>9}{brk/tot*100:>7.2f}%")
