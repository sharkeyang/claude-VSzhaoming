# -*- coding: utf-8 -*-
"""
补充验证：
1. DXCD忠 → 忐 的转移概率（忠状态下，次日变成忐/上/忠/其他 的概率）
2. 广义正交护型按ZA拆分（戊(DXZA>0) vs 戊(DXZA≤0)）
3. 忠状态下护型的维持率（忠 + 甲 → 次日甲 的概率）
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

护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

# 转移统计: (当前CD, 当前护型) -> {次日CD: n}
trans_cd = defaultdict(lambda: defaultdict(int))
# 护型转移: (当前CD, 当前护型) -> {次日护型: n}
trans_hx = defaultdict(lambda: defaultdict(int))
# 广义正交按ZA: (护型, ZA符号, ZC符号) -> [n, hr3]
stats_za = defaultdict(lambda: [0,0])

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            prev = None  # (cd, hx, za, zc, hr)
            for row in r:
                if len(row) <= 26: continue
                cd = row[8].strip()
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                hr = to_f(row[26])
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                # 转移统计（用当前行的次日高幅=下一行，但CD转移需要下一行的CD）
                # 这里用 prev 记录上一行，当前行作为"次日"
                if prev is not None:
                    pcd, phx, pza, pzc = prev
                    # 忠状态下护型维持
                    if pcd == '忠':
                        trans_cd[(pcd, phx)][cd] += 1
                        trans_hx[(pcd, phx)][hx] += 1
                # 广义正交按ZA
                za_key = 'ZA>0' if za>0 else ('ZA=0' if za==0 else 'ZA<0')
                zc_key = 'ZC>0' if zc>0 else 'ZC<=0'
                stats_za[(hx, za_key, zc_key)][0]+=1
                stats_za[(hx, za_key, zc_key)][1]+= (1 if hr>=3 else 0)
                prev = (cd, hx, za, zc)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

# ============ 忠→CD转移 ============
print('='*70)
print('忠状态下，次日DXCD转移概率')
print('='*70)
for phx in ['甲','乙','己','丙','丁','戊']:
    key = ('忠', phx)
    if key not in trans_cd: continue
    total = sum(trans_cd[key].values())
    if total < 1000: continue
    print(f'忠+{phx} (n={total:,}):')
    for cd in ['上','忐','忠','中','下','忑']:
        n = trans_cd[key].get(cd, 0)
        print(f'    →{cd}: {n/total*100:.1f}%')
    print()

# ============ 忠→护型转移 ============
print('='*70)
print('忠状态下，次日护型转移概率')
print('='*70)
for phx in ['甲','乙','己','丙','丁','戊']:
    key = ('忠', phx)
    if key not in trans_hx: continue
    total = sum(trans_hx[key].values())
    if total < 1000: continue
    print(f'忠+{phx} (n={total:,}):')
    for hx in ['甲','乙','丙','己','戊','丁']:
        n = trans_hx[key].get(hx, 0)
        print(f'    →{hx}: {n/total*100:.1f}%')
    print()

# ============ 广义正交按ZA ============
print('='*70)
print('广义正交护型按ZA拆分 (DXZC>0)')
print('='*70)
print(f'{"护型":<6} {"ZA":<6} {"ZC":<6} {"n":>10} {"P(≥3%)":>8}')
print('-'*50)
for hx in ['甲','乙','丙','己','戊','丁']:
    for za_key in ['ZA>0','ZA=0','ZA<0']:
        for zc_key in ['ZC>0','ZC<=0']:
            key = (hx, za_key, zc_key)
            if key in stats_za:
                s = stats_za[key]
                if s[0] >= 500:
                    print(f'{hx:<6} {za_key:<6} {zc_key:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')
