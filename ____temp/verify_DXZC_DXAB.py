# -*- coding: utf-8 -*-
"""验证：周级龙态内，DXZC + DXAB护型 对下日冲高的区分度
数据：谕组日 CSV，GBK编码
列：日周联动[7](首字符=周向)、DXZC[14]、DXAB护型[9](a甲/b乙/c丙/z丁/y戊/r己)、次日高幅[26](下一行高幅)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def parse_float(s):
    try: return float(s)
    except: return None

def huxing_ab(hx):
    # DXAB护型：a甲/b乙/c丙/z丁/y戊/r己
    if not hx: return '?'
    c = hx[0]
    if c in 'ab': return '甲乙'
    if c == 'r': return '己'
    if c == 'c': return '丙'
    if c in 'zy': return '丁戊'
    return '?'

# 统计：周向 × DXZC(>0/<0) × DXAB护型
# 指标：下日冲高率(次日高幅>=3%)
stats = defaultdict(lambda: defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}))
base = {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)-1):
        row, nxt = rows[i], rows[i+1]
        lian = row[7]
        if not lian: continue
        zhou = lian[0]  # 周向
        dxzc = parse_float(row[14])
        hx = huxing_ab(row[9])
        next_hr = parse_float(nxt[6])
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
        if zhou not in '龙武雀虎': continue
        if dxzc is None: continue
        zc_key = 'ZC>0' if dxzc > 0 else 'ZC<=0'
        key = f'{zhou}|{zc_key}|{hx}'
        s = stats[zhou][f'{zc_key}|{hx}']
        s['n'] += 1
        if next_hr is not None:
            s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
            if next_hr >= 3: s['next_p3'][0] += 1
            s['next_p3'][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下日冲高率: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  下日均高幅: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')

print(f'\n=== 周级龙态内：DXZC × DXAB护型 ===')
for zc in ['ZC>0','ZC<=0']:
    for hx in ['甲乙','己','丙','丁戊']:
        s = stats['龙'][f'{zc}|{hx}']
        if s['n'] == 0: continue
        p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
        avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
        print(f'  [龙|{zc}|{hx}] n={s["n"]}: 下日冲高率={p3:.2f}% 下日均高幅={avg_hr:.2f}%')

print(f'\n=== 周级武态内：DXZC × DXAB护型 ===')
for zc in ['ZC>0','ZC<=0']:
    for hx in ['甲乙','己','丙','丁戊']:
        s = stats['武'][f'{zc}|{hx}']
        if s['n'] == 0: continue
        p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
        avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
        print(f'  [武|{zc}|{hx}] n={s["n"]}: 下日冲高率={p3:.2f}% 下日均高幅={avg_hr:.2f}%')

print(f'\n=== 周级虎态内：DXZC × DXAB护型 ===')
for zc in ['ZC>0','ZC<=0']:
    for hx in ['甲乙','己','丙','丁戊']:
        s = stats['虎'][f'{zc}|{hx}']
        if s['n'] == 0: continue
        p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
        avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
        print(f'  [虎|{zc}|{hx}] n={s["n"]}: 下日冲高率={p3:.2f}% 下日均高幅={avg_hr:.2f}%')