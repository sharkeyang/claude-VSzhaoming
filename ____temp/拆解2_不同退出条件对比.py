# -*- coding: utf-8 -*-
"""拆解2：不同退出条件对比
A: 忠/忑（两线之下，当前策略）
B: 下/忠/忑（升势转跌势，DJZ<DJD）
C: 中/下/忠/忑（DXZC<0，跌破短均线DJC）
D: 无截断（纯Z退基准）
介入条件统一：周大局A/H
"""
import csv, sys, io, os, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL_DATE = 0
COL_CLOSE = 1
COL_DXCD = 8
COL_ZDJ = 81
ZD_AH = {'A', 'H'}

EXIT_SETS = {
    'A_忠忑(两线之下)': {'忠', '忑'},
    'B_下忠忑(转跌势)': {'下', '忠', '忑'},
    'C_中下忠忑(ZC<0)': {'中', '下', '忠', '忑'},
    'D_无截断(纯Z退)': set(),
}

def load_rows(filepath):
    try:
        with open(filepath, encoding='gbk') as fp:
            r = csv.reader(fp)
            next(r)
            return list(r)
    except:
        return None

def simulate(rows, exit_set):
    trades = []
    in_pos = False
    buy_price = 0.0
    buy_date = ''
    for row in rows:
        if len(row) <= COL_ZDJ:
            continue
        try:
            close = float(row[COL_CLOSE])
        except:
            continue
        dxcd = row[COL_DXCD]
        zdj_first = row[COL_ZDJ][0] if len(row[COL_ZDJ]) > 0 else ''
        if not in_pos:
            if zdj_first in ZD_AH and dxcd not in exit_set:
                in_pos = True
                buy_price = close
                buy_date = row[COL_DATE]
        else:
            exit_reason = ''
            if zdj_first == 'Z':
                exit_reason = '周Z退'
            elif exit_set and dxcd in exit_set:
                exit_reason = '截断'
            if exit_reason:
                trades.append((buy_date, buy_price, row[COL_DATE], close, exit_reason))
                in_pos = False
    if in_pos and rows:
        last = rows[-1]
        try:
            trades.append((buy_date, buy_price, last[COL_DATE], float(last[COL_CLOSE]), '未平仓'))
        except:
            pass
    return trades

files = sorted(glob.glob('昭明算展/谕组日/谕组日_*.csv'))
t0 = time.time()

# 预加载所有rows
print('加载数据...')
all_rows = {}
for i, f in enumerate(files):
    rows = load_rows(f)
    if rows:
        all_rows[f] = rows
    if (i+1) % 1000 == 0:
        print(f'  加载 {i+1}/{len(files)}')
print(f'加载完成，用时{time.time()-t0:.0f}s')

print('\n========== 拆解2：不同退出条件对比 ==========')
print(f'{"退出条件":<22} {"笔数":>7} {"胜率":>7} {"平均":>9} {"中位":>9} {"累计":>12} {"大赚%":>7} {"大亏%":>7} {"复利均":>9} {"复利盈%":>8}')
for name, exit_set in EXIT_SETS.items():
    all_rets = []
    big_win = 0
    big_loss = 0
    wins = 0
    comp_list = []
    for f, rows in all_rows.items():
        trades = simulate(rows, exit_set)
        if not trades:
            continue
        rets = [(t[3]-t[1])/t[1]*100 for t in trades if t[1] > 0]
        if not rets:
            continue
        all_rets.extend(rets)
        wins += sum(1 for r in rets if r > 0)
        big_win += sum(1 for r in rets if r > 10)
        big_loss += sum(1 for r in rets if r < -10)
        eq = 1.0
        for t in trades:
            if t[1] > 0:
                eq *= (1 + (t[3]-t[1])/t[1])
        comp_list.append((eq-1)*100)
    n = len(all_rets)
    cn = len(comp_list)
    cs = sorted(comp_list)
    print(f'{name:<22} {n:>7} {wins/n*100:>6.1f}% {sum(all_rets)/n:>+8.3f}% {sorted(all_rets)[n//2]:>+8.3f}% {sum(all_rets):>+11.1f}% {big_win/n*100:>6.2f}% {big_loss/n*100:>6.2f}% {sum(comp_list)/cn:>+8.2f}% {sum(1 for x in comp_list if x>0)/cn*100:>7.1f}%')
print(f'\n用时: {time.time()-t0:.0f}s')
