# -*- coding: utf-8 -*-
"""
戊(ZA<0) / 丁(ZA<0) 参与价值分析
====================================================
问题：戊(ZA<0)/丁(ZA<0) 是不是大多数都会转为DXZC<0？是不是没有任何参与价值？

输出：
  ① P(≥3%)（次日冲高率）——参与价值
  ② 次日转移方向（是否转DXZC<0 / 是否转正交类）
  ③ 与基线对比

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

# 当前行统计: key -> [n, hr3, sum_hr]
cur_stats = defaultdict(lambda: [0, 0, 0.0])
# 次日转移: (cur_key, nxt_key) -> count
trans = defaultdict(int)
# 次日DXZC符号: (cur_key, nxt_zc_sign) -> count
trans_zc = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    prev_key = None
    prev_za = None
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 26: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                hr = to_f(row[26])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                # 当前行统计（全样本）
                cur_stats[key][0] += 1
                cur_stats[key][1] += (1 if hr >= 3 else 0)
                cur_stats[key][2] += hr
                # 次日转移
                if prev_key is not None:
                    trans[(prev_key, key)] += 1
                    if zc is not None:
                        trans_zc[(prev_key, 'ZC>0' if zc > 0 else 'ZC<=0')] += 1
                prev_key = key
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

# 目标类型
targets = ['戊(ZA<0)', '丁(ZA<0)']
# 正交类（好机会）
正交 = ['甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '己(ZA>0)', '戊(ZA>0)']

print('=' * 70)
print('① 参与价值：P(≥3%)（次日冲高率，全样本）')
print('=' * 70)
print(f'{"护型":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
for k in targets + ['甲(ZA>0)', '乙(ZA>0)']:
    s = cur_stats[k]
    if s[0] > 0:
        print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 70)
print('② 次日转移方向（戊ZA<0 / 丁ZA<0）')
print('=' * 70)
for k in targets:
    total = sum(trans[(k, nk)] for nk in 正交) + sum(trans[(k, nk)] for nk in targets)
    # 收集所有转移
    all_trans = {nk: c for (ck, nk), c in trans.items() if ck == k}
    tot = sum(all_trans.values())
    print(f'\n--- {k}（次日转移，n={tot:,}）---')
    for nk, c in sorted(all_trans.items(), key=lambda x: -x[1]):
        print(f'  {nk:<12} {c:>10,}  {c/tot*100:>6.2f}%')

print()
print('=' * 70)
print('③ 次日DXZC符号（戊ZA<0 / 丁ZA<0 是否转DXZC<0）')
print('=' * 70)
for k in targets:
    zc_pos = trans_zc[(k, 'ZC>0')]
    zc_neg = trans_zc[(k, 'ZC<=0')]
    tot = zc_pos + zc_neg
    if tot > 0:
        print(f'  {k:<12} 次日ZC>0: {zc_pos:>10,} ({zc_pos/tot*100:.2f}%)  次日ZC<=0: {zc_neg:>10,} ({zc_neg/tot*100:.2f}%)')
