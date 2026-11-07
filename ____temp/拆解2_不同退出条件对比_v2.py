# -*- coding: utf-8 -*-
"""拆解2重跑：不同退出条件对比（行缓冲输出，单次遍历）
A: 忠/忑（两线之下，当前策略）
B: 下/忠/忑（升势转跌势，DJZ<DJD）
C: 中/下/忠/忑（DXZC<0，跌破短均线DJC）
D: 无截断（纯Z退基准）
介入条件统一：周大局首字符∈{A,H}
"""
import csv, sys, io, os, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

def simulate(rows, exit_set):
    trades = []
    in_pos = False
    buy_price = 0.0
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
            if zdj_first in ZD_AH and (not exit_set or dxcd not in exit_set):
                in_pos = True
                buy_price = close
        else:
            do_exit = False
            if zdj_first == 'Z':
                do_exit = True
            elif exit_set and dxcd in exit_set:
                do_exit = True
            if do_exit:
                if buy_price > 0:
                    trades.append((buy_price, close))
                in_pos = False
    if in_pos and rows:
        last = rows[-1]
        try:
            if buy_price > 0:
                trades.append((buy_price, float(last[COL_CLOSE])))
        except:
            pass
    return trades

files = sorted(glob.glob('昭明算展/谕组日/谕组日_*.csv'))
t0 = time.time()
print(f'总文件数: {len(files)}', flush=True)

# 每个策略独立遍历（避免内存爆炸），4次遍历
for name, exit_set in EXIT_SETS.items():
    all_rets = []
    comp_list = []
    wins = 0
    big_win = 0
    big_loss = 0
    for i, f in enumerate(files):
        try:
            with open(f, encoding='gbk') as fp:
                r = csv.reader(fp)
                next(r)
                rows = list(r)
        except:
            continue
        trades = simulate(rows, exit_set)
        if not trades:
            continue
        eq = 1.0
        for bp, sp in trades:
            ret = (sp - bp) / bp * 100
            all_rets.append(ret)
            if ret > 0:
                wins += 1
            if ret > 10:
                big_win += 1
            if ret < -10:
                big_loss += 1
            eq *= (1 + (sp - bp) / bp)
        comp_list.append((eq - 1) * 100)
        if (i + 1) % 1000 == 0:
            print(f'  [{name}] {i+1}/{len(files)} 用时{time.time()-t0:.0f}s', flush=True)
    n = len(all_rets)
    cn = len(comp_list)
    cs = sorted(comp_list)
    print(f'\n===== {name} =====', flush=True)
    print(f'交易笔数: {n}  胜率: {wins/n*100:.2f}%  平均: {sum(all_rets)/n:+.3f}%  中位: {sorted(all_rets)[n//2]:+.3f}%', flush=True)
    print(f'累计(简单): {sum(all_rets):+.1f}%  大赚>10%: {big_win/n*100:.2f}%  大亏<-10%: {big_loss/n*100:.2f}%', flush=True)
    print(f'复利: 盈利股票{sum(1 for x in comp_list if x>0)/cn*100:.1f}%  平均{sum(comp_list)/cn:+.2f}%  中位{cs[cn//2]:+.2f}%', flush=True)
    print(f'用时: {time.time()-t0:.0f}s', flush=True)
