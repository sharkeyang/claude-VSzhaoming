# -*- coding: utf-8 -*-
"""
DXAB由负转正信号在DXEF/DXCD下的重要性研究（高波池）
====================================================
DXAB由负转正 = BTAB从<0转为>0（JA=EMA5上穿JB=EMA12）

研究：
1. DXAB由负转正信号在DXEF/DXCD各分类下的重要性（次日冲高率）
2. 是否会延续（转正后N天仍保持BTAB>0的概率）
3. 是否准备介入（转正后冲高率）
4. 可能持续多少时间（转正后BTAB>0持续天数）
5. 遇见阴柱如何处理（转正后遇阴柱的冲高率）
6. 遇见DXZA<0如何处理（转正后日ZA<0的冲高率）
7. 遇见DXZB<0如何处理（用日ZA<0代理，因日ZB不可用）

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 21=BSHA, 26=次日高幅, 50=月策带日
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
    if not 月策带日: return ''
    m = re.search(r'\(([^)]+)\)', 月策带日)
    return m.group(1) if m else ''

# ============ 统计容器 ============
# 1. DXAB由负转正信号在DXEF/DXCD下的重要性
q1 = defaultdict(lambda: [0,0,0.0])  # key: EF|CD -> [n, hr>=3, sum_hr]
# 2. 转正后延续（N天后仍BTAB>0）
q2 = defaultdict(lambda: [0,0])  # key: N天 -> [转正样本, N天后仍正]
# 3. 转正后持续天数
q3 = defaultdict(lambda: [0,0.0])  # key: EF|CD -> [转正样本, 持续天数总和]
# 4. 转正后遇阴柱
q4 = defaultdict(lambda: [0,0,0.0])  # key: 阴/阳 -> [n, hr>=3, sum_hr]
# 5. 转正后遇DXZA<0
q5 = defaultdict(lambda: [0,0,0.0])  # key: ZA符号 -> [n, hr>=3, sum_hr]
# 6. 转正后遇DXZB<0（用日ZA<0代理）
q6 = defaultdict(lambda: [0,0,0.0])

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
    zfs = [to_f(rows[i][5]) for i in range(n)]
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    月策带日s = [rows[i][50].strip() if len(rows[i])>50 else '' for i in range(n)]

    # 找DXAB由负转正点（BTAB从<0转为>0）
    for i in range(1, n):
        hx_prev, zj_prev, dirch_prev, val_prev = dxabs[i-1]
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None or val_prev is None: continue
        # 由负转正：前值<0，当前>0
        if val_prev < 0 and val > 0:
            hr = hrs[i]
            zc = zcs[i]
            za = zas[i]
            zf = zfs[i]
            if hr is None or zc is None or za is None or zf is None: continue
            if hr < -50 or hr > 50: continue
            ef = extract_ef(月策带日s[i])
            cd = dxcds[i]

            # 1. DXEF/DXCD下的重要性
            q1[f'{ef}|{cd}'][0]+=1; q1[f'{ef}|{cd}'][1]+= (1 if hr>=3 else 0); q1[f'{ef}|{cd}'][2]+=hr

            # 2. 转正后延续（N天后仍BTAB>0）
            for N in [1,2,3,5,7,10]:
                still_pos = False
                for k in range(1, N+1):
                    if i+k >= n: break
                    hx2, zj2, dirch2, val2 = dxabs[i+k]
                    if val2 is not None and val2 > 0:
                        still_pos = True
                    else:
                        still_pos = False
                        break
                if still_pos:
                    q2[f'{N}天'][0]+=1; q2[f'{N}天'][1]+=1
                else:
                    q2[f'{N}天'][0]+=1

            # 3. 转正后持续天数
            dur = 0
            for k in range(i, n):
                hx2, zj2, dirch2, val2 = dxabs[k]
                if val2 is not None and val2 > 0:
                    dur += 1
                else:
                    break
            q3[f'{ef}|{cd}'][0]+=1; q3[f'{ef}|{cd}'][1]+=dur

            # 4. 转正后遇阴柱（当前阴柱）
            if zf < 0:
                q4['阴柱'][0]+=1; q4['阴柱'][1]+= (1 if hr>=3 else 0); q4['阴柱'][2]+=hr
            else:
                q4['阳柱'][0]+=1; q4['阳柱'][1]+= (1 if hr>=3 else 0); q4['阳柱'][2]+=hr

            # 5. 转正后遇DXZA<0
            if za < 0:
                q5['ZA<0'][0]+=1; q5['ZA<0'][1]+= (1 if hr>=3 else 0); q5['ZA<0'][2]+=hr
            elif za > 0:
                q5['ZA>0'][0]+=1; q5['ZA>0'][1]+= (1 if hr>=3 else 0); q5['ZA>0'][2]+=hr
            else:
                q5['ZA=0'][0]+=1; q5['ZA=0'][1]+= (1 if hr>=3 else 0); q5['ZA=0'][2]+=hr

            # 6. 转正后遇DXZB<0（用日ZA<0代理，因日ZB不可用）
            # 日ZB = 价格 vs DJB(EMA12)，介于日ZA(EMA5)和日ZC(EMA26)之间
            # 用日ZA<0 且 日ZC<0 作为"日ZB<0"的近似
            if za < 0 and zc < 0:
                q6['ZB<0(ZA<0且ZC<0)'][0]+=1; q6['ZB<0(ZA<0且ZC<0)'][1]+= (1 if hr>=3 else 0); q6['ZB<0(ZA<0且ZC<0)'][2]+=hr
            elif za > 0 and zc > 0:
                q6['ZB>0(ZA>0且ZC>0)'][0]+=1; q6['ZB>0(ZA>0且ZC>0)'][1]+= (1 if hr>=3 else 0); q6['ZB>0(ZA>0且ZC>0)'][2]+=hr

print(f'高波池文件: {files_core}')
print()

# ===== 1输出 =====
print('='*75)
print('【1】DXAB由负转正信号在DXEF/DXCD下的重要性（次日冲高率）')
print('='*75)
print(f'{"DXEF":<4} {"DXCD":<4} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*45)
for ef in ['金','银','唏','嘘','屎','尿']:
    for cd in ['上','忐','忠','中','忑','下']:
        key = f'{ef}|{cd}'
        if key in q1:
            s = q1[key]
            if s[0] >= 100:
                print(f'{ef:<4} {cd:<4} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 2输出 =====
print('='*75)
print('【2】DXAB由负转正后延续（N天后仍BTAB>0）')
print('='*75)
print(f'{"N天":<6} {"转正样本":>10} {"仍正":>10} {"延续率":>8}')
print('-'*40)
for N in [1,2,3,5,7,10]:
    if f'{N}天' in q2:
        s = q2[f'{N}天']
        if s[0] >= 100:
            print(f'{N}天    {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()

# ===== 3输出 =====
print('='*75)
print('【3】DXAB由负转正后持续天数 × DXEF/DXCD')
print('='*75)
print(f'{"DXEF":<4} {"DXCD":<4} {"转正样本":>10} {"平均持续":>10}')
print('-'*40)
for ef in ['金','银','唏','嘘','屎','尿']:
    for cd in ['上','忐','忠','中','忑','下']:
        key = f'{ef}|{cd}'
        if key in q3:
            s = q3[key]
            if s[0] >= 100:
                print(f'{ef:<4} {cd:<4} {s[0]:>10,} {s[1]/s[0]:>9.2f}天')
print()

# ===== 4输出 =====
print('='*75)
print('【4】DXAB由负转正后遇阴柱/阳柱')
print('='*75)
print(f'{"柱":<6} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*40)
for k in ['阴柱','阳柱']:
    if k in q4:
        s = q4[k]
        if s[0] >= 100:
            print(f'{k:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 5输出 =====
print('='*75)
print('【5】DXAB由负转正后遇DXZA<0')
print('='*75)
print(f'{"日ZA":<6} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*40)
for k in ['ZA<0','ZA>0','ZA=0']:
    if k in q5:
        s = q5[k]
        if s[0] >= 100:
            print(f'{k:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 6输出 =====
print('='*75)
print('【6】DXAB由负转正后遇DXZB<0（用日ZA/日ZC代理）')
print('='*75)
print(f'{"类别":<20} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*45)
for k in ['ZB<0(ZA<0且ZC<0)','ZB>0(ZA>0且ZC>0)']:
    if k in q6:
        s = q6[k]
        if s[0] >= 100:
            print(f'{k:<20} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()