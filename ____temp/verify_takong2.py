# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证DJA之上跌连统计准确性
# 用不同"创新高"定义交叉验证:
# 定义A: 收盘价>跌连当日收盘(宽松)
# 定义B: 收盘价>跌连前5日最高(严格,真正创新高)
# 定义C: 5日最高价>跌连当日收盘(盘中创新高)
r = defaultdict(lambda:[0,0,0,0,0,0])  # (信号) -> [样本, A5, A10, B5, B10, C5]

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
        if hx0 not in ('a','b','r') or za <= 0: continue
        if not (zhu.startswith('跌') and '连' in zhu): continue
        try:
            cur_close = float(row[1])
            # 前5日最高(不含当日)
            prev_hi = max(float(rows[k][3]) for k in range(max(0,i-5), i))
        except:
            continue
        # 定义A: 收盘>当前收盘
        a5=0; a10=0
        for j in range(i+1, min(i+6, len(rows))):
            try:
                if float(rows[j][1]) > cur_close: a5=1; break
            except: pass
        for j in range(i+1, min(i+11, len(rows))):
            try:
                if float(rows[j][1]) > cur_close: a10=1; break
            except: pass
        # 定义B: 收盘>前5日最高(真正创新高)
        b5=0; b10=0
        for j in range(i+1, min(i+6, len(rows))):
            try:
                if float(rows[j][1]) > prev_hi: b5=1; break
            except: pass
        for j in range(i+1, min(i+11, len(rows))):
            try:
                if float(rows[j][1]) > prev_hi: b10=1; break
            except: pass
        # 定义C: 5日最高价>当前收盘(盘中创新高)
        c5=0
        for j in range(i+1, min(i+6, len(rows))):
            try:
                if float(rows[j][3]) > cur_close: c5=1; break
            except: pass
        r['DJA之上跌连'][0] += 1
        if a5: r['DJA之上跌连'][1] += 1
        if a10: r['DJA之上跌连'][2] += 1
        if b5: r['DJA之上跌连'][3] += 1
        if b10: r['DJA之上跌连'][4] += 1
        if c5: r['DJA之上跌连'][5] += 1
    n += 1

print('总文件:', n)
for k,(tot,a5,a10,b5,b10,c5) in r.items():
    print(f'\n=== {k} (n={tot}) ===')
    print(f'定义A(收盘>跌连收盘): 5日创新高={a5/tot*100:.2f}%, 10日={a10/tot*100:.2f}%')
    print(f'定义B(收盘>前5日最高,真正新高): 5日={b5/tot*100:.2f}%, 10日={b10/tot*100:.2f}%')
    print(f'定义C(盘中最高>跌连收盘): 5日={c5/tot*100:.2f}%')
