# -*- coding: utf-8 -*-
"""
股性分析：持有条件比例是否定义股票性格
====================================================
用户假设：持有条件比例（DXCD=上/忐 + 甲/乙ZA>0/己/乙ZA<0）定义股性——
高比例=适合持有（有操盘手/游资/机构持有）=好股；低比例=杂毛=不适合持有。

验证：
  ① 股性稳定性：股票持有比例是否随时间稳定（前一半 vs 后一半的相关性）
  ② 高/低比例股票的收益差异（P≥3%、均高幅、日均涨幅）
  ③ 高/低比例股票的波动性差异（标准差）
  ④ 按比例分组的收益对比

磁盘CSV列序：5=涨幅, 8=DXCD, 9=DXAB, 13=日ZA, 26=次日高幅
"""
import csv, os, sys, statistics
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

# 每只股票: code -> {总天数, 持有天数, 前一半持有比例, 后一半持有比例, 次日高幅列表, 涨幅列表}
per_stock = {}
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            rows = list(csv.reader(f))
            data = rows[1:]
            n = len(data)
            if n < 100: continue  # 样本太少
            rec = {'tot': n, 'hold': 0, 'hrs': [], 'zfs': []}
            half = n // 2
            rec['hold_first'] = 0
            rec['hold_second'] = 0
            for i, row in enumerate(data):
                if len(row) <= 26: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                hr = to_f(row[26])
                zf = to_f(row[5])
                if hr is None or hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                rec['hrs'].append(hr)
                if zf is not None: rec['zfs'].append(zf)
                if in_region(dxcd, hx):
                    rec['hold'] += 1
                    if i < half: rec['hold_first'] += 1
                    else: rec['hold_second'] += 1
            rec['hold_first_ratio'] = rec['hold_first'] / half * 100
            rec['hold_second_ratio'] = rec['hold_second'] / (n - half) * 100
            per_stock[code] = rec
    except Exception:
        pass

print(f'高波池文件: {files_core}, 有效股票: {len(per_stock)}')
print()

# 每只股票的持有比例
props = {c: r['hold']/r['tot']*100 for c, r in per_stock.items()}

print('=' * 70)
print('① 股性稳定性：前一半 vs 后一半 持有比例')
print('=' * 70)
# 计算相关性（皮尔逊）
firsts = [per_stock[c]['hold_first_ratio'] for c in per_stock]
seconds = [per_stock[c]['hold_second_ratio'] for c in per_stock]
n = len(firsts)
mean_f = sum(firsts)/n; mean_s = sum(seconds)/n
cov = sum((firsts[i]-mean_f)*(seconds[i]-mean_s) for i in range(n))/n
std_f = statistics.stdev(firsts); std_s = statistics.stdev(seconds)
corr = cov/(std_f*std_s)
print(f'  前一半均值: {mean_f:.2f}%, 后一半均值: {mean_s:.2f}%')
print(f'  相关性(皮尔逊): {corr:.3f}')
print(f'  → 若相关性高(>0.5)，说明持有比例是稳定股性')

print()
print('=' * 70)
print('② 按持有比例分组：收益与波动对比')
print('=' * 70)
# 分组：低<20%, 中低20-27%, 中高27-33%, 高>33%
groups = {'低(<20%)': [], '中低(20-27%)': [], '中高(27-33%)': [], '高(>33%)': []}
for c, p in props.items():
    if p < 20: groups['低(<20%)'].append(c)
    elif p < 27: groups['中低(20-27%)'].append(c)
    elif p < 33: groups['中高(27-33%)'].append(c)
    else: groups['高(>33%)'].append(c)

print(f'{"分组":<14} {"股票数":>6} {"平均持有比例":>10} {"P(≥3%)":>8} {"均高幅":>8} {"日均涨幅":>8} {"波动(σ)":>8}')
print('-' * 70)
for gname, codes in groups.items():
    if not codes: continue
    hrs = [hr for c in codes for hr in per_stock[c]['hrs']]
    zfs = [zf for c in codes for zf in per_stock[c]['zfs']]
    avg_p = sum(props[c] for c in codes)/len(codes)
    p3 = sum(1 for hr in hrs if hr >= 3)/len(hrs)*100
    avg_hr = sum(hrs)/len(hrs)
    avg_zf = sum(zfs)/len(zfs)
    vol = statistics.stdev(zfs)
    print(f'{gname:<14} {len(codes):>6} {avg_p:>9.2f}% {p3:>7.2f}% {avg_hr:>7.2f}% {avg_zf:>7.2f}% {vol:>7.2f}%')

print()
print('=' * 70)
print('③ 极端对比：最高10% vs 最低10% 持有比例股票')
print('=' * 70)
sorted_codes = sorted(props, key=lambda c: props[c])
low10 = sorted_codes[:max(1, len(sorted_codes)//10)]
high10 = sorted_codes[-max(1, len(sorted_codes)//10):]
for label, codes in [('最低10%', low10), ('最高10%', high10)]:
    hrs = [hr for c in codes for hr in per_stock[c]['hrs']]
    zfs = [zf for c in codes for zf in per_stock[c]['zfs']]
    avg_p = sum(props[c] for c in codes)/len(codes)
    p3 = sum(1 for hr in hrs if hr >= 3)/len(hrs)*100
    avg_hr = sum(hrs)/len(hrs)
    avg_zf = sum(zfs)/len(zfs)
    vol = statistics.stdev(zfs)
    print(f'{label}: 平均持有比例{avg_p:.2f}%, P(≥3%)={p3:.2f}%, 均高幅={avg_hr:.2f}%, 日均涨幅={avg_zf:.2f}%, 波动={vol:.2f}%')
