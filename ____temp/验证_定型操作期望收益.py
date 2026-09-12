# -*- coding: utf-8 -*-
"""
定型操作框架（§4.8）期望收益分析
====================================================
定型方法：DXCD=上/忐 × 甲/乙ZA>0/己 × DJA丘(日ZA>0) + BSHA5触发器

输出：
  ① 各层递进的 P(≥3%)/均高幅（基线→DXCD→护型→DJA丘）
  ② 定型方法核心组合的 P(≥3%)/均高幅
  ③ 交易频率估算（每年出现多少天）
  ④ 年化收益粗估

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 19=BSHA, 26=次日高幅
（注意：表头62列与数据列序不一致，次日高幅实际在[26]非[28]，见csv-read-export-columns-not-header）
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

# 各层统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
# 每只股票的 setup run 计数（DJA丘连续段 = 一次交易）
per_stock_runs = defaultdict(int)  # code -> DJA丘 run 数
per_stock_bsha_runs = defaultdict(int)  # code -> BSHA5 run 数
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    in_dja = False
    in_bsha = False
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 26: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                bsha = to_f(row[19])
                hr = to_f(row[26])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                # 各层
                stats['基线'][0]+=1; stats['基线'][1]+= (1 if hr>=3 else 0); stats['基线'][2]+=hr
                if dxcd in ('上','忐'):
                    stats['DXCD上忐'][0]+=1; stats['DXCD上忐'][1]+= (1 if hr>=3 else 0); stats['DXCD上忐'][2]+=hr
                    if key in ('甲(ZA>0)','乙(ZA>0)','己(ZA>0)'):
                        stats['+护型甲乙己'][0]+=1; stats['+护型甲乙己'][1]+= (1 if hr>=3 else 0); stats['+护型甲乙己'][2]+=hr
                        if za > 0:
                            stats['+DJA丘'][0]+=1; stats['+DJA丘'][1]+= (1 if hr>=3 else 0); stats['+DJA丘'][2]+=hr
                            # DJA丘 run 计数
                            if not in_dja:
                                per_stock_runs[code] += 1
                                in_dja = True
                            if bsha is not None and bsha >= 5:
                                stats['+BSHA5'][0]+=1; stats['+BSHA5'][1]+= (1 if hr>=3 else 0); stats['+BSHA5'][2]+=hr
                                if not in_bsha:
                                    per_stock_bsha_runs[code] += 1
                                    in_bsha = True
                            else:
                                in_bsha = False
                        else:
                            in_dja = False
                            in_bsha = False
                    else:
                        in_dja = False
                        in_bsha = False
                else:
                    in_dja = False
                    in_bsha = False
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('=' * 70)
print('定型操作框架：各层递进 P(≥3%)/均高幅')
print('=' * 70)
print(f'{"层":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 50)
for k in ['基线', 'DXCD上忐', '+护型甲乙己', '+DJA丘', '+BSHA5']:
    s = stats[k]
    if s[0] == 0: continue
    print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

# 交易频率估算
print()
print('=' * 70)
print('交易频率与年化收益粗估')
print('=' * 70)
total_rows = stats['基线'][0]
# 每只股票每年约250交易日
rows_per_year = 250
# 数据覆盖年数估算：总行数 / (股票数 × 250)
years = total_rows / (files_core * 250)
print(f'总样本: {total_rows:,} 行, {files_core} 只股票, 覆盖约 {years:.1f} 年')

# 每只股票每年的 setup run 数
dja_runs_per_stock = sum(per_stock_runs.values()) / files_core / years
bsha_runs_per_stock = sum(per_stock_bsha_runs.values()) / files_core / years
print(f'每只股票每年 DJA丘 交易次数: {dja_runs_per_stock:.1f} 次')
print(f'每只股票每年 BSHA5 交易次数: {bsha_runs_per_stock:.1f} 次')

# 年化收益粗估（单只股票，复利）
for k, label, runs in [('+DJA丘', 'DJA丘', dja_runs_per_stock), ('+BSHA5', 'BSHA5', bsha_runs_per_stock)]:
    s = stats[k]
    if s[0] == 0: continue
    p3 = s[1]/s[0]
    avg_hr = s[2]/s[0]
    print(f'\n{label}: P(≥3%)={p3*100:.2f}%, 均高幅={avg_hr:.2f}%, 每年{runs:.1f}次/股')
    for cap, capname in [(0.5, '保守(吃50%均高幅)'), (0.8, '乐观(吃80%均高幅)')]:
        per_trade = avg_hr * cap
        annual_simple = per_trade * runs
        annual_comp = ((1 + per_trade/100) ** runs - 1) * 100
        print(f'  {capname}: 每次{per_trade:.2f}% × {runs:.1f}次 = 年化简单{annual_simple:.1f}% / 复利{annual_comp:.1f}%')
