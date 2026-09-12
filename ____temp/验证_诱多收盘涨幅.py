# -*- coding: utf-8 -*-
"""
重新验证诱多（用收盘涨幅>0概率）+ 转负比例从1罗列（高波池）
====================================================
1. 乙(DXZA>0)DXZA=1+前跌排+升吞 是否诱多（用次日收盘涨幅>0概率 + 次日涨幅期望）
2. 升连上影阳柱 是否诱多（用次日收盘涨幅>0概率）
3. DXAB负转正后转负比例从1开始罗列（分DXZE/DXEF）
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

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def extract_ef(月策带日):
    if not 月策带日: return ''
    m = re.search(r'\(([^)]+)\)', 月策带日)
    return m.group(1) if m else ''

# ============ 统计容器 ============
# 1. 乙ZA1前跌排升吞（用次日收盘涨幅>0概率）
q1 = defaultdict(lambda: [0,0,0.0])  # key -> [n, 次日涨幅>0, sum_次日涨幅]
# 2. 升连上影阳柱（用次日收盘涨幅>0概率）
q2 = defaultdict(lambda: [0,0,0.0])
# 3. DXAB负转正后转负比例（从1开始罗列）
q3 = defaultdict(lambda: [0,0])  # key: 情况|N天 -> [n, 转负]

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
    zes = [to_f(rows[i][15]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]  # 当日涨幅
    nxt_zfs = [to_f(rows[i+1][5]) if i+1 < n else None for i in range(n)]  # 次日涨幅
    月策带日s = [rows[i][50].strip() if len(rows[i])>50 else '' for i in range(n)]
    zps = [rows[i][10].strip() if len(rows[i])>10 else '' for i in range(n)]

    # ===== 1. 乙ZA1前跌排升吞（用次日收盘涨幅>0概率） =====
    for i in range(n):
        hx = parse_hx(rows[i][9].strip())
        za = zas[i]; nxt_zf = nxt_zfs[i]
        if hx != '乙' or za is None or nxt_zf is None: continue
        if za == 1 and '升.尾吞' in zps[i]:
            prev_zp = zps[i-1] if i>0 else ''
            if '跌' in prev_zp:
                q1['乙ZA=1+前跌排+升吞'][0]+=1; q1['乙ZA=1+前跌排+升吞'][1]+= (1 if nxt_zf>0 else 0); q1['乙ZA=1+前跌排+升吞'][2]+=nxt_zf
            else:
                q1['乙ZA=1+非跌排+升吞'][0]+=1; q1['乙ZA=1+非跌排+升吞'][1]+= (1 if nxt_zf>0 else 0); q1['乙ZA=1+非跌排+升吞'][2]+=nxt_zf
        # 对照：乙ZA=1整体
        if hx == '乙' and za == 1:
            q1['乙ZA=1整体'][0]+=1; q1['乙ZA=1整体'][1]+= (1 if nxt_zf>0 else 0); q1['乙ZA=1整体'][2]+=nxt_zf

    # ===== 2. 升连上影阳柱（用次日收盘涨幅>0概率） =====
    for i in range(n):
        nxt_zf = nxt_zfs[i]; zf = zfs[i]
        if nxt_zf is None or zf is None: continue
        if '升.尾连' not in zps[i]: continue
        if zf > 0:
            hr_high = to_f(rows[i][6])  # 高幅
            if hr_high is not None and hr_high > zf:
                q2['升连+上影阳柱'][0]+=1; q2['升连+上影阳柱'][1]+= (1 if nxt_zf>0 else 0); q2['升连+上影阳柱'][2]+=nxt_zf
            else:
                q2['升连+无上影阳柱'][0]+=1; q2['升连+无上影阳柱'][1]+= (1 if nxt_zf>0 else 0); q2['升连+无上影阳柱'][2]+=nxt_zf

    # ===== 3. DXAB负转正后转负比例（从1开始罗列） =====
    for i in range(1, n):
        hx_prev, zj_prev, dirch_prev, val_prev = dxabs[i-1]
        hx, zj, dirch, val = dxabs[i]
        if val is None or val_prev is None: continue
        if not (val_prev < 0 and val > 0): continue
        ze = zes[i]
        ef = extract_ef(月策带日s[i])
        for N in [1,2,3,4,5,6,7,8,9,10]:
            turned = False
            for k in range(1, N+1):
                if i+k >= n: break
                hx2, zj2, dirch2, val2 = dxabs[i+k]
                if val2 is not None and val2 < 0:
                    turned = True; break
            # 分DXZE
            if ze is None:
                case = '全局'
            elif ze > 0:
                case = 'DXZE>0'
            else:
                case = 'DXZE<0'
            if turned:
                q3[f'{case}|{N}天'][0]+=1; q3[f'{case}|{N}天'][1]+=1
            else:
                q3[f'{case}|{N}天'][0]+=1
            # 分DXEF
            if ef in ('金','银','唏'):
                case2 = 'DXEF>0'
            elif ef in ('嘘','屎','尿'):
                case2 = 'DXEF≤0'
            else:
                case2 = 'DXEF未知'
            if turned:
                q3[f'{case2}|{N}天'][0]+=1; q3[f'{case2}|{N}天'][1]+=1
            else:
                q3[f'{case2}|{N}天'][0]+=1

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    print(f'{"类别":<24} {"n":>10} {"次日涨>0":>8} {"次日均涨幅":>10}')
    print('-'*55)
    for k in keys:
        if k in d:
            s = d[k]
            if s[0] >= 100:
                print(f'{k:<24} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>9.2f}%')
    print()

show(q1, '1. 乙ZA1前跌排升吞（次日收盘涨幅>0概率）', ['乙ZA=1+前跌排+升吞','乙ZA=1+非跌排+升吞','乙ZA=1整体'])
show(q2, '2. 升连上影阳柱（次日收盘涨幅>0概率）', ['升连+上影阳柱','升连+无上影阳柱'])

# 3. 转负比例
print('='*75)
print('【3. DXAB负转正后转负比例（从1天开始罗列）】')
print('='*75)
for case in ['全局','DXZE>0','DXZE<0','DXEF>0','DXEF≤0']:
    print(f'--- {case} ---')
    print(f'{"N天":<6} {"n":>10} {"转负":>10} {"转负率":>8}')
    print('-'*40)
    for N in [1,2,3,4,5,6,7,8,9,10]:
        k = f'{case}|{N}天'
        if k in q3:
            s = q3[k]
            if s[0] >= 100:
                print(f'{N}天    {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
    print()