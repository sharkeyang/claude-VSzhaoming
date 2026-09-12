# -*- coding: utf-8 -*-
"""
DXZC>0 / DXZC<0 时各 DXAB 护型的 升连 比例分布
====================================================
升连 = 柱排[10] 以"升"开头且含"连"（连续阳线）
对比 DXZC>0 vs DXZC<0 时各护型的升连比例

磁盘CSV列序：8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 14=日ZC
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

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('升') and '连' in s: return '升连'
    if s.startswith('跌') and '连' in s: return '跌连'
    if s.startswith('升') and '孕' in s: return '升孕'
    if s.startswith('跌') and '孕' in s: return '跌孕'
    if s.startswith('升') and '吞' in s: return '升吞'
    if s.startswith('跌') and '吞' in s: return '跌吞'
    if '人' in s: return '人排'
    return '其他'

# 统计: (护型, zc_sign, 柱排类) -> count
stats = defaultdict(int)
# 每(护型, zc_sign)总行数
tot = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 14: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                if za is None or zc is None: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                zc_sign = 'ZC>0' if zc > 0 else 'ZC<=0'
                zp = classify_zp(row[10])
                stats[(key, zc_sign, zp)] += 1
                tot[(key, zc_sign)] += 1
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

all_types = ['甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)', '己(ZA>0)']
zp_cats = ['升连', '跌连', '升孕', '跌孕', '升吞', '跌吞', '人排', '其他']

for zc_sign in ['ZC>0', 'ZC<=0']:
    print('=' * 78)
    print(f'{zc_sign} 时各护型 柱排分布（升连比例）')
    print('=' * 78)
    print(f'{"护型":<12} {"n":>10} {"升连":>8} {"跌连":>8} {"升孕":>7} {"跌孕":>7} {"升吞":>7} {"跌吞":>7} {"人排":>7}')
    print('-' * 78)
    for k in all_types:
        t = tot[(k, zc_sign)]
        if t == 0: continue
        def p(cat):
            return stats[(k, zc_sign, cat)]/t*100
        print(f'{k:<12} {t:>10,} {p("升连"):>7.2f}% {p("跌连"):>7.2f}% {p("升孕"):>6.2f}% {p("跌孕"):>6.2f}% {p("升吞"):>6.2f}% {p("跌吞"):>6.2f}% {p("人排"):>6.2f}%')
    print()

print('=' * 78)
print('升连比例对比：DXZC>0 vs DXZC<=0')
print('=' * 78)
print(f'{"护型":<12} {"ZC>0升连":>10} {"ZC<=0升连":>12} {"差值":>8}')
print('-' * 50)
for k in all_types:
    t_pos = tot[(k, 'ZC>0')]
    t_neg = tot[(k, 'ZC<=0')]
    if t_pos == 0 or t_neg == 0: continue
    p_pos = stats[(k, 'ZC>0', '升连')]/t_pos*100
    p_neg = stats[(k, 'ZC<=0', '升连')]/t_neg*100
    print(f'{k:<12} {p_pos:>9.2f}% {p_neg:>11.2f}% {p_pos-p_neg:>+7.2f}pp')
