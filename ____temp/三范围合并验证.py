# -*- coding: utf-8 -*-
"""三范围合并验证 + 执念范围重跑 — 按当前VBA列位置
宽范围 = DXZC>0
禁区范围 = DXZE≤0 + DXCD=下/忑
执念范围 = 剩余 = {DXZC≤0 ∩ DXCD=中} ∪ {DXZC≤0 ∩ DXCD∈{下,忑} ∩ DXZE>0}
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])
def add(key, nxt):
    s = stats[key]; s[0]+=1
    if nxt>=3: s[1]+=1
    s[2]+=nxt

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            prev = None
            for row in r:
                if len(row) <= 50: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                cd = row[8].strip()
                ab = row[9].strip()
                zc = to_f(row[14])
                ze = to_f(row[15])
                nxt = to_f(row[26])
                ef = row[50][1] if len(row[50])>1 else '?'
                if zc is None or ze is None or nxt is None: continue
                if prev is not None:
                    p_cd, p_zc, p_ze, p_nxt = prev
                    if p_nxt < -50 or p_nxt > 50:
                        prev = (cd, zc, ze, nxt); continue
                    hr3 = 1 if p_nxt >= 3 else 0
                    # 基线
                    add('基线', p_nxt)
                    # 宽范围: DXZC>0
                    if p_zc > 0:
                        add('宽范围', p_nxt)
                    # 禁区范围: DXZE≤0 + DXCD=下/忑
                    if p_ze <= 0 and p_cd in ('下','忑'):
                        add('禁区范围', p_nxt)
                    # 执念范围: 剩余
                    # 部分1: DXZC≤0 + DXCD=中
                    if p_zc <= 0 and p_cd == '中':
                        add('执念范围', p_nxt)
                        add('执念_部分1_CD中', p_nxt)
                    # 部分2: DXZC≤0 + DXCD∈{下,忑} + DXZE>0
                    if p_zc <= 0 and p_cd in ('下','忑') and p_ze > 0:
                        add('执念范围', p_nxt)
                        add('执念_部分2_CD下忑_ZE>0', p_nxt)
                prev = (cd, zc, ze, nxt)
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
def show(key):
    if key in stats:
        s = stats[key]
        print(f'{key:<28} n={s[0]:>10,} 次日冲高≥3%={s[1]/s[0]*100:.2f}% 平均次日高幅={s[2]/s[0]:.2f}%')
    else:
        print(f'{key:<28} n=0')

print('=== 三范围合并验证 ===')
show('基线')
show('宽范围')
show('禁区范围')
show('执念范围')
show('执念_部分1_CD中')
show('执念_部分2_CD下忑_ZE>0')

# 验证合并
n_all = stats['基线'][0]
n_w = stats['宽范围'][0]
n_a = stats['禁区范围'][0]
n_z = stats['执念范围'][0]
print()
print(f'宽范围 + 禁区范围 + 执念范围 = {n_w:,} + {n_a:,} + {n_z:,} = {n_w+n_a+n_z:,}')
print(f'基线(全部) = {n_all:,}')
print(f'合并/全部 = {(n_w+n_a+n_z)/n_all*100:.2f}%')