# -*- coding: utf-8 -*-
"""C6 §5.2 关键数据表重跑 — 按VBA列位置读取"""
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

def classify_zx(zx):
    if '梯' in zx: return '柱梯'
    if '栅' in zx: return '柱栅'
    if '枝' in zx: return '柱枝'
    if '根' in zx: return '柱根'
    return '柱其他'

# 统计: key -> [n, sum, p3]
stats = defaultdict(lambda: [0,0.0,0])
def add(key, nxt):
    s = stats[key]; s[0]+=1; s[1]+=nxt
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
            for row in r:
                if len(row) <= 33: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                dtza = to_f(row[13]); zc = to_f(row[14]); nxt = to_f(row[26])
                bsha = to_f(row[19]); gk = to_f(row[22])
                mf = row[33].strip()[-1] if row[33].strip() else ''
                sf = row[30].strip()
                dxab = row[9].strip(); zx = row[27].strip(); zp = row[10].strip()
                if dtza is None or nxt is None: continue
                dg = classify_dg(dtza, mf)
                hx = parse_hx(dxab)
                zg = classify_zx(zx)
                zc_label = 'ZC>0' if (zc is not None and zc>0) else 'ZC≤0'
                # 触顶: 上符串末位A
                is_touch = len(sf)>0 and sf[-1]=='A'
                # 柱排方向: 升/人/跌
                if '升' in zp: zp_dir = '升排'
                elif '跌' in zp: zp_dir = '跌排'
                else: zp_dir = '人排'
                # 管宽分段
                gk_v = gk if gk is not None else -999
                # ① 等型×ZC
                if dg: add(f'等ZC|{dg}|{zc_label}', nxt)
                # ② 护型×ZC
                if hx: add(f'护ZC|{hx}|{zc_label}', nxt)
                # ③ 等型×护型×ZC 关键场景
                if dg and hx: add(f'等护ZC|{dg}|{hx}|{zc_label}', nxt)
                # ④ ZC五段式×等型
                if dg and zc is not None:
                    if zc<=-2: zc5='ZC≤-2'
                    elif zc==-1: zc5='ZC=-1'
                    elif zc<5: zc5='1≤ZC<5'
                    else: zc5='ZC≥5'
                    add(f'ZC5|{dg}|{zc5}', nxt)
                # 柱型baseline
                add(f'柱型|{zg}', nxt)
                # 日柱排×DXAB
                if hx in '甲乙己': hx_good='甲乙己'
                else: hx_good='非甲乙己'
                add(f'柱排|{zp_dir}|{hx_good}', nxt)
                add(f'柱排|{zp_dir}', nxt)
                # 日顶型×DXAB
                add(f'顶型|{"触顶" if is_touch else "非触顶"}|{hx_good}', nxt)
                add(f'顶型|{"触顶" if is_touch else "非触顶"}', nxt)
                # 管中形态×DXAB
                if gk_v < 5: gk_cat='管宽<5'
                elif gk_v >= 40: gk_cat='管宽≥40'
                else: gk_cat='管宽5-40'
                add(f'管宽|{gk_cat}|{hx_good}', nxt)
                add(f'管宽|{gk_cat}', nxt)
                # 三候选×等高线 对比
                if dg=='等2': add('候选|等高线等2', nxt)
                if dg=='等3': add('候选|等高线等3', nxt)
                if zp_dir=='升排': add('候选|日柱排升排', nxt)
                if is_touch: add('候选|日顶型触顶', nxt)
                if gk_v>=10: add('候选|管宽≥10', nxt)
                if gk_v>=20: add('候选|管宽≥20', nxt)
                # 等高线内部稳定性
                if dg:
                    add(f'稳|{dg}|基线', nxt)
                    if bsha is not None:
                        if bsha<3: add(f'稳|{dg}|BSHA<3', nxt)
                        if bsha>=5: add(f'稳|{dg}|BSHA≥5', nxt)
                    add(f'稳|{dg}|{zp_dir}', nxt)
                    add(f'稳|{dg}|{zc_label}', nxt)
                    if nxt>0: add(f'稳|{dg}|下柱>0', nxt)
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
def show(key):
    if key in stats:
        s = stats[key]
        print(f'{key:<40} n={s[0]:>10,} 均={s[1]/s[0]:.2f}% P3={s[2]/s[0]*100:.1f}%')
    else:
        print(f'{key:<40} 无数据')

print('=== ① 等型×ZC ===')
for dg in ['等1','等2','等3','等5','等6','等7']:
    for zl in ['ZC>0','ZC≤0']:
        show(f'等ZC|{dg}|{zl}')
print()
print('=== ② 护型×ZC ===')
for hx in '甲乙丙丁戊己':
    for zl in ['ZC>0','ZC≤0']:
        show(f'护ZC|{hx}|{zl}')
print()
print('=== ③ 等型×护型×ZC 关键场景 ===')
for dg in ['等1','等2','等3','等5','等6','等7']:
    for hx in '甲乙丙丁戊己':
        for zl in ['ZC>0','ZC≤0']:
            show(f'等护ZC|{dg}|{hx}|{zl}')
print()
print('=== ④ ZC五段式×等型 ===')
for dg in ['等1','等2','等3','等5','等6','等7']:
    for z5 in ['ZC≤-2','ZC=-1','1≤ZC<5','ZC≥5']:
        show(f'ZC5|{dg}|{z5}')
print()
print('=== 柱型baseline ===')
for zg in ['柱梯','柱栅','柱枝','柱根','柱其他']:
    show(f'柱型|{zg}')
print()
print('=== 日柱排×DXAB ===')
for zp_dir in ['升排','人排','跌排']:
    show(f'柱排|{zp_dir}')
    show(f'柱排|{zp_dir}|甲乙己')
    show(f'柱排|{zp_dir}|非甲乙己')
print()
print('=== 日顶型×DXAB ===')
for t in ['触顶','非触顶']:
    show(f'顶型|{t}')
    show(f'顶型|{t}|甲乙己')
    show(f'顶型|{t}|非甲乙己')
print()
print('=== 管中形态×DXAB ===')
for gc in ['管宽<5','管宽≥40']:
    show(f'管宽|{gc}')
    show(f'管宽|{gc}|甲乙己')
    show(f'管宽|{gc}|非甲乙己')
print()
print('=== 三候选×等高线 对比 ===')
for k in ['候选|等高线等2','候选|等高线等3','候选|日柱排升排','候选|日顶型触顶','候选|管宽≥10','候选|管宽≥20']:
    show(k)
print()
print('=== 等高线内部稳定性 ===')
for dg in ['等1','等2','等3','等5','等6','等7']:
    show(f'稳|{dg}|基线')
    show(f'稳|{dg}|BSHA<3')
    show(f'稳|{dg}|BSHA≥5')
    show(f'稳|{dg}|升排')
    show(f'稳|{dg}|跌排')
    show(f'稳|{dg}|ZC>0')
    show(f'稳|{dg}|ZC≤0')
    show(f'稳|{dg}|下柱>0')
