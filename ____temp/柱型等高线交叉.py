# -*- coding: utf-8 -*-
"""柱型 × 等高线 交叉赛马（§1.4.3.2）— 按VBA列位置读取"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 市板映射
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 柱型分组: 梯/栅/枝/根/其他
def classify_zx(zx):
    if '梯' in zx: return '柱梯'
    if '栅' in zx: return '柱栅'
    if '枝' in zx: return '柱枝'
    if '根' in zx: return '柱根'
    return '柱其他'

# 等高线6等（VBA逻辑，用中符串末位）
def classify_dg(dtza, mf):
    if dtza == 1: return '等1'
    elif dtza >= 2:
        return '等3' if mf in 'AB' else '等2'
    elif dtza == -1: return '等5'
    elif dtza <= -2:
        return '等7' if mf in 'EF' else '等6'
    return None

# 统计: key -> [n, h2, h3, sum, dn]
stats = defaultdict(lambda: [0,0,0,0.0,0])

def add(key, nxt):
    s = stats[key]
    s[0]+=1
    if nxt>=2: s[1]+=1
    if nxt>=3: s[2]+=1
    s[3]+=nxt
    if nxt>0: s[4]+=1

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
                if len(row) <= 27: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                dtza = to_f(row[13])
                zc = to_f(row[14])
                nxt = to_f(row[26])
                mf = row[33].strip()[-1] if row[33].strip() else ''
                zx = row[27].strip()
                cd = row[8].strip()
                if dtza is None or nxt is None or not zx: continue
                dg = classify_dg(dtza, mf)
                if dg is None: continue
                zg = classify_zx(zx)
                # 周门
                zm = (zc is not None and zc>0 and cd=='上')
                add(f'{zg}+{dg}', nxt)
                if zm: add(f'{zg}+{dg}_周门', nxt)
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
print('=== 柱型 × 等高线 交叉赛马（H2排序，周门）===')
print(f'{"组合":<20} {"样本":>10} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7} {"下柱>0":>7}')
print('-'*60)
rows = []
for k, s in stats.items():
    if not k.endswith('_周门'): continue
    if s[0] < 1000: continue
    rows.append((s[1]/s[0]*100, k, s[0], s[2]/s[0]*100, s[3]/s[0], s[4]/s[0]*100))
rows.sort(key=lambda x: -x[0])
for h2, k, n, h3, avg, dn in rows:
    print(f'{k:<20} {n:>10,} {h2:>6.1f}% {h3:>6.1f}% {avg:>6.2f}% {dn:>6.1f}%')
