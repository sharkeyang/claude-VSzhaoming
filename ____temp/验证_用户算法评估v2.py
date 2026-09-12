# -*- coding: utf-8 -*-
"""
用户算法评估 v2 + 新增问题（高波池）
====================================================
DXAB正交 = DXAB>0 = BTAB>0 = JA(EMA5) > JB(EMA12)

算法：DJC丘(DXZC>0) → DXAB广义正交(DXAB>0+广义护型) → DJA丘(日ZA>0/日等型)

新增问题：
A. DXAB>0后快速负交(≤5天转负)出现在DXEF/DXCD哪个区域？
B. 短期反复交叉的统计特征，是否大多在DXZC<0或DXCD<0？
C. 只做DXZC>0 + 剔除(DXZE<0且DXCD=忠) + 只做DXAB广义正交：胜率/盈利率/年化
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
# 算法分层
stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    s = stats[key]; s[0]+=1
    if hr>=3: s[1]+=1
    s[2]+=hr

# 新增A: DXAB>0后快速负交(≤5天)的DXEF/DXCD区域
qA = defaultdict(lambda: [0,0])
# 新增B: 快速负交 vs 非快速负交 的DXZC/DXCD分布
qB = defaultdict(lambda: [0,0])
# 新增C: 胜率/盈利率/年化
# 胜率 = 次日高幅≥3%概率；盈利率 = 次日高幅均值；年化需按持有期估算
qC = defaultdict(lambda: [0,0,0.0])

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
    zes = [to_f(rows[i][15]) for i in range(n)]
    hrs = [to_f(rows[i][26]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]
    # DXEF (16), DXCD (8)
    dxefs = [rows[i][16].strip() if len(rows[i])>16 else '' for i in range(n)]
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    中符串s = [rows[i][35].strip() if len(rows[i])>35 else '' for i in range(n)]

    # ===== 算法分层 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        hr = hrs[i]
        za = zas[i]; zc = zcs[i]
        if hr is None or za is None or zc is None: continue
        if hr < -50 or hr > 50: continue
        # 第1层 DJC丘
        if zc > 0:
            add('L1_DJC丘', hr)
            # 第2层 DXAB广义正交（DXAB>0 + 广义护型）
            if val is not None and val > 0 and is_广义(hx, za):
                add('L2_DXAB广义正交', hr)
                # 第3层 DJA丘（日ZA>0）
                if za > 0:
                    add('L3_DJA丘', hr)
                    末符 = 中符串s[i][-1] if 中符串s[i] else ''
                    等型 = calc_等型(za, 末符)
                    if 等型:
                        add(f'L3_{等型}', hr)
                else:
                    add('L3_非DJA丘', hr)
            else:
                add('L2_非DXAB广义', hr)
        else:
            add('L0_非DJC丘', hr)

    # ===== 新增A: DXAB>0后快速负交的DXEF/DXCD区域 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None or val <= 0: continue
        # 检查后续5天内是否转负
        quick_neg = False
        for k in range(1, 6):
            if i+k >= n: break
            hx2, zj2, dirch2, val2 = dxabs[i+k]
            if val2 is not None and val2 < 0:
                quick_neg = True
                break
        if quick_neg:
            # 记录当前DXEF/DXCD
            ef = dxefs[i]; cd = dxcds[i]
            qA[f'{ef}|{cd}'][0]+=1; qA[f'{ef}|{cd}'][1]+=1
            # 记录DXZC/DXCD符号
            zc = zcs[i]
            if zc is not None:
                if zc > 0: qB['快速负交|ZC>0'][0]+=1
                else: qB['快速负交|ZC<=0'][0]+=1
            if cd in ('下','忑'): qB['快速负交|CD<0'][0]+=1
            elif cd in ('上','忐','忠'): qB['快速负交|CD>0'][0]+=1
            else: qB['快速负交|CD=中'][0]+=1
        else:
            zc = zcs[i]
            if zc is not None:
                if zc > 0: qB['非快速负交|ZC>0'][0]+=1
                else: qB['非快速负交|ZC<=0'][0]+=1
            cd = dxcds[i]
            if cd in ('下','忑'): qB['非快速负交|CD<0'][0]+=1
            elif cd in ('上','忐','忠'): qB['非快速负交|CD>0'][0]+=1
            else: qB['非快速负交|CD=中'][0]+=1

    # ===== 新增C: 胜率/盈利率 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        hr = hrs[i]
        za = zas[i]; zc = zcs[i]; ze = zes[i]
        if hr is None or za is None or zc is None or ze is None: continue
        if hr < -50 or hr > 50: continue
        cd = dxcds[i]
        # 条件：DXZC>0 + 剔除(DXZE<0且DXCD=忠) + DXAB广义正交
        if zc > 0 and not (ze < 0 and cd == '忠') and val is not None and val > 0 and is_广义(hx, za):
            qC['C_全条件'][0]+=1; qC['C_全条件'][1]+= (1 if hr>=3 else 0); qC['C_全条件'][2]+=hr
        # 对照：只DXZC>0
        if zc > 0:
            qC['C_仅DJC丘'][0]+=1; qC['C_仅DJC丘'][1]+= (1 if hr>=3 else 0); qC['C_仅DJC丘'][2]+=hr
        # 对照：DXZC>0 + DXAB>0
        if zc > 0 and val is not None and val > 0:
            qC['C_DJC+DXAB>0'][0]+=1; qC['C_DJC+DXAB>0'][1]+= (1 if hr>=3 else 0); qC['C_DJC+DXAB>0'][2]+=hr
        # 对照：DXZC>0 + 剔除忠
        if zc > 0 and not (ze < 0 and cd == '忠'):
            qC['C_DJC+剔忠'][0]+=1; qC['C_DJC+剔忠'][1]+= (1 if hr>=3 else 0); qC['C_DJC+剔忠'][2]+=hr

print(f'高波池文件: {files_core}')
print()

# ===== 算法分层输出 =====
print('='*75)
print('【算法分层】DJC丘 → DXAB广义正交 → DJA丘')
print('='*75)
def show(label, key):
    s = stats[key]
    if s[0] == 0: return
    print(f'{label:<22} n={s[0]:>12,}  P(≥3%)={s[1]/s[0]*100:>6.2f}%  均高幅={s[2]/s[0]:>5.2f}%')
show('L0_非DJC丘', 'L0_非DJC丘')
show('L1_DJC丘(DXZC>0)', 'L1_DJC丘')
show('L2_DXAB广义正交', 'L2_DXAB广义正交')
show('L2_非DXAB广义', 'L2_非DXAB广义')
show('L3_DJA丘(日ZA>0)', 'L3_DJA丘')
show('L3_非DJA丘', 'L3_非DJA丘')
for 等 in ['等1','等2','等3','等4']:
    show(f'  L3+{等}', f'L3_{等}')
print()

# 增量
s0 = stats['L0_非DJC丘']; s1 = stats['L1_DJC丘']; s2 = stats['L2_DXAB广义正交']; s3 = stats['L3_DJA丘']
print('='*75)
print('【增量贡献】')
print('='*75)
print(f'非DJC丘基线: P(≥3%)={s0[1]/s0[0]*100:.2f}%')
print(f'DJC丘:       P(≥3%)={s1[1]/s1[0]*100:.2f}%  (+{s1[1]/s1[0]*100-s0[1]/s0[0]*100:.2f}pp)')
print(f'DXAB广义正交: P(≥3%)={s2[1]/s2[0]*100:.2f}%  (+{s2[1]/s2[0]*100-s1[1]/s1[0]*100:.2f}pp vs DJC丘)')
print(f'DJA丘:       P(≥3%)={s3[1]/s3[0]*100:.2f}%  (+{s3[1]/s3[0]*100-s2[1]/s2[0]*100:.2f}pp vs DXAB广义)')
print()

# ===== 新增A输出 =====
print('='*75)
print('【新增A】DXAB>0后快速负交(≤5天)的DXEF/DXCD区域分布')
print('='*75)
print(f'{"DXEF":<4} {"DXCD":<4} {"快速负交样本":>12} {"占比":>8}')
print('-'*40)
total_A = sum(v[0] for v in qA.values())
for ef in ['金','银','唏','嘘','屎','尿']:
    for cd in ['上','忐','忠','中','忑','下']:
        key = f'{ef}|{cd}'
        if key in qA:
            s = qA[key]
            if s[0] >= 100:
                print(f'{ef:<4} {cd:<4} {s[0]:>12,} {s[0]/total_A*100:>7.2f}%')
print(f'快速负交总样本: {total_A:,}')
print()

# ===== 新增B输出 =====
print('='*75)
print('【新增B】快速负交 vs 非快速负交 的DXZC/DXCD分布')
print('='*75)
for k in ['快速负交|ZC>0','快速负交|ZC<=0','非快速负交|ZC>0','非快速负交|ZC<=0']:
    if k in qB:
        s = qB[k]
        print(f'{k:<20} n={s[0]:>12,}')
print()
for k in ['快速负交|CD>0','快速负交|CD<0','快速负交|CD=中','非快速负交|CD>0','非快速负交|CD<0','非快速负交|CD=中']:
    if k in qB:
        s = qB[k]
        print(f'{k:<20} n={s[0]:>12,}')
print()

# ===== 新增C输出 =====
print('='*75)
print('【新增C】胜率/盈利率（次日高幅口径）')
print('='*75)
print(f'{"条件":<20} {"n":>12} {"胜率(≥3%)":>10} {"均高幅":>8}')
print('-'*55)
for k in ['C_仅DJC丘','C_DJC+DXAB>0','C_DJC+剔忠','C_全条件']:
    if k in qC:
        s = qC[k]
        if s[0] >= 100:
            print(f'{k:<20} {s[0]:>12,} {s[1]/s[0]*100:>9.2f}% {s[2]/s[0]:>7.2f}%')
print()