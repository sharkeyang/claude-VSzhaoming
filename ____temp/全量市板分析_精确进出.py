# -*- coding: utf-8 -*-
"""
全量市板分析_精确进出.py
====================
用谕组日CSV全量数据，按市板统计 DXZE>0+DXZC>0 持有周期表现。
口径：精确进出——条件满足时开盘买入，条件不满足时最高价卖出。
收益用 (卖出最高价/买入开盘价 - 1) 计算。
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

agg = defaultdict(lambda: {'n':0, 'sum_ret':0.0, 'n_win':0, 'n_loss':0, 'n_severe':0, 'rets':[], 'days':[]})

t0 = time.time()
for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  {i}/{len(files)}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5:
            continue
    except:
        continue
    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if not board:
        continue

    try:
        ze = df['日ZE'].astype(float).values
        zc = df['日ZC'].astype(float).values
        open_p = df['开'].astype(float).values
        high = df['高'].astype(float).values
        close = df['收'].astype(float).values
    except:
        continue

    in_cycle = False
    entry_price = 0.0
    cycle_days = 0
    for j in range(len(df)):
        cond = ze[j] > 0 and zc[j] > 0
        if cond and not in_cycle:
            in_cycle = True
            entry_price = open_p[j] if open_p[j] > 0 else close[j]
            cycle_days = 0
        if in_cycle:
            cycle_days += 1
        if in_cycle and (not cond or j == len(df)-1):
            exit_price = high[j] if high[j] > 0 else close[j]
            if entry_price > 0 and exit_price > 0:
                total_ret = (exit_price / entry_price - 1) * 100
                agg[board]['n'] += 1
                agg[board]['sum_ret'] += total_ret
                agg[board]['rets'].append(total_ret)
                if total_ret > 0:
                    agg[board]['n_win'] += 1
                else:
                    agg[board]['n_loss'] += 1
                if total_ret < -5:
                    agg[board]['n_severe'] += 1
                agg[board]['days'].append(cycle_days)
            in_cycle = False

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

lines = []
lines.append('市板,周期,胜率,亏损率,<-5%,均收益,中位数,均天数')
for board in ['Qif','Qic','Qim','Qit','Qin','Qd','Qe','Qst','Qbj']:
    a = agg[board]
    if a['n'] == 0:
        continue
    win_rate = a['n_win']/a['n']*100
    loss_rate = a['n_loss']/a['n']*100
    severe_rate = a['n_severe']/a['n']*100
    avg_ret = a['sum_ret']/a['n']
    median_ret = np.median(a['rets']) if a['rets'] else 0
    avg_days = np.mean(a['days']) if a['days'] else 0
    lines.append(f'{board},{a["n"]},{win_rate:.1f}%,{loss_rate:.1f}%,{severe_rate:.1f}%,{avg_ret:.2f}%,{median_ret:.2f}%,{avg_days:.1f}天')

result = '\n'.join(lines)
print(result)

with open('____temp/board_full_precision.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(f'\n结果已保存: ____temp/board_full_precision.txt')