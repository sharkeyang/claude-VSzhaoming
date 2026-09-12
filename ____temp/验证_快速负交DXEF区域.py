# -*- coding: utf-8 -*-
"""
新增A修正：DXAB>0后快速负交(≤5天)的DXEF/DXCD区域分布
DXEF从月策带日(50)提取：(金)▲(上)▲(上) → 第1个括号=DXEF
DXCD从列8提取
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

def extract_ef(月策带日):
    """从月策带日提取DXEF：(金)▲(上)▲(上) → 金"""
    if not 月策带日: return ''
    m = re.search(r'\(([^)]+)\)', 月策带日)
    return m.group(1) if m else ''

# 统计: key -> [快速负交样本, 总DXAB>0样本]
qA = defaultdict(lambda: [0,0])
# 快速负交的DXZC/DXCD分布
qB = defaultdict(lambda: [0,0])

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
    zcs = [to_f(rows[i][14]) for i in range(n)]
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    月策带日s = [rows[i][50].strip() if len(rows[i])>50 else '' for i in range(n)]

    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None or val <= 0: continue
        ef = extract_ef(月策带日s[i])
        cd = dxcds[i]
        zc = zcs[i]
        # 检查后续5天内是否转负
        quick_neg = False
        for k in range(1, 6):
            if i+k >= n: break
            hx2, zj2, dirch2, val2 = dxabs[i+k]
            if val2 is not None and val2 < 0:
                quick_neg = True
                break
        # 记录DXEF/DXCD
        qA[f'{ef}|{cd}'][0]+=1
        qA[f'{ef}|{cd}'][1]+=1
        if quick_neg:
            if zc is not None:
                if zc > 0: qB['快速|ZC>0'][0]+=1
                else: qB['快速|ZC<=0'][0]+=1
            if cd in ('下','忑'): qB['快速|CD<0'][0]+=1
            elif cd in ('上','忐','忠'): qB['快速|CD>0'][0]+=1
            else: qB['快速|CD=中'][0]+=1
        else:
            if zc is not None:
                if zc > 0: qB['非快速|ZC>0'][0]+=1
                else: qB['非快速|ZC<=0'][0]+=1
            if cd in ('下','忑'): qB['非快速|CD<0'][0]+=1
            elif cd in ('上','忐','忠'): qB['非快速|CD>0'][0]+=1
            else: qB['非快速|CD=中'][0]+=1

print(f'高波池文件: {files_core}')
print()

# DXEF/DXCD分布
print('='*75)
print('【DXAB>0后快速负交(≤5天)的DXEF/DXCD区域分布】')
print('='*75)
print(f'{"DXEF":<4} {"DXCD":<4} {"DXAB>0样本":>12} {"快速负交":>10} {"快速负交率":>10}')
print('-'*55)
for ef in ['金','银','唏','嘘','屎','尿']:
    for cd in ['上','忐','忠','中','忑','下']:
        key = f'{ef}|{cd}'
        if key in qA:
            s = qA[key]
            if s[0] >= 100:
                print(f'{ef:<4} {cd:<4} {s[0]:>12,} {s[1]:>10,} {s[1]/s[0]*100:>9.2f}%')
print()

# 按DXEF汇总
print('='*75)
print('【按DXEF汇总的快速负交率】')
print('='*75)
ef_tot = defaultdict(lambda: [0,0])
for k, s in qA.items():
    ef = k.split('|')[0]
    ef_tot[ef][0]+=s[0]; ef_tot[ef][1]+=s[1]
for ef in ['金','银','唏','嘘','屎','尿']:
    if ef in ef_tot:
        s = ef_tot[ef]
        if s[0] >= 100:
            print(f'{ef:<4} DXAB>0样本={s[0]:>12,} 快速负交={s[1]:>10,} 快速负交率={s[1]/s[0]*100:>7.2f}%')
print()

# 按DXCD汇总
print('='*75)
print('【按DXCD汇总的快速负交率】')
print('='*75)
cd_tot = defaultdict(lambda: [0,0])
for k, s in qA.items():
    cd = k.split('|')[1]
    cd_tot[cd][0]+=s[0]; cd_tot[cd][1]+=s[1]
for cd in ['上','忐','忠','中','忑','下']:
    if cd in cd_tot:
        s = cd_tot[cd]
        if s[0] >= 100:
            print(f'{cd:<4} DXAB>0样本={s[0]:>12,} 快速负交={s[1]:>10,} 快速负交率={s[1]/s[0]*100:>7.2f}%')
print()

# 快速负交的DXZC/DXCD分布
print('='*75)
print('【快速负交 vs 非快速负交 的DXZC/DXCD分布】')
print('='*75)
for k in ['快速|ZC>0','快速|ZC<=0','非快速|ZC>0','非快速|ZC<=0']:
    if k in qB:
        s = qB[k]
        print(f'{k:<16} n={s[0]:>12,}')
print()
for k in ['快速|CD>0','快速|CD<0','快速|CD=中','非快速|CD>0','非快速|CD<0','非快速|CD=中']:
    if k in qB:
        s = qB[k]
        print(f'{k:<16} n={s[0]:>12,}')
print()