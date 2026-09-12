# -*- coding: utf-8 -*-
"""
验证BSHA对DXZC/DXAB的交叉关系（高波池）
====================================================
用户假设：刚DXAB正交时偏离较小，随后逐步放大，直到波段顶部。

验证：
1. DXAB>0（BTAB>0）时，BSHA（偏离DJA）随BTAB值增大的演变
2. DXAB<0（BTAB<0）时，BSHA随BTAB值减小的演变
3. DXZC>0时，BSHA随日ZC值增大的演变
4. BSHA在波段顶部（日ZC转负前）是否最大
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
# 1. DXAB>0时，BSHA随BTAB值演变
bsha_btab_pos = defaultdict(lambda: [0,0.0])  # key: BTAB值 -> [n, sum_bsha]
# 2. DXAB<0时，BSHA随BTAB值演变
bsha_btab_neg = defaultdict(lambda: [0,0.0])
# 3. DXZC>0时，BSHA随日ZC值演变
bsha_zc = defaultdict(lambda: [0,0.0])
# 4. 波段顶部（日ZC转负前一天）的BSHA vs 波段内其他天
bsha_top = defaultdict(lambda: [0,0.0])  # key: 位置 -> [n, sum_bsha]

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
    bshas = [to_f(rows[i][21]) for i in range(n)]

    # ===== 1/2. BSHA随BTAB值演变 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None: continue
        bsha = bshas[i]
        if bsha is None: continue
        if val > 0:
            # 分段：1-5, 6-10, 11-15, 16-20, 21-30, 31-50, >50
            if val <= 5: k = '1-5'
            elif val <= 10: k = '6-10'
            elif val <= 15: k = '11-15'
            elif val <= 20: k = '16-20'
            elif val <= 30: k = '21-30'
            elif val <= 50: k = '31-50'
            else: k = '>50'
            bsha_btab_pos[k][0]+=1; bsha_btab_pos[k][1]+=bsha
        elif val < 0:
            av = -val
            if av <= 5: k = '1-5'
            elif av <= 10: k = '6-10'
            elif av <= 15: k = '11-15'
            elif av <= 20: k = '16-20'
            elif av <= 30: k = '21-30'
            elif av <= 50: k = '31-50'
            else: k = '>50'
            bsha_btab_neg[k][0]+=1; bsha_btab_neg[k][1]+=bsha

    # ===== 3. BSHA随日ZC值演变 =====
    for i in range(n):
        zc = zcs[i]
        bsha = bshas[i]
        if zc is None or bsha is None: continue
        if zc > 0:
            if zc <= 5: k = 'ZC1-5'
            elif zc <= 10: k = 'ZC6-10'
            elif zc <= 20: k = 'ZC11-20'
            elif zc <= 30: k = 'ZC21-30'
            else: k = 'ZC>30'
            bsha_zc[k][0]+=1; bsha_zc[k][1]+=bsha

    # ===== 4. 波段顶部BSHA =====
    # 找DXZC>0区域，比较顶部（最后一天）vs 其他天
    i = 0
    while i < n:
        zc = zcs[i]
        if zc is None or zc <= 0:
            i += 1; continue
        start = i
        while i < n and zcs[i] is not None and zcs[i] > 0:
            i += 1
        end = i  # 区域 [start, end)
        if end - start < 3: continue
        # 顶部 = 最后一天（end-1），其他 = 中间
        for j in range(start, end):
            bsha = bshas[j]
            if bsha is None: continue
            if j == end - 1:
                bsha_top['顶部(最后天)'][0]+=1; bsha_top['顶部(最后天)'][1]+=bsha
            elif j == start:
                bsha_top['底部(首天)'][0]+=1; bsha_top['底部(首天)'][1]+=bsha
            else:
                bsha_top['中间'][0]+=1; bsha_top['中间'][1]+=bsha

print(f'高波池文件: {files_core}')
print()

# ===== 1输出 =====
print('='*75)
print('【1】DXAB>0时，BSHA（偏离DJA）随BTAB值演变')
print('='*75)
print(f'{"BTAB段":<10} {"n":>10} {"平均BSHA":>10}')
print('-'*35)
for k in ['1-5','6-10','11-15','16-20','21-30','31-50','>50']:
    if k in bsha_btab_pos:
        s = bsha_btab_pos[k]
        if s[0] >= 100:
            print(f'{k:<10} {s[0]:>10,} {s[1]/s[0]:>9.2f}%')
print()

# ===== 2输出 =====
print('='*75)
print('【2】DXAB<0时，BSHA随BTAB值演变')
print('='*75)
print(f'{"BTAB段":<10} {"n":>10} {"平均BSHA":>10}')
print('-'*35)
for k in ['1-5','6-10','11-15','16-20','21-30','31-50','>50']:
    if k in bsha_btab_neg:
        s = bsha_btab_neg[k]
        if s[0] >= 100:
            print(f'{k:<10} {s[0]:>10,} {s[1]/s[0]:>9.2f}%')
print()

# ===== 3输出 =====
print('='*75)
print('【3】DXZC>0时，BSHA随日ZC值演变')
print('='*75)
print(f'{"日ZC段":<10} {"n":>10} {"平均BSHA":>10}')
print('-'*35)
for k in ['ZC1-5','ZC6-10','ZC11-20','ZC21-30','ZC>30']:
    if k in bsha_zc:
        s = bsha_zc[k]
        if s[0] >= 100:
            print(f'{k:<10} {s[0]:>10,} {s[1]/s[0]:>9.2f}%')
print()

# ===== 4输出 =====
print('='*75)
print('【4】波段顶部BSHA（DXZC>0区域）')
print('='*75)
print(f'{"位置":<12} {"n":>10} {"平均BSHA":>10}')
print('-'*35)
for k in ['底部(首天)','中间','顶部(最后天)']:
    if k in bsha_top:
        s = bsha_top[k]
        if s[0] >= 100:
            print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]:>9.2f}%')
print()