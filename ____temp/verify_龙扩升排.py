# -*- coding: utf-8 -*-
"""研究：龙扩猪关注升排 vs 其他可选(龙震〇/芽/武/龙头交)属震荡应在阴柱后介入
数据：谕组周 CSV，GBK编码
列：波型[5]、柱排周[6]、周涨[1](本周阴阳)、HR[3](下周=下一行)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def parse_float(s):
    try: return float(s)
    except: return None

def classify(name):
    if '龙扩猪' in name: return '龙扩猪'
    if '龙扩根' in name: return '龙扩根'
    if '龙扩栅' in name: return '龙扩栅'
    if '龙扩杂' in name: return '龙扩杂'
    if '龙震〇' in name: return '龙震〇'
    if '龙震芽' in name: return '龙震芽'
    if '龙震根' in name: return '龙震根'
    if '龙头芽' in name: return '龙头交'
    if '龙头根' in name: return '龙头返'
    if '武' in name: return '武'
    if '雀' in name: return '雀'
    return '其他'

# 统计：按波型 × 柱排方向(升/跌/人) × 本周阴阳(阳/阴)
# 指标：下周冲高率
stats = defaultdict(lambda: defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}))

def zhuopai_dir(zp):
    if not zp: return '?'
    c = zp[0]
    if c == '升': return '升排'
    if c == '跌': return '跌排'
    return '人排'

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
        cat = classify(name)
        zp = zhuopai_dir(row[6])
        zhang = parse_float(row[1])  # 本周涨幅
        yinyang = '阳' if (zhang is not None and zhang >= 0) else ('阴' if zhang is not None else '?')
        next_hr = parse_float(nxt[3])
        # 按波型×柱排
        s = stats[cat][zp]
        s['n'] += 1
        if next_hr is not None:
            s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
            if next_hr >= 3: s['next_p3'][0] += 1
            s['next_p3'][1] += 1
        # 按波型×阴阳
        s2 = stats[cat][yinyang]
        s2['n'] += 1
        if next_hr is not None:
            s2['next_hr_n'] += 1; s2['next_hr_sum'] += next_hr
            if next_hr >= 3: s2['next_p3'][0] += 1
            s2['next_p3'][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

def show(cat, dims):
    print(f'\n=== {cat} ===')
    for d in dims:
        s = stats[cat][d]
        if s['n'] == 0: continue
        p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
        avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
        print(f'  [{d}] n={s["n"]}: 下周冲高率={p3:.2f}% 下周均HR={avg_hr:.2f}%')

print('=== 龙扩猪：按柱排方向 ===')
show('龙扩猪', ['升排','跌排','人排'])
print('\n=== 龙扩猪：按本周阴阳 ===')
show('龙扩猪', ['阳','阴'])

print('\n=== 龙扩栅/杂：按柱排方向 ===')
show('龙扩栅', ['升排','跌排','人排'])
show('龙扩杂', ['升排','跌排','人排'])

print('\n=== 龙震〇：按柱排方向 + 阴阳 ===')
show('龙震〇', ['升排','跌排','人排'])
show('龙震〇', ['阳','阴'])

print('\n=== 龙震芽：按柱排方向 + 阴阳 ===')
show('龙震芽', ['升排','跌排','人排'])
show('龙震芽', ['阳','阴'])

print('\n=== 武：按柱排方向 + 阴阳 ===')
show('武', ['升排','跌排','人排'])
show('武', ['阳','阴'])

print('\n=== 龙头交：按柱排方向 + 阴阳 ===')
show('龙头交', ['升排','跌排','人排'])
show('龙头交', ['阳','阴'])