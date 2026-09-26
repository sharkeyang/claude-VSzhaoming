# -*- coding: utf-8 -*-
"""
乙(ZA<0) 转移概率 vs DTAB（日BTAB = DXAB字符串中护级后的持续天数）
====================================================
问题：乙(ZA<0) 转乙(ZA>0)/维持乙(ZA<0)/转丙 概率是否与 DTAB 相关？
假设：DTAB 较小时转乙(ZA>0)概率大，DTAB 较大时更容易转丙。

正确逻辑：前一柱是乙(ZA<0)，看当前柱的护型 = 转移方向。
DTAB 取前一柱 DXAB 字符串的持续天数。
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

def to_f(v):
    try: return float(v)
    except: return None

stats = defaultdict(int)
tot = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    prev_dxab = None
    prev_za = None
    prev_dtab = None
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 64: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                dtab = to_f(row[64])  # DTAB[64]（JA vs JB交叉天数，2026-09-24新增导出）
                if za is None: continue
                # 前一柱是乙(ZA<0) → 看当前柱转移方向
                if prev_dxab is not None and prev_dxab.startswith('b乙') and prev_za is not None and prev_za < 0 and prev_dtab is not None:
                    dtab = prev_dtab
                    if dtab is not None:
                        if dxab.startswith('b乙') and za > 0:
                            nxt = '转乙ZA>0'
                        elif dxab.startswith('b乙') and za < 0:
                            nxt = '维持乙ZA<0'
                        elif dxab.startswith('c丙'):
                            nxt = '转丙'
                        elif dxab.startswith('z丁'):
                            nxt = '转丁'
                        else:
                            nxt = '其他'
                        if dtab <= 2: bucket = 'DTAB≤2'
                        elif dtab <= 5: bucket = 'DTAB3-5'
                        elif dtab <= 10: bucket = 'DTAB6-10'
                        elif dtab <= 20: bucket = 'DTAB11-20'
                        else: bucket = 'DTAB>20'
                        stats[(bucket, nxt)] += 1
                        tot[bucket] += 1
                prev_dxab = dxab
                prev_za = za
                prev_dtab = dtab
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

buckets = ['DTAB≤2', 'DTAB3-5', 'DTAB6-10', 'DTAB11-20', 'DTAB>20']

print('=' * 70)
print('乙(ZA<0) 次日转移概率 vs DTAB')
print('=' * 70)
print(f'{"DTAB":<10} {"n":>8} {"转乙ZA>0":>10} {"维持乙ZA<0":>12} {"转丙":>8} {"转丁":>8}')
print('-' * 70)
for b in buckets:
    t = tot[b]
    if t == 0: continue
    p_pos = stats[(b, '转乙ZA>0')]/t*100
    p_neg = stats[(b, '维持乙ZA<0')]/t*100
    p_bing = stats[(b, '转丙')]/t*100
    p_ding = stats[(b, '转丁')]/t*100
    print(f'{b:<10} {t:>8,} {p_pos:>9.2f}% {p_neg:>11.2f}% {p_bing:>7.2f}% {p_ding:>7.2f}%')
