# -*- coding: utf-8 -*-
"""分析龙头/龙震系列波型的 ZA 分布和下周表现"""
import sys, csv, glob
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

TARGETS = ['Dd龙头芽', 'De龙头根', 'Fd龙震芽', 'Fe龙震根']

def parse_float(s):
    try: return float(s)
    except: return None

# 每个波型：ZA分布 + 下周P3(按ZA分组) + 下周ZA<0(按ZA分组)
stats = {t: {'za_dist': Counter(), 'next_p3': defaultdict(lambda: [0,0]), 
             'next_neg': defaultdict(lambda: [0,0]), 'next_hr': defaultdict(lambda: [0,0])} for t in TARGETS}

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)-1):
        row, nxt = rows[i], rows[i+1]
        b = row[5]
        if not b: continue
        name = b.split('.')[0]
        if name not in TARGETS: continue
        try: za = int(row[13])
        except: continue
        next_hr = parse_float(nxt[3])
        try: next_za = int(nxt[13])
        except: next_za = None
        # ZA分组
        if za < 0: grp = 'ZA<0'
        elif za <= 3: grp = 'ZA1-3'
        else: grp = 'ZA>3'
        s = stats[name]
        s['za_dist'][grp] += 1
        if next_hr is not None:
            s['next_p3'][grp][0] += 1
            s['next_hr'][grp][0] += 1
            s['next_hr'][grp][1] += next_hr
            if next_hr >= 3: s['next_p3'][grp][1] += 1
        if next_za is not None:
            s['next_neg'][grp][0] += 1
            if next_za < 0: s['next_neg'][grp][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

for name in TARGETS:
    s = stats[name]
    total = sum(s['za_dist'].values())
    print(f'\n=== {name} (n={total}) ===')
    print(f'  ZA分布: ' + '  '.join(f'{k}={v}({v/total*100:.1f}%)' for k,v in s['za_dist'].most_common()))
    for grp in ['ZA<0', 'ZA1-3', 'ZA>3']:
        n = s['za_dist'][grp]
        if n == 0: continue
        p3 = s['next_p3'][grp][1]/s['next_p3'][grp][0]*100 if s['next_p3'][grp][0] else 0
        avg_hr = s['next_hr'][grp][1]/s['next_hr'][grp][0] if s['next_hr'][grp][0] else 0
        neg = s['next_neg'][grp][1]/s['next_neg'][grp][0]*100 if s['next_neg'][grp][0] else 0
        print(f'  [{grp}] n={n}: 下周P3={p3:.2f}% 下周均HR={avg_hr:.2f}% 下周ZA<0={neg:.2f}%')
