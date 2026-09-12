# -*- coding: utf-8 -*-
"""
用户算法可行性评估：DJC丘 → 广义正交 → DJA丘(日等型) 分层
====================================================
用户算法：
  第1层 DJC丘 = DXZC>0区域（价格在日JC=EMA26之上）
  第2层 DXAB广义正交区域 = 广义正交护型（己/戊ZA>0/甲/乙/丙）
  第3层 日等型聚焦DJA丘（日ZA>0，即等1/等2/等3/等4）

评估：每层P(≥3%)、均高幅、样本占比、增量贡献
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def calc_等型(dtza, 末符):
    """等高线分类（阈值3）"""
    if dtza == 1: return '等1'
    elif dtza > 0:
        if dtza >= 2 and 末符 in 'AB': return '等3'
        elif dtza >= 2 and 末符 in 'CDEF': return '等2'
        elif dtza > 3 and 末符 in 'CDEF': return '等4'
    elif dtza == -1: return '等5'
    elif dtza < 0:
        if dtza <= -2 and 末符 in 'EF': return '等7'
        elif dtza <= -2 and 末符 in 'ABCD': return '等6'
        elif dtza < -3 and 末符 in 'ABCD': return '等8'
    return ''

def is_广义(hx, za):
    """广义正交护型：己、戊(ZA>0)、甲、乙、丙"""
    if hx == '己': return True
    if hx == '戊': return za > 0
    if hx in ('甲','乙','丙'): return True
    return False

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    s = stats[key]; s[0]+=1
    if hr>=3: s[1]+=1
    s[2]+=hr

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
            rows = list(r)
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    for i in range(n):
        row = rows[i]
        if len(row) <= 26: continue
        dxab = row[9].strip()
        za = to_f(row[13])
        zc = to_f(row[14])
        hr = to_f(row[26])
        中符串 = row[33].strip() if len(row) > 33 else ''
        if za is None or zc is None or hr is None: continue
        if hr < -50 or hr > 50: continue
        hx = parse_hx(dxab)
        if not hx: continue
        末符 = 中符串[-1] if 中符串 else ''
        等型 = calc_等型(za, 末符)

        # 第1层: DJC丘（DXZC>0）
        if zc > 0:
            add('L1_DJC丘', hr)
            # 第2层: 广义正交
            if is_广义(hx, za):
                add('L2_广义正交', hr)
                # 第3层: DJA丘（日ZA>0 = 等1/2/3/4）
                if za > 0:
                    add('L3_DJA丘', hr)
                    if 等型:
                        add(f'L3_{等型}', hr)
                else:
                    add('L3_非DJA丘', hr)
            else:
                add('L2_非广义', hr)
        else:
            add('L0_非DJC丘', hr)

print(f'高波池文件: {files_core}')
print()

def show(label, key):
    s = stats[key]
    if s[0] == 0: return
    print(f'{label:<22} n={s[0]:>12,}  P(≥3%)={s[1]/s[0]*100:>6.2f}%  均高幅={s[2]/s[0]:>5.2f}%')

print('='*70)
print('【分层漏斗】DJC丘 → 广义正交 → DJA丘')
print('='*70)
show('L0_非DJC丘', 'L0_非DJC丘')
show('L1_DJC丘(DXZC>0)', 'L1_DJC丘')
show('L2_广义正交', 'L2_广义正交')
show('L2_非广义', 'L2_非广义')
show('L3_DJA丘(日ZA>0)', 'L3_DJA丘')
show('L3_非DJA丘', 'L3_非DJA丘')
print()

# 各层占比
base = stats['L1_DJC丘'][0]
print('='*70)
print('【各层占比】（相对DJC丘）')
print('='*70)
for label, key in [('广义正交', 'L2_广义正交'), ('非广义', 'L2_非广义'), ('DJA丘', 'L3_DJA丘'), ('非DJA丘', 'L3_非DJA丘')]:
    s = stats[key]
    if s[0] > 0:
        print(f'{label:<12} 占DJC丘 {s[0]/base*100:>6.2f}%')
print()

# 第3层各等型
print('='*70)
print('【第3层 DJA丘内各等型】')
print('='*70)
for 等 in ['等1','等2','等3','等4']:
    show(f'  DJA丘+{等}', f'L3_{等}')
print()

# 增量贡献：每层相对上一层的提升
print('='*70)
print('【增量贡献】')
print('='*70)
s0 = stats['L0_非DJC丘']
s1 = stats['L1_DJC丘']
s2 = stats['L2_广义正交']
s3 = stats['L3_DJA丘']
print(f'非DJC丘基线: P(≥3%)={s0[1]/s0[0]*100:.2f}%')
print(f'DJC丘:       P(≥3%)={s1[1]/s1[0]*100:.2f}%  (+{s1[1]/s1[0]*100-s0[1]/s0[0]*100:.2f}pp)')
print(f'广义正交:     P(≥3%)={s2[1]/s2[0]*100:.2f}%  (+{s2[1]/s2[0]*100-s1[1]/s1[0]*100:.2f}pp vs DJC丘)')
print(f'DJA丘:       P(≥3%)={s3[1]/s3[0]*100:.2f}%  (+{s3[1]/s3[0]*100-s2[1]/s2[0]*100:.2f}pp vs 广义正交)')
print()

# 关键：DJA丘内等型 vs 广义正交整体
print('='*70)
print('【DJA丘内等型 vs 广义正交整体（找最优）】')
print('='*70)
for 等 in ['等1','等2','等3','等4']:
    s = stats[f'L3_{等}']
    if s[0] > 0:
        print(f'  DJA丘+{等}: n={s[0]:,} P(≥3%)={s[1]/s[0]*100:.2f}% 均高幅={s[2]/s[0]:.2f}%')