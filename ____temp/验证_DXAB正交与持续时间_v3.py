# -*- coding: utf-8 -*-
"""
DXAB正交/持续时间/阴柱特权 综合分析 v3（高波池）
====================================================
DXAB数值 = BTAB = JA(EMA5) vs JB(EMA12) 交叉天数（衍生交叉天数）
DXAB正交 = DXAB>0 = BTAB>0 = JA在JB之上（短期均线多头）
DXAB<0 = BTAB<0 = JA在JB之下

回答用户问题：
1. DXAB初期阴柱特权：DXAB>0初期(BTAB值1-4)遇阴柱，次日冲高率？
2. DXAB正交后短期转负概率：BTAB>0后N天内转负(BTAB<0)的概率
3. DXAB>0持续时间统计规律
4. DXAB<0持续时间统计规律
5. DXAB正交是否可作为机会（次日冲高率 vs 基线）
6. DXZC>0与DXAB正交交叉统计
7. 一个DXZC>0区域一般有多少次DXAB交叉(BTAB穿越0)

磁盘CSV列序：0日期 5涨幅 9DXAB 10柱排 13日ZA 14日ZC 15日ZE 16日BTEF 26次日高幅 28上身
DXAB格式：a甲↗上1.I → 位1护型代码 位2汉字 位3正交符号 位4层护级AB 位5BTAB数值 . 位6BTZA关系
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
    """返回 (护型, 正交符号, 方向字符, BTAB数值)"""
    if len(dxab) < 3: return ('','','',None)
    hx = hxmap.get(dxab[0], '')
    zj = dxab[2]
    dirch = dxab[3] if len(dxab) > 3 else ''
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    val = int(m.group(1)) if m else None
    return (hx, zj, dirch, val)

# ============ 统计容器 ============
# 问题1: DXAB初期阴柱特权（BTAB>0初期，当前阴柱 vs 阳柱）
q1 = defaultdict(lambda: [0,0,0.0])
# 问题2: BTAB>0后转负
q2 = defaultdict(lambda: [0,0])
# 问题3/4: BTAB>0 / <0 持续时间
dur_pos = defaultdict(lambda: [0,0.0])
dur_neg = defaultdict(lambda: [0,0.0])
dur_pos_all = [0,0.0]
dur_neg_all = [0,0.0]
# 问题5: DXAB>0次日冲高率
q5 = defaultdict(lambda: [0,0,0.0])
# 问题6: DXZC>0区域内BTAB交叉次数
q6 = defaultdict(lambda: [0,0.0])
# 问题7: BTAB>0后首次转负天数
q7 = defaultdict(lambda: [0,0.0])
# 问题8: DXAB>0 vs DXAB<0 次日冲高率
q8 = defaultdict(lambda: [0,0,0.0])
# 问题9: DXZC>0 × DXAB>0 交叉
q9 = defaultdict(lambda: [0,0,0.0])

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
            rows = [row for row in r]
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    dxabs = [parse_dxab(rows[i][9].strip()) for i in range(n)]
    zas = [to_f(rows[i][13]) for i in range(n)]
    zcs = [to_f(rows[i][14]) for i in range(n)]
    hrs = [to_f(rows[i][26]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]

    # ===== 问题1: DXAB初期阴柱特权 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        hr = hrs[i]
        zf = zfs[i]
        if hr is None or zf is None: continue
        if hr < -50 or hr > 50: continue
        if val is None: continue
        if val > 0:
            if val <= 4 and zf < 0:
                q1[f'{hx}|初1-4|阴'][0]+=1; q1[f'{hx}|初1-4|阴'][1]+= (1 if hr>=3 else 0); q1[f'{hx}|初1-4|阴'][2]+=hr
            if val <= 4 and zf >= 0:
                q1[f'{hx}|初1-4|阳'][0]+=1; q1[f'{hx}|初1-4|阳'][1]+= (1 if hr>=3 else 0); q1[f'{hx}|初1-4|阳'][2]+=hr
            if val > 4 and zf < 0:
                q1[f'{hx}|后>4|阴'][0]+=1; q1[f'{hx}|后>4|阴'][1]+= (1 if hr>=3 else 0); q1[f'{hx}|后>4|阴'][2]+=hr
            if val > 4 and zf >= 0:
                q1[f'{hx}|后>4|阳'][0]+=1; q1[f'{hx}|后>4|阳'][1]+= (1 if hr>=3 else 0); q1[f'{hx}|后>4|阳'][2]+=hr

    # ===== 问题2/5/7/8/9: DXAB>0 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        hr = hrs[i]
        zc = zcs[i]
        za = zas[i]
        if hr is None: continue
        if hr < -50 or hr > 50: continue
        if val is None: continue
        # 问题8: DXAB>0 vs <0
        if val > 0:
            q8[f'{hx}|DXAB>0'][0]+=1; q8[f'{hx}|DXAB>0'][1]+= (1 if hr>=3 else 0); q8[f'{hx}|DXAB>0'][2]+=hr
        elif val < 0:
            q8[f'{hx}|DXAB<0'][0]+=1; q8[f'{hx}|DXAB<0'][1]+= (1 if hr>=3 else 0); q8[f'{hx}|DXAB<0'][2]+=hr
        # 问题9: DXZC>0 × DXAB>0
        if zc is not None and zc > 0:
            if val > 0:
                q9['ZC>0|DXAB>0'][0]+=1; q9['ZC>0|DXAB>0'][1]+= (1 if hr>=3 else 0); q9['ZC>0|DXAB>0'][2]+=hr
            else:
                q9['ZC>0|DXAB<=0'][0]+=1; q9['ZC>0|DXAB<=0'][1]+= (1 if hr>=3 else 0); q9['ZC>0|DXAB<=0'][2]+=hr
        else:
            if val > 0:
                q9['ZC<=0|DXAB>0'][0]+=1; q9['ZC<=0|DXAB>0'][1]+= (1 if hr>=3 else 0); q9['ZC<=0|DXAB>0'][2]+=hr
            else:
                q9['ZC<=0|DXAB<=0'][0]+=1; q9['ZC<=0|DXAB<=0'][1]+= (1 if hr>=3 else 0); q9['ZC<=0|DXAB<=0'][2]+=hr
        # 问题5: DXAB>0次日冲高率（正交是否可作为机会）
        if val > 0:
            zc_key = 'ZC>0' if (zc is not None and zc > 0) else 'ZC<=0'
            q5[f'{hx}|{zc_key}'][0]+=1; q5[f'{hx}|{zc_key}'][1]+= (1 if hr>=3 else 0); q5[f'{hx}|{zc_key}'][2]+=hr
            # 问题2/7: DXAB>0后N天内转负
            for N in [1,2,3,5,7,10]:
                turned = False
                for k in range(1, N+1):
                    if i+k >= n: break
                    hx2, zj2, dirch2, val2 = dxabs[i+k]
                    if val2 is not None and val2 < 0:
                        turned = True
                        break
                if turned:
                    q2[f'{hx}|{N}天'][0]+=1; q2[f'{hx}|{N}天'][1]+=1
                else:
                    q2[f'{hx}|{N}天'][0]+=1
            # 问题7: 首次转负天数
            first_neg = None
            for k in range(1, 15):
                if i+k >= n: break
                hx2, zj2, dirch2, val2 = dxabs[i+k]
                if val2 is not None and val2 < 0:
                    first_neg = k
                    break
            if first_neg is not None:
                q7[f'{hx}'][0]+=1; q7[f'{hx}'][1]+=first_neg

    # ===== 问题3/4: BTAB>0 / <0 持续时间 =====
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
            dur_pos[hx][0]+=1; dur_pos[hx][1]+=length
            dur_pos_all[0]+=1; dur_pos_all[1]+=length
        elif val < 0:
            start = i
            while i < n:
                hx2, zj2, dirch2, val2 = dxabs[i]
                if val2 is None or val2 >= 0: break
                i += 1
            length = i - start
            dur_neg[hx][0]+=1; dur_neg[hx][1]+=length
            dur_neg_all[0]+=1; dur_neg_all[1]+=length
        else:
            i += 1

    # ===== 问题6: DXZC>0区域内BTAB交叉次数 =====
    i = 0
    while i < n:
        zc = zcs[i]
        if zc is None or zc <= 0:
            i += 1; continue
        start = i
        while i < n and zcs[i] is not None and zcs[i] > 0:
            i += 1
        end = i
        crossings = 0
        prev_sign = None
        for j in range(start, end):
            hx2, zj2, dirch2, val2 = dxabs[j]
            if val2 is None: continue
            sign = 1 if val2 > 0 else (-1 if val2 < 0 else 0)
            if prev_sign is not None and sign != 0 and prev_sign != 0 and sign != prev_sign:
                crossings += 1
            if sign != 0:
                prev_sign = sign
        hx_count = defaultdict(int)
        for j in range(start, end):
            hx2, zj2, dirch2, val2 = dxabs[j]
            if hx2: hx_count[hx2]+=1
        if hx_count:
            main_hx = max(hx_count, key=hx_count.get)
            q6[main_hx][0]+=1; q6[main_hx][1]+=crossings

print(f'高波池文件: {files_core}')
print()

# ===== 问题1输出 =====
print('='*75)
print('【问题1】DXAB初期阴柱特权（DXAB>0，当前阴柱 vs 阳柱，次日冲高率）')
print('='*75)
print(f'{"护型":<4} {"阶段":<8} {"柱":<4} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*55)
for hx in ['甲','乙','己','戊','丙','丁']:
    for stage in ['初1-4','后>4']:
        for zf_key in ['阴','阳']:
            key = f'{hx}|{stage}|{zf_key}'
            if key in q1:
                s = q1[key]
                if s[0] >= 500:
                    print(f'{hx:<4} {stage:<8} {zf_key:<4} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 问题2输出 =====
print('='*75)
print('【问题2】DXAB>0后N天内转负(BTAB<0)的概率')
print('='*75)
print(f'{"护型":<4} {"N天":<6} {"n":>10} {"转负率":>8}')
print('-'*40)
for hx in ['甲','乙','己','戊','丙','丁']:
    for N in [1,2,3,5,7,10]:
        key = f'{hx}|{N}天'
        if key in q2:
            s = q2[key]
            if s[0] >= 100:
                print(f'{hx:<4} {N:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')
    print('-'*40)
print()

# ===== 问题3/4输出 =====
print('='*75)
print('【问题3/4】DXAB>0 与 DXAB<0 持续时间（BTAB=JA vs JB交叉天数）')
print('='*75)
print(f'{"护型":<4} {"方向":<6} {"run数":>10} {"平均天数":>10}')
print('-'*45)
for hx in ['甲','乙','己','戊','丙','丁']:
    if hx in dur_pos:
        s = dur_pos[hx]
        print(f'{hx:<4} {"正>0":<6} {s[0]:>10,} {s[1]/s[0]:>9.2f}')
    if hx in dur_neg:
        s = dur_neg[hx]
        print(f'{hx:<4} {"负<0":<6} {s[0]:>10,} {s[1]/s[0]:>9.2f}')
print(f'{"全部":<4} {"正>0":<6} {dur_pos_all[0]:>10,} {dur_pos_all[1]/dur_pos_all[0]:>9.2f}')
print(f'{"全部":<4} {"负<0":<6} {dur_neg_all[0]:>10,} {dur_neg_all[1]/dur_neg_all[0]:>9.2f}')
print()

# ===== 问题5输出 =====
print('='*75)
print('【问题5】DXAB>0次日冲高率（正交是否可作为机会）')
print('='*75)
print(f'{"护型":<4} {"ZC方向":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*50)
for hx in ['甲','乙','己','戊','丙','丁']:
    for zc_key in ['ZC>0','ZC<=0']:
        key = f'{hx}|{zc_key}'
        if key in q5:
            s = q5[key]
            if s[0] >= 100:
                print(f'{hx:<4} {zc_key:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 问题6输出 =====
print('='*75)
print('【问题6】DXZC>0区域内DXAB交叉次数（主护型）')
print('='*75)
print(f'{"主护型":<6} {"区域数":>10} {"总交叉":>10} {"平均交叉/区域":>14}')
print('-'*50)
for hx in ['甲','乙','己','戊','丙','丁']:
    if hx in q6:
        s = q6[hx]
        if s[0] >= 100:
            print(f'{hx:<6} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]:>13.2f}')
print()

# ===== 问题7输出 =====
print('='*75)
print('【问题7】DXAB>0后首次转负的平均天数')
print('='*75)
print(f'{"护型":<4} {"样本":>10} {"平均转负天数":>14}')
print('-'*40)
for hx in ['甲','乙','己','戊','丙','丁']:
    if hx in q7:
        s = q7[hx]
        if s[0] >= 100:
            print(f'{hx:<4} {s[0]:>10,} {s[1]/s[0]:>13.2f}')
print()

# ===== 问题8输出 =====
print('='*75)
print('【问题8】DXAB>0 vs DXAB<0 次日冲高率')
print('='*75)
print(f'{"护型":<4} {"状态":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*50)
for hx in ['甲','乙','己','戊','丙','丁']:
    for st in ['DXAB>0','DXAB<0']:
        key = f'{hx}|{st}'
        if key in q8:
            s = q8[key]
            if s[0] >= 500:
                print(f'{hx:<4} {st:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 问题9输出 =====
print('='*75)
print('【问题9】DXZC>0 × DXAB>0 交叉')
print('='*75)
print(f'{"组合":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*50)
for k in ['ZC>0|DXAB>0','ZC>0|DXAB<=0','ZC<=0|DXAB>0','ZC<=0|DXAB<=0']:
    if k in q9:
        s = q9[k]
        if s[0] >= 500:
            print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()