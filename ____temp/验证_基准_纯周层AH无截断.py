# -*- coding: utf-8 -*-
"""对比基准：纯周层A/H介入 + Z退出（无DXCD截断）
用于对比DXCD两线截断的贡献
"""
import csv, sys, io, os, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL_DATE = 0
COL_CLOSE = 1
COL_DXCD = 8
COL_ZDJ = 81

ZD_AH = {'A', 'H'}

def simulate_one(filepath):
    try:
        with open(filepath, encoding='gbk') as fp:
            r = csv.reader(fp)
            next(r)
            rows = list(r)
    except:
        return None
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
        zdj = row[COL_ZDJ]
        zdj_first = zdj[0] if len(zdj) > 0 else ''
        if not in_pos:
            if zdj_first in ZD_AH:
                in_pos = True
                buy_price = close
                buy_date = row[COL_DATE]
        else:
            if zdj_first == 'Z':
                trades.append((buy_date, buy_price, row[COL_DATE], close, '周Z退'))
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
all_rets = []
stock_results = []
total_trades = 0
wins = 0
big_win = 0
big_loss = 0

for i, f in enumerate(files):
    trades = simulate_one(f)
    if not trades:
        continue
    rets = [(t[3]-t[1])/t[1]*100 for t in trades if t[1] > 0]
    if not rets:
        continue
    sw = sum(1 for r in rets if r > 0)
    stock_results.append((os.path.basename(f), len(rets), sw, sum(rets)))
    total_trades += len(rets)
    wins += sw
    big_win += sum(1 for r in rets if r > 10)
    big_loss += sum(1 for r in rets if r < -10)
    for t in trades:
        if t[1] > 0:
            all_rets.append((t[3]-t[1])/t[1]*100)

n = len(all_rets)
print(f'========== 基准：纯周层A/H介入+Z退出（无截断）==========')
print(f'股票数: {len(stock_results)}  总交易笔数: {total_trades}  用时: {time.time()-t0:.0f}s')
print(f'胜: {wins}笔({wins/n*100:.2f}%)  负: {n-wins}笔({(n-wins)/n*100:.2f}%)')
print(f'平均收益: {sum(all_rets)/n:+.3f}%  中位: {sorted(all_rets)[n//2]:+.3f}%')
print(f'累计(简单加总): {sum(all_rets):+.1f}%')
print(f'大赚(>10%): {big_win}笔({big_win/n*100:.2f}%)  大亏(<-10%): {big_loss}笔({big_loss/n*100:.2f}%)')
stock_cum = [s[3] for s in stock_results]
sc = sorted(stock_cum)
sn = len(sc)
print(f'盈利股票: {sum(1 for x in stock_cum if x>0)}({sum(1 for x in stock_cum if x>0)/sn*100:.1f}%)  平均累计: {sum(stock_cum)/sn:+.2f}%  中位: {sc[sn//2]:+.2f}%')

# 复利
comp = []
for f in files:
    trades = simulate_one(f)
    if not trades:
        continue
    eq = 1.0
    for t in trades:
        if t[1] > 0:
            eq *= (1 + (t[3]-t[1])/t[1])
    comp.append((eq-1)*100)
cn = len(comp)
cs = sorted(comp)
print(f'复利: 盈利{sum(1 for x in comp if x>0)}({sum(1 for x in comp if x>0)/cn*100:.1f}%) 平均{sum(comp)/cn:+.2f}% 中位{cs[cn//2]:+.2f}%')
