# -*- coding: utf-8 -*-
"""验证修改后的日漏提示周级部分（第1层周类备选 + 第2层周柱排漏斗）
数据：谕组周 CSV，GBK编码（旧编码波型）
列：波型[5]、柱排周[6]、HR[3](下周=下一行)、周管BT鼎[46]
旧编码→新编码：Aa龙扩猪/Ac龙扩栅/Ab龙扩杂→扩，Ae龙扩根→排除，Fa龙震〇→震〇，Fd龙震芽→震芽，Dd龙头芽→头交，De龙头根→排除，Fe龙震根→排除，NF武→武
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def parse_float(s):
    try: return float(s)
    except: return None

def classify(name):
    if '龙扩根' in name: return '排除(龙扩根)'
    if '龙震根' in name: return '排除(龙震根)'
    if '龙头根' in name: return '排除(龙头返)'
    if '龙扩' in name: return '扩'
    if '龙震〇' in name: return '震〇'
    if '龙震芽' in name: return '震芽'
    if '龙头芽' in name: return '头交'
    if '武' in name: return '武'
    return '其他'

def zhuopai_funnel(zp, bt_ding):
    # 第2层周柱排漏斗：连阳/鼎/跌孕
    if not zp: return '无'
    # 连阳：柱排含"连"或末位升连
    if '连' in zp: return '连阳'
    if bt_ding == '1': return '鼎'
    if '孕' in zp: return '跌孕'
    return '无'

stats = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0})
funnel_stats = defaultdict(lambda: defaultdict(lambda: {'n':0,'next_p3':[0,0]}))
base = {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}

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
        zp = row[6]
        bt_ding = row[46]
        funnel = zhuopai_funnel(zp, bt_ding)
        next_hr = parse_float(nxt[3])
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
        # 按周类备选
        s = stats[cat]
        s['n'] += 1
        if next_hr is not None:
            s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
            if next_hr >= 3: s['next_p3'][0] += 1
            s['next_p3'][1] += 1
        # 按周类备选 × 周柱排漏斗
        if cat in ['扩','震〇','震芽','头交','武']:
            fs = funnel_stats[cat][funnel]
            fs['n'] += 1
            if next_hr is not None:
                if next_hr >= 3: fs['next_p3'][0] += 1
                fs['next_p3'][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下周冲高率: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  下周均HR: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')

print(f'\n=== 修改后第1层：周类备选 ===')
for cat in ['扩','震〇','震芽','头交','武','排除(龙扩根)','排除(龙震根)','排除(龙头返)']:
    s = stats[cat]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    print(f'  [{cat}] n={s["n"]}: 下周冲高率={p3:.2f}% 下周均HR={avg_hr:.2f}%')

print(f'\n=== 修改后第2层：周类备选 × 周柱排漏斗 ===')
for cat in ['扩','震〇','震芽','头交','武']:
    for funnel in ['连阳','鼎','跌孕','无']:
        fs = funnel_stats[cat][funnel]
        if fs['n'] == 0: continue
        p3 = fs['next_p3'][0]/fs['next_p3'][1]*100 if fs['next_p3'][1] else 0
        print(f'  [{cat}|{funnel}] n={fs["n"]}: 下周冲高率={p3:.2f}%')