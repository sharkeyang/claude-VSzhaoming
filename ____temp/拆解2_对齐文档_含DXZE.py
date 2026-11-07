# -*- coding: utf-8 -*-
"""对齐文档D §2.6：退出条件对比（含文档定义的A={下,忑}和C=DXZE<0）
介入条件统一：周大局首字符∈{A,H}

退出条件（持有期间触发即退出，周层大局转Z也退出）：
- A1_忠忑      : {忠,忑}（我之前的策略，两线之下但含忠）
- A2_下忑      : {下,忑}（文档A=DXZD<0且DXZC<0，主升转弱确认）
- B_下忠忑     : {下,忠,忑}（升势转跌势，DJZ<DJD）
- C1_ZC<0      : {中,下,忠,忑}（跌破短均线，最敏感）
- C2_ZE<0      : DXZE<0（文档C=强制止损，跌破EMA120）
- D_无截断     : {}（纯Z退基准）

注：C2用DXZE<0（列18），其他用DXCD（列8）
"""
import csv, sys, io, os, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL_CLOSE = 1
COL_DXCD = 8
COL_DTZE = 18   # 日ZE = DTZE
COL_ZDJ = 81
ZD_AH = {'A', 'H'}

# (名称, 截断集合DXCD, 是否用DXZE<0替代)
STRATEGIES = [
    ('A1_忠忑(两线之下)', {'忠', '忑'}, False),
    ('A2_下忑(文档A主升转弱)', {'下', '忑'}, False),
    ('B_下忠忑(转跌势)', {'下', '忠', '忑'}, False),
    ('C1_ZC<0(跌破短均线)', {'中', '下', '忠', '忑'}, False),
    ('C2_ZE<0(文档C强制止损)', set(), True),   # 用DXZE<0
    ('D_无截断(纯Z退)', set(), False),
]

def simulate(rows, exit_set, use_ze):
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
        # DXZE<0 判定
        ze_below = False
        if use_ze:
            try:
                ze_below = float(row[COL_DTZE]) < 0
            except:
                ze_below = False
        if not in_pos:
            can_enter = zdj_first in ZD_AH
            if use_ze:
                can_enter = can_enter and not ze_below
            else:
                can_enter = can_enter and (not exit_set or dxcd not in exit_set)
            if can_enter:
                in_pos = True
                buy_price = close
        else:
            do_exit = False
            if zdj_first == 'Z':
                do_exit = True
            elif use_ze and ze_below:
                do_exit = True
            elif (not use_ze) and exit_set and dxcd in exit_set:
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

for name, exit_set, use_ze in STRATEGIES:
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
        trades = simulate(rows, exit_set, use_ze)
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
