# -*- coding: utf-8 -*-
"""分析龙头/龙震系列波型的冲高回落（诱多）"""
import sys, csv, glob
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

TARGETS = ['Dd龙头芽', 'De龙头根', 'Fd龙震芽', 'Fe龙震根']

def parse_float(s):
    try: return float(s)
    except: return None

# 每个波型：下周P3、下周PR<0、冲高回落(HR>=3且PR<0)、下周ZA<0
stats = {t: {'n':0, 'next_p3':[0,0], 'next_pr_neg':[0,0], 'chonggao_huiluo':[0,0],
             'next_za_neg':[0,0], 'next_hr_sum':0, 'next_hr_n':0} for t in TARGETS}
base = {'n':0, 'next_p3':[0,0], 'next_pr_neg':[0,0], 'chonggao_huiluo':[0,0],
        'next_za_neg':[0,0], 'next_hr_sum':0, 'next_hr_n':0}

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
        next_hr = parse_float(nxt[3])
        next_pr = parse_float(nxt[2])
        try: next_za = int(nxt[13])
        except: next_za = None
        # 基线
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
            if next_pr is not None and next_pr < 0:
                base['next_pr_neg'][0] += 1
                if next_hr >= 3: base['chonggao_huiluo'][0] += 1
            base['next_pr_neg'][1] += 1
            if next_hr >= 3: base['chonggao_huiluo'][1] += 1
        if next_za is not None:
            base['next_za_neg'][1] += 1
            if next_za < 0: base['next_za_neg'][0] += 1
        # 目标
        if name in TARGETS:
            s = stats[name]
            s['n'] += 1
            if next_hr is not None:
                s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
                if next_hr >= 3: s['next_p3'][0] += 1
                s['next_p3'][1] += 1
                if next_pr is not None and next_pr < 0:
                    s['next_pr_neg'][0] += 1
                    if next_hr >= 3: s['chonggao_huiluo'][0] += 1
                s['next_pr_neg'][1] += 1
                if next_hr >= 3: s['chonggao_huiluo'][1] += 1
            if next_za is not None:
                s['next_za_neg'][1] += 1
                if next_za < 0: s['next_za_neg'][0] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下周P3: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%')
print(f'  下周PR<0: {base["next_pr_neg"][0]/base["next_pr_neg"][1]*100:.2f}%')
print(f'  冲高回落(HR>=3且PR<0): {base["chonggao_huiluo"][0]/base["chonggao_huiluo"][1]*100:.2f}%')
print(f'  下周ZA<0: {base["next_za_neg"][0]/base["next_za_neg"][1]*100:.2f}%')

for name in TARGETS:
    s = stats[name]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100
    pr_neg = s['next_pr_neg'][0]/s['next_pr_neg'][1]*100
    chg = s['chonggao_huiluo'][0]/s['chonggao_huiluo'][1]*100
    za_neg = s['next_za_neg'][0]/s['next_za_neg'][1]*100
    avg_hr = s['next_hr_sum']/s['next_hr_n']
    print(f'\n=== {name} (n={s["n"]}) ===')
    print(f'  下周P3: {p3:.2f}%')
    print(f'  下周均HR: {avg_hr:.2f}%')
    print(f'  下周PR<0: {pr_neg:.2f}%')
    print(f'  冲高回落(HR>=3且PR<0): {chg:.2f}%')
    print(f'  下周ZA<0: {za_neg:.2f}%')
