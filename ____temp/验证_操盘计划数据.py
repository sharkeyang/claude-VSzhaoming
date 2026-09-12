# -*- coding: utf-8 -*-
"""
操盘计划数据研究（高波池）
====================================================
1. 验证乙ZA<0/丙提前退出的实战胜率（次日冲高率，确认退出是对的）
2. 验证DXZC<0中DXAB>0上破的实战胜率（介入后冲高率）
3. 收集操盘计划所需数据：各介入点P(≥3%)、均高幅、期望收益
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

def parse_dxab(dxab):
    if len(dxab) < 3: return ('','','',None)
    hx = hxmap.get(dxab[0], '')
    zj = dxab[2]
    dirch = dxab[3] if len(dxab) > 3 else ''
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    val = int(m.group(1)) if m else None
    return (hx, zj, dirch, val)

def is_广义(hx, za):
    if hx == '己': return True
    if hx == '戊': return za > 0
    if hx in ('甲','乙','丙'): return True
    return False

def calc_等型(dtza, 末符):
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

# ============ 统计容器 ============
# 1. 乙ZA<0/丙提前退出：次日冲高率（确认退出是对的）
q1 = defaultdict(lambda: [0,0,0.0])  # key: 护型 -> [样本, hr>=3, sum_hr]
# 2. DXZC<0中DXAB>0上破：介入后冲高率
q2 = defaultdict(lambda: [0,0,0.0])
# 3. 操盘计划数据：各介入点
q3 = defaultdict(lambda: [0,0,0.0])

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
    dxabs = [parse_dxab(rows[i][9].strip()) for i in range(n)]
    zas = [to_f(rows[i][13]) for i in range(n)]
    zcs = [to_f(rows[i][14]) for i in range(n)]
    hrs = [to_f(rows[i][26]) for i in range(n)]
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    中符串s = [rows[i][35].strip() if len(rows[i])>35 else '' for i in range(n)]

    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        za = zas[i]; zc = zcs[i]; hr = hrs[i]
        if za is None or zc is None or hr is None: continue
        if hr < -50 or hr > 50: continue
        末符 = 中符串s[i][-1] if 中符串s[i] else ''
        等型 = calc_等型(za, 末符)
        cd = dxcds[i]

        # ===== 1. 乙ZA<0/丙提前退出 =====
        # 当前DXZC>0，乙ZA<0或丙，次日冲高率（确认退出是对的）
        if zc > 0:
            if hx == '乙' and za < 0:
                q1['乙ZA<0|ZC>0'][0]+=1; q1['乙ZA<0|ZC>0'][1]+= (1 if hr>=3 else 0); q1['乙ZA<0|ZC>0'][2]+=hr
            if hx == '丙':
                q1['丙|ZC>0'][0]+=1; q1['丙|ZC>0'][1]+= (1 if hr>=3 else 0); q1['丙|ZC>0'][2]+=hr

        # ===== 2. DXZC<0中DXAB>0上破 =====
        # 当前DXZC<0，DXAB>0，次日冲高率（介入后）
        if zc <= 0 and val is not None and val > 0:
            q2['DXZC<0|DXAB>0'][0]+=1; q2['DXZC<0|DXAB>0'][1]+= (1 if hr>=3 else 0); q2['DXZC<0|DXAB>0'][2]+=hr
            # 细分：DXCD
            if cd in ('上','忐'):
                q2['DXZC<0|DXAB>0|CD上忐'][0]+=1; q2['DXZC<0|DXAB>0|CD上忐'][1]+= (1 if hr>=3 else 0); q2['DXZC<0|DXAB>0|CD上忐'][2]+=hr
            elif cd in ('中','下','忑'):
                q2['DXZC<0|DXAB>0|CD中下忑'][0]+=1; q2['DXZC<0|DXAB>0|CD中下忑'][1]+= (1 if hr>=3 else 0); q2['DXZC<0|DXAB>0|CD中下忑'][2]+=hr

        # ===== 3. 操盘计划数据 =====
        # 核心介入点：DJC丘 + 真正交 + DJA丘(等1/等3)
        if zc > 0 and val is not None and val > 0 and cd in ('上','忐') and za > 0:
            q3['核心|DJC+真正交+DJA'][0]+=1; q3['核心|DJC+真正交+DJA'][1]+= (1 if hr>=3 else 0); q3['核心|DJC+真正交+DJA'][2]+=hr
            if 等型:
                q3[f'核心|{等型}'][0]+=1; q3[f'核心|{等型}'][1]+= (1 if hr>=3 else 0); q3[f'核心|{等型}'][2]+=hr
        # 对照：DJC丘 + 真正交（不含DJA）
        if zc > 0 and val is not None and val > 0 and cd in ('上','忐'):
            q3['对照|DJC+真正交'][0]+=1; q3['对照|DJC+真正交'][1]+= (1 if hr>=3 else 0); q3['对照|DJC+真正交'][2]+=hr
        # 对照：DJC丘 + DJA丘（不含真正交）
        if zc > 0 and za > 0:
            q3['对照|DJC+DJA'][0]+=1; q3['对照|DJC+DJA'][1]+= (1 if hr>=3 else 0); q3['对照|DJC+DJA'][2]+=hr
        # 对照：DJC丘 + 剔忠
        if zc > 0 and not (cd == '忠'):
            q3['对照|DJC+剔忠'][0]+=1; q3['对照|DJC+剔忠'][1]+= (1 if hr>=3 else 0); q3['对照|DJC+剔忠'][2]+=hr

print(f'高波池文件: {files_core}')
print()

# ===== 1输出 =====
print('='*75)
print('【1】乙ZA<0/丙提前退出：次日冲高率（确认退出是对的）')
print('='*75)
print(f'{"类别":<16} {"样本":>12} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*50)
for k in ['乙ZA<0|ZC>0','丙|ZC>0']:
    if k in q1:
        s = q1[k]
        if s[0] >= 100:
            print(f'{k:<16} {s[0]:>12,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 2输出 =====
print('='*75)
print('【2】DXZC<0中DXAB>0上破：次日冲高率（介入后）')
print('='*75)
print(f'{"类别":<24} {"样本":>12} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*55)
for k in ['DXZC<0|DXAB>0','DXZC<0|DXAB>0|CD上忐','DXZC<0|DXAB>0|CD中下忑']:
    if k in q2:
        s = q2[k]
        if s[0] >= 100:
            print(f'{k:<24} {s[0]:>12,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 3输出 =====
print('='*75)
print('【3】操盘计划核心介入点数据')
print('='*75)
print(f'{"类别":<24} {"样本":>12} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*55)
for k in ['核心|DJC+真正交+DJA','核心|等1','核心|等3','对照|DJC+真正交','对照|DJC+DJA','对照|DJC+剔忠']:
    if k in q3:
        s = q3[k]
        if s[0] >= 100:
            print(f'{k:<24} {s[0]:>12,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()