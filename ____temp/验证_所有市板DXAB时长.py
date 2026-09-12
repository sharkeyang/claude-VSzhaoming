# -*- coding: utf-8 -*-
"""
所有市板DXAB持续时长（含基金/指数）
====================================================
验证Qd(指数)/Qe(ETF基金)/Qif(沪深300)/Qst(ST)等市板的DXAB持续时长
是否与高波池(Qic/Qim/Qit)不同
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]

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
q = defaultdict(lambda: [0,0.0])  # key: 市板|方向 -> [run数, 总天数]

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    board = pool.get(code, '')
    if not board: continue
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
            q[f'{board}|正'][0]+=1; q[f'{board}|正'][1]+=length
        elif val < 0:
            start = i
            while i < n:
                hx2, zj2, dirch2, val2 = dxabs[i]
                if val2 is None or val2 >= 0: break
                i += 1
            length = i - start
            q[f'{board}|负'][0]+=1; q[f'{board}|负'][1]+=length
        else:
            i += 1

print(f'文件数: {files_core}')
print()

print('='*75)
print('【所有市板DXAB持续时长】')
print('='*75)
print(f'{"市板":<10} {"方向":<4} {"run数":>10} {"平均天数":>10}')
print('-'*40)
for board in ['Qic','Qim','Qit','Qif','Qin','Qd','Qe','Qst']:
    for d in ['正','负']:
        key = f'{board}|{d}'
        if key in q:
            s = q[key]
            if s[0] >= 100:
                print(f'{board:<10} {d:<4} {s[0]:>10,} {s[1]/s[0]:>9.2f}')
print()