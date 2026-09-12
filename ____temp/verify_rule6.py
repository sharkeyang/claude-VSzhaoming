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

# 用风险指标验证: 后续3日内下破DJA概率
# 基线 vs 用户原规则 vs 修正规则
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
        dxcd = row[8]
        dxzc = int(row[14])
        hx0 = row[9][0]
        za = int(row[13])
        zhu = row[10]
        if dxcd in ('上','忐') and dxzc > 0 and hx0 in ('a','b','r'):
            # 3日内下破DJA
            brk = 0
            for j in range(i+1, min(i+4, len(rows))):
                if int(rows[j][13]) < 0:
                    brk = 1
                    break
            r['基线(甲乙己)'][0] += 1
            if brk: r['基线(甲乙己)'][1] += 1
            zc = zhu_class(zhu)
            ok_user = False
            if za == 1: ok_user = (zc == '升连')
            elif za == 2: ok_user = (zc in ('升连','跌孕'))
            elif za >= 3: ok_user = (zc != '阴阳阴')
            if ok_user:
                r['用户原规则'][0] += 1
                if brk: r['用户原规则'][1] += 1
            ok_fix = False
            if za == 1: ok_fix = True
            elif za == 2: ok_fix = (zc in ('升连','跌孕'))
            elif za >= 3: ok_fix = (zc != '阴阳阴')
            if ok_fix:
                r['修正规则(DTZA=1不过滤)'][0] += 1
                if brk: r['修正规则(DTZA=1不过滤)'][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 风险管理验证: 3日内下破DJA概率 ===')
print(f"{'规则':<26}{'样本':>9}{'3日下破':>9}{'P下破':>8}")
for k,(tot,brk) in r.items():
    print(f"{k:<26}{tot:>9}{brk:>9}{brk/tot*100:>7.2f}%")
