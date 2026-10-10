# -*- coding: utf-8 -*-
"""验证龙扩四类(猪/根/栅/杂)的下周冲高率 + 诱多率，以及龙震〇/龙震芽/武的标注
数据：谕组周 CSV，GBK编码
列：波型[5]、HR[3](下周=下一行)、ZA周[13](下周ZA=下一行)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def parse_float(s):
    try: return float(s)
    except: return None

def classify(name):
    # 龙扩四类
    if '龙扩猪' in name: return '龙扩猪'
    if '龙扩根' in name: return '龙扩根'
    if '龙扩栅' in name: return '龙扩栅'
    if '龙扩杂' in name: return '龙扩杂'
    # 龙震/龙头
    if '龙震〇' in name: return '龙震〇'
    if '龙震芽' in name: return '龙震芽'
    if '龙震根' in name: return '龙震根'
    if '龙头芽' in name: return '龙头交(旧龙头芽)'
    if '龙头根' in name: return '龙头返(旧龙头根)'
    # 武/雀
    if '武' in name: return '武'
    if '雀' in name: return '雀'
    return '其他'

stats = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0,'za_1_3':0,'za_1_3_next_neg':0,'next_za_neg':0,'next_za_n':0})
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
        next_hr = parse_float(nxt[3])
        try: za = int(row[13])
        except: za = None
        try: next_za = int(nxt[13])
        except: next_za = None
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
        s = stats[cat]
        s['n'] += 1
        if next_hr is not None:
            s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
            if next_hr >= 3: s['next_p3'][0] += 1
            s['next_p3'][1] += 1
        if za is not None and 0 < za <= 3:
            s['za_1_3'] += 1
            if next_za is not None and next_za < 0:
                s['za_1_3_next_neg'] += 1
        if next_za is not None:
            s['next_za_n'] += 1
            if next_za < 0: s['next_za_neg'] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下周冲高率: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  下周均HR: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')

print(f'\n=== 龙扩四类 + 龙震〇/龙震芽/武 ===')
order = ['龙扩猪','龙扩根','龙扩栅','龙扩杂','龙震〇','龙震芽','武','龙头交(旧龙头芽)','龙头返(旧龙头根)','龙震根']
for cat in order:
    s = stats[cat]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    za13 = s['za_1_3']/s['n']*100
    youduo = s['za_1_3_next_neg']/s['za_1_3']*100 if s['za_1_3'] else 0
    next_neg = s['next_za_neg']/s['next_za_n']*100 if s['next_za_n'] else 0
    print(f'  [{cat}] n={s["n"]}: 下周冲高率={p3:.2f}% 下周均HR={avg_hr:.2f}% | 0<ZA<=3占比={za13:.2f}% 诱多率={youduo:.2f}% 下周ZA<0={next_neg:.2f}%')