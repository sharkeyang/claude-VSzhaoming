# -*- coding: utf-8 -*-
"""§1.5.5.5 赛马组合增强 + §1.5.5.6 触顶条件 — 按VBA列位置读取"""
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
    elif dtza >= 2: return '等3' if mf in 'AB' else '等2'
    elif dtza == -1: return '等5'
    elif dtza <= -2: return '等7' if mf in 'EF' else '等6'
    return None

def parse_hx(dxab):
    if len(dxab) > 1 and dxab[1] in '甲乙丙丁戊己': return dxab[1]
    return ''

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
            prev_dxab = ''
            for row in r:
                if len(row) <= 33: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                dtza = to_f(row[13]); zc = to_f(row[14]); nxt = to_f(row[26]); bsha = to_f(row[19])
                mf = row[33].strip()[-1] if row[33].strip() else ''
                sf = row[30].strip()  # 上符串（触顶判断）
                dxab = row[9].strip(); cd = row[8].strip()
                if dtza is None or nxt is None: continue
                dg = classify_dg(dtza, mf)
                if dg is None: continue
                hx = parse_hx(dxab)
                prev_hx = parse_hx(prev_dxab)
                # 条件
                cond_bsha5 = bsha is not None and bsha > 5
                cond_bsha4 = bsha is not None and bsha > 4
                cond_men = zc is not None and zc > 0 and cd == '上'
                cond_operable = (zc is not None and zc > 0) or (zc is not None and zc <= 0 and hx in '甲乙己')
                cond_prev_good = prev_hx in '甲乙'
                is_touch = 'v' in sf
                # §1.5.5.5 等1 赛马组合
                if dg == '等1':
                    if cond_bsha5: add('等1+BSHA5', nxt)
                    if cond_bsha5 and cond_operable: add('等1+可操作+BSHA5', nxt)
                    if cond_bsha5 and cond_men: add('等1+周门+BSHA5', nxt)
                    if cond_bsha5 and cond_prev_good: add('等1+前一柱甲乙+BSHA5', nxt)
                    if cond_bsha5 and cond_prev_good and cond_men: add('等1+前一柱甲乙+BSHA5+周门', nxt)
                # §1.5.5.5 等5 赛马组合
                if dg == '等5':
                    if cond_bsha5: add('等5+BSHA5', nxt)
                    if cond_bsha5 and cond_prev_good: add('等5+前一柱甲乙+BSHA5', nxt)
                    if cond_bsha5 and cond_prev_good and cond_men: add('等5+前一柱甲乙+BSHA5+周门', nxt)
                    if cond_bsha4 and cond_men: add('等5+BSHA4+周门', nxt)
                # §1.5.5.5 等2/等3 增强过滤
                if dg == '等2':
                    if cond_bsha5: add('等2+BSHA5', nxt)
                    if cond_bsha5 and cond_prev_good: add('等2+BSHA5+前一柱甲乙', nxt)
                    if cond_bsha5 and cond_men: add('等2+BSHA5+周门', nxt)
                    if cond_bsha5 and cond_men and cond_prev_good: add('等2+BSHA5+周门+前一柱甲乙', nxt)
                if dg == '等3':
                    if cond_bsha5: add('等3+BSHA5', nxt)
                    if cond_bsha5 and cond_prev_good: add('等3+BSHA5+前一柱甲乙', nxt)
                # §1.5.5.6 触顶
                add(f'触顶|{dg}|{"触" if is_touch else "不触"}', nxt)
                if cond_bsha5:
                    add(f'触顶BSHA5|{dg}|{"触" if is_touch else "不触"}', nxt)
                if cond_bsha4:
                    add(f'触顶BSHA4|{dg}|{"触" if is_touch else "不触"}', nxt)
                prev_dxab = dxab
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
def show(key):
    if key in stats:
        s = stats[key]
        print(f'{key:<34} n={s[0]:>9,} ≥2%={s[1]/s[0]*100:.1f}% ≥3%={s[2]/s[0]*100:.1f}%')
    else:
        print(f'{key:<34} 无数据')

print('=== §1.5.5.5 等1 赛马组合 ===')
for k in ['等1+前一柱甲乙+BSHA5+周门','等1+前一柱甲乙+BSHA5','等1+周门+BSHA5','等1+可操作+BSHA5','等1+BSHA5']:
    show(k)
print()
print('=== §1.5.5.5 等5 赛马组合 ===')
for k in ['等5+前一柱甲乙+BSHA5','等5+BSHA5','等5+前一柱甲乙+BSHA5+周门','等5+BSHA4+周门']:
    show(k)
print()
print('=== §1.5.5.5 等2/等3 增强过滤 ===')
for k in ['等2+BSHA5','等2+BSHA5+前一柱甲乙','等2+BSHA5+周门','等2+BSHA5+周门+前一柱甲乙','等3+BSHA5','等3+BSHA5+前一柱甲乙']:
    show(k)
print()
print('=== §1.5.5.6 触顶 vs 不触顶 ===')
for dg in ['等1','等2','等3','等6']:
    show(f'触顶|{dg}|触')
    show(f'触顶|{dg}|不触')
print()
print('=== §1.5.5.6 触顶+BSHA5 ===')
for dg in ['等1','等2','等3','等6']:
    show(f'触顶BSHA5|{dg}|触')
    show(f'触顶BSHA5|{dg}|不触')
print()
print('=== §1.5.5.6 触顶+BSHA4 ===')
for dg in ['等6']:
    show(f'触顶BSHA4|{dg}|触')
    show(f'触顶BSHA4|{dg}|不触')
