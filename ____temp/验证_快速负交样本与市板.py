# -*- coding: utf-8 -*-
"""
快速负交样本数 + DXAB持续时长与市板相关（高波池）
====================================================
1. 快速负交的护型×DXCD交叉样本数
2. DXAB持续时长与市板相关（指数等是否更稳定）
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

# ============ 统计容器 ============
# 1. 快速负交的护型×DXCD交叉样本数
q1 = defaultdict(lambda: [0,0])  # key: 护型|DXCD -> [DXAB>0样本, 快速负交]
# 2. DXAB持续时长与市板相关
q2 = defaultdict(lambda: [0,0.0])  # key: 市板 -> [run数, 总天数]

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
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    board = pool.get(code, '')

    # ===== 1. 快速负交的护型×DXCD交叉样本数 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None or val <= 0: continue
        cd = dxcds[i]
        # 检查后续5天内是否转负
        quick_neg = False
        for k in range(1, 6):
            if i+k >= n: break
            hx2, zj2, dirch2, val2 = dxabs[i+k]
            if val2 is not None and val2 < 0:
                quick_neg = True; break
        q1[f'{hx}|{cd}'][0]+=1
        if quick_neg: q1[f'{hx}|{cd}'][1]+=1

    # ===== 2. DXAB持续时长与市板相关 =====
    i = 0
    while i < n:
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None:
            i += 1; continue
        if val > 0:
            start = i
            while i < n:
                hx2, zj2, dirch2, val2 = dxabs[i]
                if val2 is None or val2 <= 0: break
                i += 1
            length = i - start
            q2[f'{board}|正'][0]+=1; q2[f'{board}|正'][1]+=length
        elif val < 0:
            start = i
            while i < n:
                hx2, zj2, dirch2, val2 = dxabs[i]
                if val2 is None or val2 >= 0: break
                i += 1
            length = i - start
            q2[f'{board}|负'][0]+=1; q2[f'{board}|负'][1]+=length
        else:
            i += 1

print(f'高波池文件: {files_core}')
print()

# ===== 1输出 =====
print('='*75)
print('【1】快速负交的护型×DXCD交叉样本数')
print('='*75)
print(f'{"护型":<4} {"DXCD":<4} {"DXAB>0样本":>12} {"快速负交":>10} {"快速负交率":>10}')
print('-'*50)
for hx in ['甲','乙','己','戊','丙','丁']:
    for cd in ['上','忐','忠','中','忑','下']:
        key = f'{hx}|{cd}'
        if key in q1:
            s = q1[key]
            if s[0] >= 100:
                print(f'{hx:<4} {cd:<4} {s[0]:>12,} {s[1]:>10,} {s[1]/s[0]*100:>9.2f}%')
print()

# ===== 2输出 =====
print('='*75)
print('【2】DXAB持续时长与市板相关')
print('='*75)
print(f'{"市板":<8} {"方向":<4} {"run数":>10} {"平均天数":>10}')
print('-'*40)
for board in ['Qic','Qim','Qit']:
    for d in ['正','负']:
        key = f'{board}|{d}'
        if key in q2:
            s = q2[key]
            if s[0] >= 100:
                print(f'{board:<8} {d:<4} {s[0]:>10,} {s[1]/s[0]:>9.2f}')
print()