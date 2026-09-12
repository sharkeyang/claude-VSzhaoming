# -*- coding: utf-8 -*-
"""
DXAB负转正特权修正版（高波池）
====================================================
修正：DXEF直接区分（金/银/唏 vs 嘘/屎/尿），不依赖DXZE
补充：DJA之上跌连后升吞（扩大样本）
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
# 1. DXAB负转正后特权（按DXEF直接分）
q1 = defaultdict(lambda: [0,0,0.0])
# 2. DJA之上跌连后升吞（扩大样本）
q2 = defaultdict(lambda: [0,0,0.0])

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
    hrs = [to_f(rows[i][26]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]
    月策带日s = [rows[i][50].strip() if len(rows[i])>50 else '' for i in range(n)]
    zps = [rows[i][10].strip() if len(rows[i])>10 else '' for i in range(n)]

    # ===== 1. DXAB负转正后特权（按DXEF直接分） =====
    for i in range(1, n):
        hx_prev, zj_prev, dirch_prev, val_prev = dxabs[i-1]
        hx, zj, dirch, val = dxabs[i]
        if val is None or val_prev is None: continue
        if not (val_prev < 0 and val > 0): continue
        for j in range(i, n):
            za = zas[j]; zf = zfs[j]
            if za is None or zf is None: continue
            if za <= 1 and zf < 0:
                hr = hrs[j]; ze = zes[j]
                if hr is None: break
                if hr < -50 or hr > 50: break
                ef = extract_ef(月策带日s[j])
                if ef in ('金','银','唏'):
                    case = 'DXEF>0(金银唏)'
                elif ef in ('嘘','屎','尿'):
                    case = 'DXEF≤0(嘘屎尿)'
                else:
                    case = 'DXEF未知'
                q1[case][0]+=1; q1[case][1]+= (1 if hr>=3 else 0); q1[case][2]+=hr
                break

    # ===== 2. DJA之上跌连后升吞（扩大样本） =====
    for i in range(n):
        za = zas[i]; hr = hrs[i]
        if za is None or hr is None: continue
        if hr < -50 or hr > 50: continue
        if za > 0 and '升.尾吞' in zps[i]:
            prev_zp = zps[i-1] if i>0 else ''
            prev_za = zas[i-1] if i>0 else None
            # DJA之上（prev_za>0），前跌排
            if '跌' in prev_zp and prev_za is not None and prev_za > 0:
                if '跌.尾连' in prev_zp:
                    q2['DJA之上+跌连后升吞'][0]+=1; q2['DJA之上+跌连后升吞'][1]+= (1 if hr>=3 else 0); q2['DJA之上+跌连后升吞'][2]+=hr
                else:
                    q2['DJA之上+其他跌后升吞'][0]+=1; q2['DJA之上+其他跌后升吞'][1]+= (1 if hr>=3 else 0); q2['DJA之上+其他跌后升吞'][2]+=hr

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    print(f'{"类别":<24} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*55)
    for k in keys:
        if k in d:
            s = d[k]
            if s[0] >= 100:
                print(f'{k:<24} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
    print()

show(q1, '1. DXAB负转正后阴柱回调至DJA附近（按DXEF直接分）', ['DXEF>0(金银唏)','DXEF≤0(嘘屎尿)','DXEF未知'])
show(q2, '2. DJA之上跌连后升吞', ['DJA之上+跌连后升吞','DJA之上+其他跌后升吞'])