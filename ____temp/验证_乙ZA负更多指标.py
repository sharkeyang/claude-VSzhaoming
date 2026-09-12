# -*- coding: utf-8 -*-
"""
乙(DXZA<0) 转好的更多预测指标：上符串末位/柱排/日ZA×柱排交叉
上符串[30]末位：A=顶 B=哼 v=哈 w=底 _=无
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def sfs_last(sfs):
    s = sfs.strip()
    if not s: return '空'
    c = s[-1]
    return {'A':'触顶','B':'触哼','v':'触哈','w':'触底','_':'无'}.get(c, c)

stats = defaultdict(lambda: [0,0])
def add(key, good):
    stats[key][0]+=1
    stats[key][1]+=(1 if good else 0)

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 30: continue
                if not row[9].strip().startswith('b'): continue
                zpa = to_f(row[13])
                if zpa is None or zpa > 0: continue
                if i+1 >= len(rows): continue
                nht = rows[i+1][9].strip()[:1]
                nzpa = to_f(rows[i+1][13])
                good = (nht=='b' and nzpa is not None and nzpa>0)
                # 上符串末位
                add(f'上符串={sfs_last(row[30])}', good)
                # 日ZA深度 × 柱排 交叉
                zp = classify_zp(row[10])
                if zp != '其他':
                    if zpa <= -4: add(f'深跌(≤-4)+{zp}', good)
                    elif zpa <= -2: add(f'中跌(-3~-2)+{zp}', good)
                    else: add(f'浅跌(-1)+{zp}', good)
                # 日ZA深度 × 上符串
                sl = sfs_last(row[30])
                if zpa <= -4: add(f'深跌+{sl}', good)
                elif zpa <= -2: add(f'中跌+{sl}', good)
                else: add(f'浅跌+{sl}', good)
    except Exception: pass

print('乙(DXZA<0) 转好率：上符串末位')
print(f'{"条件":<20} {"n":>10} {"转好率":>8}')
for k in sorted(stats.keys()):
    if k.startswith('上符串'):
        s = stats[k]
        if s[0] < 1000: continue
        print(f'{k:<20} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')

print()
print('乙(DXZA<0) 转好率：日ZA深度 × 柱排 交叉')
for k in sorted(stats.keys()):
    if '深跌' in k or '中跌' in k or '浅跌' in k:
        if '+' in k and any(z in k for z in ['升排','跌吞','跌连','跌孕','人排']):
            s = stats[k]
            if s[0] < 1000: continue
            print(f'{k:<24} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')

print()
print('乙(DXZA<0) 转好率：日ZA深度 × 上符串 交叉')
for k in sorted(stats.keys()):
    if ('深跌' in k or '中跌' in k or '浅跌' in k) and ('触顶' in k or '触哼' in k or '触哈' in k or '触底' in k or '无' in k):
        s = stats[k]
        if s[0] < 1000: continue
        print(f'{k:<24} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')
