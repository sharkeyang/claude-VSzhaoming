# -*- coding: utf-8 -*-
"""§1.4.2.3 条件边际贡献与叠加规律 — 按VBA列位置读取"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 统计: key -> [n, h2]
stats = defaultdict(lambda: [0,0])
def add(key, nxt):
    s = stats[key]; s[0]+=1
    if nxt>=2: s[1]+=1

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
                if len(row) <= 42: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                nxt = to_f(row[26])
                zc = to_f(row[14])
                bsha = to_f(row[19])
                btly = to_f(row[42])
                btding = to_f(row[40])
                if nxt is None: continue
                cd = row[8].strip()
                dxab = row[9].strip()
                ceng = row[28].strip()
                hx = dxab[1] if len(dxab)>1 and dxab[1] in '甲乙丙丁戊己' else ''
                # 条件
                cond_bsha5 = bsha is not None and bsha > 5
                cond_bsha3 = bsha is not None and bsha > 3
                cond_ly = btly is not None and btly > 0
                cond_btding = btding is not None and btding > 0
                cond_men = zc is not None and zc > 0 and cd == '上'
                cond_cengzhu = ceng == '主'
                cond_zc = zc is not None and zc > 0
                cond_hx_good = hx in '甲乙己'
                # 全量基准
                add('全量', nxt)
                # 单独条件
                if cond_bsha5: add('BSHA5', nxt)
                if cond_bsha3: add('BSHA3', nxt)
                if cond_ly: add('连阳', nxt)
                if cond_btding: add('BT鼎', nxt)
                if cond_men: add('门', nxt)
                if cond_cengzhu: add('层主', nxt)
                if cond_zc: add('ZC>0', nxt)
                if cond_hx_good: add('甲乙己', nxt)
                # BSHA5叠加
                if cond_bsha5 and cond_ly: add('BSHA5+连阳', nxt)
                if cond_bsha5 and cond_men: add('BSHA5+门', nxt)
                if cond_bsha5 and cond_ly and cond_men: add('BSHA5+连阳+门', nxt)
                if cond_bsha5 and cond_zc: add('BSHA5+ZC>0', nxt)
                if cond_bsha5 and cond_hx_good: add('BSHA5+甲乙己', nxt)
                if cond_bsha5 and cond_zc and cond_hx_good and cond_ly: add('BSHA5+ZC>0+甲乙己+连阳', nxt)
                # 无BSHA5替代
                if cond_bsha3 and cond_ly: add('BSHA3+连阳', nxt)
                if cond_bsha3 and cond_men: add('BSHA3+门', nxt)
                if cond_ly and cond_men: add('连阳+门', nxt)
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
def show(key):
    if key in stats:
        s = stats[key]
        print(f'{key:<28} n={s[0]:>10,} H2={s[1]/s[0]*100:.1f}%')
    else:
        print(f'{key:<28} 无数据')

print('=== 各条件单独 vs 全量基准 ===')
show('全量')
for k in ['BSHA5','BSHA3','连阳','BT鼎','门','层主','ZC>0','甲乙己']:
    show(k)
print()
print('=== BSHA5 之上叠加 ===')
for k in ['BSHA5','BSHA5+连阳','BSHA5+门','BSHA5+连阳+门','BSHA5+ZC>0','BSHA5+甲乙己','BSHA5+ZC>0+甲乙己+连阳']:
    show(k)
print()
print('=== 无 BSHA5 替代 ===')
for k in ['BSHA3+连阳','BSHA3+门','连阳+门']:
    show(k)
