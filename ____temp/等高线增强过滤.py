# -*- coding: utf-8 -*-
"""等高线增强过滤（§1.5.5.1-1.5.5.3）— 按VBA列位置读取"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

def classify_dg(dtza, mf):
    if dtza == 1: return '等1'
    elif dtza >= 2:
        return '等3' if mf in 'AB' else '等2'
    elif dtza == -1: return '等5'
    elif dtza <= -2:
        return '等7' if mf in 'EF' else '等6'
    return None

def parse_hx(dxab):
    if len(dxab) >= 2 and dxab[1] in '甲乙丙丁戊己':
        return dxab[1]
    return ''

# 统计: key -> [n, h2, h3]
stats = defaultdict(lambda: [0,0,0])
def add(key, nxt):
    s = stats[key]; s[0]+=1
    if nxt>=2: s[1]+=1
    if nxt>=3: s[2]+=1

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            prev_rows = []
            for row in r:
                if len(row) <= 33: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                dtza = to_f(row[13]); zc = to_f(row[14]); nxt = to_f(row[26])
                mf = row[33].strip()[-1] if row[33].strip() else ''
                dxab = row[9].strip(); cd = row[8].strip()
                if dtza is None or nxt is None: continue
                dg = classify_dg(dtza, mf)
                if dg is None: continue
                hx = parse_hx(dxab)
                # 操作区域: ZC>0 或 (ZC≤0 且 AB∈甲乙己)
                operable = (zc is not None and zc>0) or (zc is not None and zc<=0 and hx in '甲乙己')
                # 全量
                add(f'全量|{dg}', nxt)
                if operable: add(f'可操作|{dg}', nxt)
                # 前一柱护型
                if prev_rows:
                    prev_dxab = prev_rows[-1]
                    prev_hx = parse_hx(prev_dxab)
                    if prev_hx:
                        add(f'prev|{dg}|{prev_hx}', nxt)
                prev_rows.append(dxab)
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
print('=== §1.5.5.1 操作区域限定 ===')
print(f'{"等高线":<6} {"全量≥2%":>8} {"可操作≥2%":>10} {"提升":>6}')
print('-'*35)
for dg in ['等1','等2','等3','等5','等6','等7']:
    k_all = f'全量|{dg}'; k_ok = f'可操作|{dg}'
    if k_all in stats:
        s_all = stats[k_all]; s_ok = stats[k_ok] if k_ok in stats else [0,0,0]
        p_all = s_all[1]/s_all[0]*100 if s_all[0] else 0
        p_ok = s_ok[1]/s_ok[0]*100 if s_ok[0] else 0
        print(f'{dg:<6} {p_all:>7.1f}% {p_ok:>9.1f}% {p_ok-p_all:>+5.1f}pp')

print()
print('=== §1.5.5.2 等1 前一柱护型 ===')
print(f'{"前一柱护型":<8} {"样本":>8} {"≥2%":>7} {"≥3%":>7}')
print('-'*35)
for hx in '乙丙丁戊':
    k = f'prev|等1|{hx}'
    if k in stats:
        s = stats[k]
        print(f'{hx:<8} {s[0]:>8,} {s[1]/s[0]*100:>6.1f}% {s[2]/s[0]*100:>6.1f}%')

print()
print('=== §1.5.5.3 等2/等5/等6 前一柱护型 ===')
for dg in ['等2','等5','等6']:
    print(f'--- {dg} ---')
    for hx in '甲乙丙丁戊己':
        k = f'prev|{dg}|{hx}'
        if k in stats:
            s = stats[k]
            print(f'  {hx}: n={s[0]:>8,} ≥2%={s[1]/s[0]*100:.1f}%')
