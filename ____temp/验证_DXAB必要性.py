# -*- coding: utf-8 -*-
"""
验证DXAB广义正交层的必要性（高波池）
====================================================
用户论点：
1. DXAB不是冗余——非广义正交很可能下破DJC；广义正交内部丙/乙(ZA<0)可提前退出，若转戊(ZA>0)/己可讨论介入
2. DXAB可以发现DXZC<0区域中可能上破DJC的情况
3. 假正交识别规则(DXAB>0+DXCD中/下/忑)的实战胜率

验证：
A. 非广义正交(戊ZA<0/丁) vs 广义正交 的下破DJC概率（次日日ZC转负）
B. 广义正交内部：丙/乙(ZA<0)的退出信号（次日转坏概率）
C. DXZC<0区域中，DXAB>0 vs DXAB<0 的上破DJC概率（次日日ZC转正）
D. 假正交(DXAB>0+DXCD中/下/忑) vs 真正交(DXAB>0+DXCD上/忐) 的实战胜率
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
    """广义正交护型：己、戊(ZA>0)、甲、乙、丙"""
    if hx == '己': return True
    if hx == '戊': return za > 0
    if hx in ('甲','乙','丙'): return True
    return False

# ============ 统计容器 ============
# A. 非广义 vs 广义 下破DJC概率
qA = defaultdict(lambda: [0,0])  # key: 类别 -> [样本, 次日ZC转负]
# B. 广义内部丙/乙(ZA<0)退出信号
qB = defaultdict(lambda: [0,0])  # key: 护型 -> [样本, 次日转坏]
# C. DXZC<0区域中DXAB>0 vs <0 上破DJC概率
qC = defaultdict(lambda: [0,0])  # key: 类别 -> [样本, 次日ZC转正]
# D. 假正交 vs 真正交 实战胜率
qD = defaultdict(lambda: [0,0,0.0])  # key: 类别 -> [样本, hr>=3, sum_hr]

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

    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        za = zas[i]; zc = zcs[i]; hr = hrs[i]
        if za is None or zc is None or hr is None: continue
        if hr < -50 or hr > 50: continue
        # 次日ZC
        nxt_zc = zcs[i+1] if i+1 < n else None
        # 次日护型
        nxt_hx = dxabs[i+1][0] if i+1 < n else ''
        nxt_za = zas[i+1] if i+1 < n else None

        # ===== A. 非广义 vs 广义 下破DJC =====
        # 当前DXZC>0，看次日是否转负（下破DJC）
        if zc > 0:
            if is_广义(hx, za):
                qA['广义|ZC>0'][0]+=1
                if nxt_zc is not None and nxt_zc <= 0: qA['广义|ZC>0'][1]+=1
            else:
                qA['非广义|ZC>0'][0]+=1
                if nxt_zc is not None and nxt_zc <= 0: qA['非广义|ZC>0'][1]+=1

        # ===== B. 广义内部丙/乙(ZA<0)退出信号 =====
        # 当前DXZC>0，看次日是否转坏（转丙/丁/戊ZA<0）
        if zc > 0 and is_广义(hx, za):
            if hx == '丙':
                qB['丙|ZC>0'][0]+=1
                if nxt_hx in ('丁','戊') or (nxt_hx=='乙' and nxt_za is not None and nxt_za<0):
                    qB['丙|ZC>0'][1]+=1
            elif hx == '乙' and za < 0:
                qB['乙ZA<0|ZC>0'][0]+=1
                if nxt_hx in ('丙','丁') or (nxt_hx=='乙' and nxt_za is not None and nxt_za<0):
                    qB['乙ZA<0|ZC>0'][1]+=1
            elif hx == '戊' and za > 0:
                qB['戊ZA>0|ZC>0'][0]+=1
                if nxt_hx in ('丙','丁') or (nxt_hx=='戊' and nxt_za is not None and nxt_za<0):
                    qB['戊ZA>0|ZC>0'][1]+=1
            elif hx == '己':
                qB['己|ZC>0'][0]+=1
                if nxt_hx in ('丙','丁') or (nxt_hx=='戊' and nxt_za is not None and nxt_za<0):
                    qB['己|ZC>0'][1]+=1

        # ===== C. DXZC<0区域中DXAB>0 vs <0 上破DJC =====
        if zc <= 0:
            if val is not None and val > 0:
                qC['DXZC<0|DXAB>0'][0]+=1
                if nxt_zc is not None and nxt_zc > 0: qC['DXZC<0|DXAB>0'][1]+=1
            else:
                qC['DXZC<0|DXAB<=0'][0]+=1
                if nxt_zc is not None and nxt_zc > 0: qC['DXZC<0|DXAB<=0'][1]+=1

        # ===== D. 假正交 vs 真正交 实战胜率 =====
        # 假正交 = DXAB>0 + DXCD中/下/忑
        # 真正交 = DXAB>0 + DXCD上/忐
        if val is not None and val > 0:
            cd = dxcds[i]
            if cd in ('中','下','忑'):
                qD['假正交|中下忑'][0]+=1; qD['假正交|中下忑'][1]+= (1 if hr>=3 else 0); qD['假正交|中下忑'][2]+=hr
            elif cd in ('上','忐'):
                qD['真正交|上忐'][0]+=1; qD['真正交|上忐'][1]+= (1 if hr>=3 else 0); qD['真正交|上忐'][2]+=hr
            elif cd == '忠':
                qD['忠|DXAB>0'][0]+=1; qD['忠|DXAB>0'][1]+= (1 if hr>=3 else 0); qD['忠|DXAB>0'][2]+=hr

print(f'高波池文件: {files_core}')
print()

# ===== A输出 =====
print('='*75)
print('【A】非广义 vs 广义 下破DJC概率（次日日ZC转负）')
print('='*75)
print(f'{"类别":<16} {"样本":>12} {"下破DJC":>10} {"下破率":>8}')
print('-'*50)
for k in ['广义|ZC>0','非广义|ZC>0']:
    if k in qA:
        s = qA[k]
        if s[0] >= 100:
            print(f'{k:<16} {s[0]:>12,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()

# ===== B输出 =====
print('='*75)
print('【B】广义内部丙/乙(ZA<0)/戊(ZA>0)/己 退出信号（次日转坏概率）')
print('='*75)
print(f'{"护型":<16} {"样本":>12} {"次日转坏":>10} {"转坏率":>8}')
print('-'*50)
for k in ['丙|ZC>0','乙ZA<0|ZC>0','戊ZA>0|ZC>0','己|ZC>0']:
    if k in qB:
        s = qB[k]
        if s[0] >= 100:
            print(f'{k:<16} {s[0]:>12,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()

# ===== C输出 =====
print('='*75)
print('【C】DXZC<0区域中DXAB>0 vs <0 上破DJC概率（次日日ZC转正）')
print('='*75)
print(f'{"类别":<20} {"样本":>12} {"上破DJC":>10} {"上破率":>8}')
print('-'*50)
for k in ['DXZC<0|DXAB>0','DXZC<0|DXAB<=0']:
    if k in qC:
        s = qC[k]
        if s[0] >= 100:
            print(f'{k:<20} {s[0]:>12,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()

# ===== D输出 =====
print('='*75)
print('【D】假正交 vs 真正交 实战胜率（次日高幅≥3%）')
print('='*75)
print(f'{"类别":<16} {"样本":>12} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*50)
for k in ['假正交|中下忑','真正交|上忐','忠|DXAB>0']:
    if k in qD:
        s = qD[k]
        if s[0] >= 100:
            print(f'{k:<16} {s[0]:>12,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()