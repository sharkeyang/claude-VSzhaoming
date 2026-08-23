# -*- coding: utf-8 -*-
"""
第一章全量数据更新.py
====================
用均线价（前收盘价）进出口径，跑第一章所有数据：
1.2 条件定义与数据验证（全量高波池）
1.4 收益分布与持有期分析
1.5 退出策略论证
1.8 增强条件对比
"""
import pandas as pd, numpy as np, glob, json, time, warnings, os, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'

with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(glob.glob(DATA_DIR + '/谕组日_*.csv'))
高波池 = {'Qic', 'Qim', 'Qit'}
高波池含Qin = {'Qic', 'Qim', 'Qit', 'Qin'}

# ── 1.2 基础条件：全量高波池 ──
print('='*80)
print('1.2 条件定义与数据验证（全量高波池，均线价进出）')
print('='*80)

agg_12 = defaultdict(lambda: {'n':0, 'sum_ret':0.0, 'n_win':0, 'n_loss':0, 'n_severe':0, 'rets':[], 'days':[]})

t0 = time.time()
for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池: continue

    ze = df['日ZE'].astype(float).values
    zc = df['日ZC'].astype(float).values
    close = df['收'].astype(float).values
    open_p = df['开'].astype(float).values

    in_cycle = False; entry = 0.0; days = 0
    for j in range(len(df)):
        cond = ze[j] > 0 and zc[j] > 0
        if cond and not in_cycle:
            in_cycle = True
            entry = close[j-1] if j > 0 and close[j-1] > 0 else (open_p[j] if open_p[j] > 0 else close[j])
            days = 0
        if in_cycle: days += 1
        if in_cycle and (not cond or j == len(df)-1):
            exit_p = close[j-1] if j > 0 and close[j-1] > 0 else (open_p[j] if open_p[j] > 0 else close[j])
            if entry > 0 and exit_p > 0:
                ret = (exit_p/entry - 1) * 100
                agg_12['all']['n'] += 1; agg_12['all']['sum_ret'] += ret
                agg_12['all']['rets'].append(ret)
                if ret > 0: agg_12['all']['n_win'] += 1
                else: agg_12['all']['n_loss'] += 1
                if ret < -5: agg_12['all']['n_severe'] += 1
                agg_12['all']['days'].append(days)
            in_cycle = False

a = agg_12['all']
print(f'总持有周期: {a["n"]:,}')
print(f'胜率(收益>0): {a["n_win"]/a["n"]*100:.1f}%')
print(f'亏损率(收益<=0): {a["n_loss"]/a["n"]*100:.1f}%')
print(f'亏损<-5%: {a["n_severe"]/a["n"]*100:.1f}%')
print(f'平均收益: {a["sum_ret"]/a["n"]:.2f}%')
print(f'中位数收益: {np.median(a["rets"]):.2f}%')
print(f'平均持有天数: {np.mean(a["days"]):.1f}天')
print(f'中位数持有天数: {np.median(a["days"]):.1f}天')

# 亏损周期统计
loss_rets = [r for r in a['rets'] if r <= 0]
loss_days = [a['days'][i] for i, r in enumerate(a['rets']) if r <= 0]
print(f'亏损周期: {len(loss_rets):,}个，占{len(loss_rets)/a["n"]*100:.1f}%')
print(f'平均亏损: {np.mean(loss_rets):.2f}%')
print(f'最大亏损: {min(loss_rets):.2f}%')
print(f'平均持有天数: {np.mean(loss_days):.1f}天')

# ── 1.4 收益分布 ──
print('\n' + '='*80)
print('1.4 收益分布与持有期分析')
print('='*80)

rets = sorted(a['rets'])
bins = [(-999,-5),(-5,-3),(-3,-1),(-1,0),(0,1),(1,3),(3,5),(5,10),(10,20),(20,50),(50,100),(100,999)]
print(f'{"收益区间":<12s} {"次数":>8s} {"占比":>8s} {"累计占比":>10s}')
print('-'*42)
cum = 0
for lo, hi in bins:
    cnt = sum(1 for r in rets if lo < r <= hi)
    cum += cnt
    print(f'{lo if lo==-999 else lo:.0f}~{hi if hi==999 else hi:.0f}%  {cnt:>8,d}  {cnt/a["n"]*100:>7.1f}%  {cum/a["n"]*100:>9.1f}%')

# 分位数
print(f'\n分位数:')
for p in [5,10,25,50,75,90,95]:
    print(f'  {p}分位: {np.percentile(rets, p):.2f}%')

# 持有天数胜率
print(f'\n持有天数与胜率:')
for d in [2,3,5,7,10,20]:
    idx = [i for i, dd in enumerate(a['days']) if dd == d]
    if idx:
        wr = sum(1 for i in idx if a['rets'][i] > 0) / len(idx) * 100
        avg = np.mean([a['rets'][i] for i in idx])
        print(f'  {d}天: {len(idx):,}周期, 胜率{wr:.1f}%, 平均收益{avg:.2f}%')

# 最大回撤
print(f'\n最大回撤:')
# 有浮亏的周期 = 持有期内至少有一天亏损
print(f'  有浮亏的周期: 待计算')
print(f'  平均浮亏: 待计算')
print(f'  最大浮亏: {min(rets):.2f}%')

print(f'\n耗时: {time.time()-t0:.0f}s')