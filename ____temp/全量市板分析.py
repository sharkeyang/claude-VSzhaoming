# -*- coding: utf-8 -*-
"""
全量市板分析.py
===============
用谕组日CSV全量数据，按市板统计 DXZE>0+DXZC>0 持有周期表现。
口径：条件满足时入场，条件不满足（ZE<=0或ZC<=0）时退出，统计整个持有期的收益。
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

# 按市板聚合持有周期
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
        pr = df['涨幅'].astype(float).values
    except:
        continue

    # 找持有周期：ZE>0+ZC>0 连续段
    in_cycle = False
    cycle_ret = 1.0
    cycle_days = 0
    for j in range(len(df)):
        cond = ze[j] > 0 and zc[j] > 0
        if cond and not in_cycle:
            in_cycle = True
            cycle_ret = 1.0
            cycle_days = 0
        if in_cycle:
            cycle_ret *= (1 + pr[j]/100)
            cycle_days += 1
        if in_cycle and (not cond or j == len(df)-1):
            total_ret = (cycle_ret - 1) * 100
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

# 输出结果
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

with open('____temp/board_full_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(f'\n结果已保存: ____temp/board_full_analysis.txt')