# -*- coding: utf-8 -*-
"""Q1: 等3中层主/BT鼎精确值 + Q3: 等2拆分DTZA=2~3 vs ≥4赛马（核心池全量）"""
import csv, os, io
from collections import Counter

# 市板映射
CODE2BOARD = {}
with open('____temp/市板映射.csv', 'r', encoding='utf-8-sig') as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if len(row) >= 2:
            CODE2BOARD[row[0].strip()] = row[1].strip()
CORE = {'Qic', 'Qim', 'Qit'}  # 高波池（已剔除Qin非成分股）

out = io.open('____temp/_q1_q3_result.txt', 'w', encoding='utf-8')

def outln(s=''):
    out.write(s + '\n')

# 统计器
# Q1: 等3 层主 vs BT鼎
q1 = {}  # key -> [count, hits1, hits2, hits3]
# Q3: 等2 拆分
q3 = {}  # key -> [count, hits2, hits3]

def add(d, key, hit1, hit2, hit3):
    if key not in d:
        d[key] = [0, 0, 0, 0]
    d[key][0] += 1
    d[key][1] += hit1
    d[key][2] += hit2
    d[key][3] += hit3

files_core = 0
for fname in os.listdir('昭明算展/谕组日'):
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if CODE2BOARD.get(code, '') not in CORE:
        continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 45: continue
                try:
                    nxt_gf = float(row[26])  # 次日高幅
                    dtza = float(row[13])     # 日ZA
                    zc = float(row[14])       # 日ZC
                    btding = float(row[40])   # BT鼎
                    btly = float(row[42])     # BT连阳
                    bsha = float(row[19])     # BSHA
                except:
                    continue
                cls = row[44].strip()   # 日等型
                cd = row[8].strip()     # DXCD
                cx = row[33].strip()    # 中符串
                cengjie = row[28].strip()  # 层界

                hit1 = 1 if nxt_gf >= 1 else 0
                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                # Q1: 等3 层主 vs BT鼎
                if cls == '等3':
                    if cengjie.startswith('主'):
                        add(q1, '等3_层主', hit1, hit2, hit3)
                    if btding > 0:
                        add(q1, '等3_BT鼎', hit1, hit2, hit3)

                # Q3: 等2 拆分 DTZA 2~3 vs ≥4
                if cls == '等2':
                    base = '等2_TZA2_3' if 2 <= dtza <= 3 else '等2_TZA4P' if dtza >= 4 else None
                    if base:
                        add(q3, base, hit1, hit2, hit3)
                        # 叠加条件
                        if bsha > 5: add(q3, base + '_偏5', hit1, hit2, hit3)
                        if btly > 0: add(q3, base + '_连', hit1, hit2, hit3)
                        if zc > 0 and cd == '上': add(q3, base + '_门', hit1, hit2, hit3)
                        if bsha > 5 and btly > 0: add(q3, base + '_偏5连', hit1, hit2, hit3)
                        if bsha > 5 and zc > 0 and cd == '上': add(q3, base + '_偏5门', hit1, hit2, hit3)
                        if bsha > 5 and btly > 0 and zc > 0 and cd == '上': add(q3, base + '_偏5连门', hit1, hit2, hit3)
    except Exception:
        pass

def pct(h, n):
    return h / n * 100 if n else 0

outln(f'核心池文件: {files_core}')
outln('')
outln('=== Q1: 等3 层主 vs BT鼎 精确值 ===')
outln(f'{"条件":<12s} {"样本":>10s} {"下日≥1%":>10s} {"下日≥2%":>10s} {"下日≥3%":>10s}')
outln('-' * 55)
for k in ['等3_层主', '等3_BT鼎']:
    if k in q1:
        n, h1, h2, h3 = q1[k]
        outln(f'{k:<12s} {n:>10,} {pct(h1,n):>9.1f}% {pct(h2,n):>9.1f}% {pct(h3,n):>9.1f}%')
outln('')

outln('=== Q3: 等2 拆分 DTZA=2~3 vs ≥4 赛马（H2排序） ===')
outln(f'{"策略":<26s} {"样本":>10s} {"≥2%":>10s} {"≥3%":>10s}')
outln('-' * 60)
# 只输出有样本且样本≥1000的行，按≥2%排序
rows = []
for k, v in q3.items():
    n, h1, h2, h3 = v
    if n >= 1000:
        rows.append((pct(h2, n), k, n, h1, h2, h3))
rows.sort(key=lambda x: -x[0])
for p2, k, n, h1, h2, h3 in rows:
    outln(f'{k:<26s} {n:>10,} {p2:>9.1f}% {pct(h3,n):>9.1f}%')

out.close()
print('Done')