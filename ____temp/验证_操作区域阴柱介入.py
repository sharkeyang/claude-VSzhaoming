# -*- coding: utf-8 -*-
"""
操作区域比例 + 阴柱介入 + 诱多识别
====================================================
操作区域（用户扩展）：DXCD=上/忐 + DXZC>0 + 甲/乙ZA>0/己/乙ZA<0

输出：
  ① 操作区域占总天数比例（高波池）
  ② 区域内 阴柱(收<开) vs 阳柱 的 P(≥3%)——验证阴柱介入
  ③ 区域内 诱多/转坏 信号识别（跌连/跌孕/触顶+跌吞/管宽<10+跌排）

磁盘CSV列序：1=收, 2=开, 8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅, 30=上符串, 31=宽符串, 10=柱排
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

def in_region(dxcd, hx, za):
    """操作区域：DXCD=上/忐 + 甲/乙ZA>0/己/乙ZA<0"""
    if dxcd not in ('上', '忐'): return False
    if hx == '甲': return True
    if hx == '乙': return True  # 乙含ZA>0和ZA<0
    if hx == '己': return True
    return False

# 统计
stats = defaultdict(lambda: [0, 0, 0.0])  # key -> [n, hr3, sum_hr]
tot_days = 0
tot_region = 0
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
                za = to_f(row[13])
                zc = to_f(row[14])
                close = to_f(row[1])
                open_ = to_f(row[2])
                hr = to_f(row[26])
                if za is None or hr is None or close is None or open_ is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                tot_days += 1
                if not in_region(dxcd, hx, za): continue
                tot_region += 1
                # 区域内：阴柱 vs 阳柱
                is_yin = close < open_
                key = '区域-阴柱' if is_yin else '区域-阳柱'
                stats[key][0]+=1; stats[key][1]+= (1 if hr>=3 else 0); stats[key][2]+=hr
                # 区域内各护型
                stats[f'区域-{hx}'][0]+=1; stats[f'区域-{hx}'][1]+= (1 if hr>=3 else 0); stats[f'区域-{hx}'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print(f'总天数: {tot_days:,}, 操作区域天数: {tot_region:,}, 占比: {tot_region/tot_days*100:.2f}%')
print()

print('=' * 70)
print('① 操作区域内 阴柱 vs 阳柱 P(≥3%)')
print('=' * 70)
print(f'{"类别":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
for k in ['区域-阴柱', '区域-阳柱']:
    s = stats[k]
    if s[0] == 0: continue
    print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 70)
print('② 操作区域内各护型 P(≥3%)')
print('=' * 70)
print(f'{"护型":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
for hx in ['甲', '乙', '己']:
    k = f'区域-{hx}'
    s = stats[k]
    if s[0] == 0: continue
    print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
