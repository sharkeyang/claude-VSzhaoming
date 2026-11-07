# -*- coding: utf-8 -*-
"""全量验证：周层大局A/H介入 + DXCD两线之下(忠/忑)截断退出
全量3446只股票，谕组日CSV（GBK，135列）
介入: 周大局首字符∈{A,H} 且 DXCD∉{忠,忑}
退出: 周大局首字符=Z 或 DXCD∈{忠,忑}
"""
import csv, sys, io, os, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL_DATE = 0
COL_CLOSE = 1
COL_DXCD = 8
COL_ZDJ = 81

TWO_LINE_BELOW = {'忠', '忑'}
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
        dxcd = row[COL_DXCD]
        zdj = row[COL_ZDJ]
        zdj_first = zdj[0] if len(zdj) > 0 else ''
        if not in_pos:
            if zdj_first in ZD_AH and dxcd not in TWO_LINE_BELOW:
                in_pos = True
                buy_price = close
                buy_date = row[COL_DATE]
        else:
            reason = ''
            if zdj_first == 'Z':
                reason = '周Z退'
            elif dxcd in TWO_LINE_BELOW:
                reason = '两线截断'
            if reason:
                trades.append((buy_date, buy_price, row[COL_DATE], close, reason))
                in_pos = False
    if in_pos and rows:
        last = rows[-1]
        try:
            trades.append((buy_date, buy_price, last[COL_DATE], float(last[COL_CLOSE]), '未平仓'))
        except:
            pass
    return trades

files = sorted(glob.glob('昭明算展/谕组日/谕组日_*.csv'))
print(f'总文件数: {len(files)}')
t0 = time.time()

all_rets = []          # 每笔收益率
reason_rets = {}       # 按退出原因
stock_results = []     # 每只股票(代码,交易数,胜率,累计收益)
total_trades = 0
wins = 0
losses = 0
big_win = 0   # >10%
big_loss = 0  # <-10%
flat = 0      # 未平仓笔数

for i, f in enumerate(files):
    code = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    trades = simulate_one(f)
    if not trades:
        continue
    rets = [(t[3]-t[1])/t[1]*100 for t in trades if t[1] > 0]
    if not rets:
        continue
    sw = sum(1 for r in rets if r > 0)
    stock_results.append((code, len(rets), sw, sum(rets)))
    total_trades += len(rets)
    wins += sw
    losses += len(rets) - sw
    big_win += sum(1 for r in rets if r > 10)
    big_loss += sum(1 for r in rets if r < -10)
    for t in trades:
        if t[1] <= 0:
            continue
        r = (t[3]-t[1])/t[1]*100
        all_rets.append(r)
        reason = t[4]
        reason_rets.setdefault(reason, []).append(r)
        if reason == '未平仓':
            flat += 1
    if (i+1) % 500 == 0:
        print(f'  进度 {i+1}/{len(files)}  已处理交易{total_trades}笔  用时{time.time()-t0:.0f}s')

elapsed = time.time() - t0
n = len(all_rets)
print(f'\n========== 全量验证结果 ==========')
print(f'股票数: {len(stock_results)}  总交易笔数: {total_trades}  用时: {elapsed:.0f}s')
print(f'胜: {wins}笔({wins/n*100:.2f}%)  负: {losses}笔({losses/n*100:.2f}%)')
print(f'平均收益: {sum(all_rets)/n:+.3f}%')
print(f'中位收益: {sorted(all_rets)[n//2]:+.3f}%')
print(f'累计收益(简单加总): {sum(all_rets):+.1f}%')
print(f'大赚(>10%): {big_win}笔({big_win/n*100:.2f}%)  大亏(<-10%): {big_loss}笔({big_loss/n*100:.2f}%)')
print(f'\n--- 按退出原因 ---')
for reason, rets in sorted(reason_rets.items()):
    nr = len(rets)
    print(f'  {reason}: {nr}笔({nr/n*100:.1f}%) 胜率{sum(1 for r in rets if r>0)/nr*100:.1f}% 平均{sum(rets)/nr:+.3f}% 累计{sum(rets):+.1f}%')

# 每只股票累计收益分布
stock_cum = [s[3] for s in stock_results]
sc_sorted = sorted(stock_cum)
sn = len(sc_sorted)
print(f'\n--- 每只股票累计收益分布 ---')
print(f'股票数: {sn}')
print(f'盈利股票: {sum(1 for x in stock_cum if x>0)}({sum(1 for x in stock_cum if x>0)/sn*100:.1f}%)  亏损股票: {sum(1 for x in stock_cum if x<0)}({sum(1 for x in stock_cum if x<0)/sn*100:.1f}%)')
print(f'平均累计: {sum(stock_cum)/sn:+.2f}%  中位: {sc_sorted[sn//2]:+.2f}%')
print(f'最差10%: {sc_sorted[sn//10]:+.2f}%  最好10%: {sc_sorted[sn*9//10]:+.2f}%')

# 复利验证：每只股票按交易顺序复利
import math
compound_rets = []
for code, ntr, sw, simple_cum in stock_results:
    pass  # 需要重新算复利，用trades顺序
# 重新算复利
compound_per_stock = []
for f in files[:0]:  # placeholder
    pass
print(f'\n--- 复利收益(每只股票交易顺序复利) ---')
# 重新遍历算复利
comp_results = []
for f in files:
    trades = simulate_one(f)
    if not trades:
        continue
    eq = 1.0
    for t in trades:
        if t[1] <= 0:
            continue
        eq *= (1 + (t[3]-t[1])/t[1])
    comp_results.append((eq-1)*100)
cn = len(comp_results)
if cn:
    cs = sorted(comp_results)
    print(f'股票数: {cn}')
    print(f'复利盈利股票: {sum(1 for x in comp_results if x>0)}({sum(1 for x in comp_results if x>0)/cn*100:.1f}%)')
    print(f'平均复利: {sum(comp_results)/cn:+.2f}%  中位: {cs[cn//2]:+.2f}%')
    print(f'最差10%: {cs[cn//10]:+.2f}%  最好10%: {cs[cn*9//10]:+.2f}%')
