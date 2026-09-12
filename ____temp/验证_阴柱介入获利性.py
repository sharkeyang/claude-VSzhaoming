# -*- coding: utf-8 -*-
"""
操作区域 阴柱介入 获利性分析
====================================================
操作区域：DXCD=上/忐 + 甲/乙ZA>0/己/乙ZA<0
阴柱 = 收<开

输出：
  ① 操作区域是否确认获利（对比基线）
  ② 区域内 阴柱 vs 阳柱 的获利性（P≥3%/均高幅/期望值）
  ③ 阴柱介入的次日高幅分布（各阈值胜率）
  ④ 阴柱介入的期望收益估算

磁盘CSV列序：1=收, 2=开, 8=DXCD, 9=DXAB, 13=日ZA, 26=次日高幅
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

def in_region(dxcd, hx):
    if dxcd not in ('上', '忐'): return False
    if hx in ('甲', '乙', '己'): return True
    return False

# 各类别: key -> 次日高幅列表
data = defaultdict(list)
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
                if len(row) <= 26: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                close = to_f(row[1])
                open_ = to_f(row[2])
                hr = to_f(row[26])
                if close is None or open_ is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                data['基线'].append(hr)
                if in_region(dxcd, hx):
                    data['区域-全部'].append(hr)
                    if close < open_:
                        data['区域-阴柱'].append(hr)
                    else:
                        data['区域-阳柱'].append(hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

def analyze(label, hrs):
    n = len(hrs)
    p3 = sum(1 for h in hrs if h >= 3)/n*100
    avg = sum(hrs)/n
    # 各阈值胜率
    w0 = sum(1 for h in hrs if h >= 0)/n*100
    w1 = sum(1 for h in hrs if h >= 1)/n*100
    w2 = sum(1 for h in hrs if h >= 2)/n*100
    w5 = sum(1 for h in hrs if h >= 5)/n*100
    # 期望值（吃均高幅的50%/80%）
    ev50 = avg * 0.5
    ev80 = avg * 0.8
    return n, p3, avg, w0, w1, w2, w5, ev50, ev80

print('=' * 90)
print('操作区域 阴柱介入 获利性分析')
print('=' * 90)
print(f'{"类别":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"≥0%":>7} {"≥1%":>7} {"≥2%":>7} {"≥5%":>7} {"EV50%":>7} {"EV80%":>7}')
print('-' * 90)
for label in ['基线', '区域-全部', '区域-阴柱', '区域-阳柱']:
    hrs = data[label]
    if not hrs: continue
    n, p3, avg, w0, w1, w2, w5, ev50, ev80 = analyze(label, hrs)
    print(f'{label:<12} {n:>10,} {p3:>7.2f}% {avg:>7.2f}% {w0:>6.1f}% {w1:>6.1f}% {w2:>6.1f}% {w5:>6.1f}% {ev50:>6.2f}% {ev80:>6.2f}%')

print()
print('=' * 90)
print('阴柱介入 次日高幅分布（操作区域内）')
print('=' * 90)
hrs = data['区域-阴柱']
bins = [(-999,-5),(-5,-3),(-3,0),(0,1),(1,2),(2,3),(3,5),(5,10),(10,999)]
print(f'{"区间":<12} {"n":>10} {"占比":>8}')
print('-' * 35)
for lo, hi in bins:
    cnt = sum(1 for h in hrs if lo <= h < hi)
    print(f'{lo:>5}~{hi:<5}% {cnt:>10,} {cnt/len(hrs)*100:>7.2f}%')
