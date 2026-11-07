# -*- coding: utf-8 -*-
"""验证策略：周层大局A/H介入 + DXCD两线之下(忠/忑)截断退出
介入: 周大局首字符∈{A,H} 且 DXCD∉{忠,忑}（两线之上）
持有: 周大局首字符≠Z 且 DXCD∉{忠,忑}
退出: 周大局首字符=Z（周线转退出）或 DXCD∈{忠,忑}（两线之下截断）
收益: 介入日收盘买入 → 退出日收盘卖出
"""
import csv, sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 列索引（元数据确认）
COL_DATE = 0      # 日期
COL_CLOSE = 1     # 收盘
COL_DXCD = 8      # DXCD（上/中/下/忐/忠/忑）
COL_ZDJ = 81      # 周层大局

TWO_LINE_BELOW = {'忠', '忑'}   # DJZ<DJC 且 DJZ<DJD（两线之下）
ZD_AH = {'A', 'H'}              # 周大局首字符 A入/H持

def simulate_one(filepath):
    """单只股票模拟，返回交易列表[(买入日,买入价,卖出日,卖出价,退出原因)]"""
    with open(filepath, encoding='gbk') as fp:
        r = csv.reader(fp)
        header = next(r)
        rows = list(r)
    trades = []
    in_pos = False
    buy_price = 0.0
    buy_date = ''
    for row in rows:
        if len(row) <= COL_ZDJ:
            continue
        date = row[COL_DATE]
        try:
            close = float(row[COL_CLOSE])
        except:
            continue
        dxcd = row[COL_DXCD]
        zdj = row[COL_ZDJ]
        zdj_first = zdj[0] if len(zdj) > 0 else ''

        if not in_pos:
            # 介入条件：周大局A/H 且 两线之上
            if zdj_first in ZD_AH and dxcd not in TWO_LINE_BELOW:
                in_pos = True
                buy_price = close
                buy_date = date
        else:
            # 退出条件：周大局转Z 或 两线之下
            reason = ''
            if zdj_first == 'Z':
                reason = '周Z退'
            elif dxcd in TWO_LINE_BELOW:
                reason = '两线截断'
            if reason:
                trades.append((buy_date, buy_price, date, close, reason))
                in_pos = False
    # 末尾未平仓
    if in_pos:
        trades.append((buy_date, buy_price, rows[-1][COL_DATE], float(rows[-1][COL_CLOSE]), '未平仓'))
    return trades

# 单只测试
f = '昭明算展/谕组日/谕组日_sh600004.csv'
trades = simulate_one(f)
print(f'=== {f} ===')
print(f'交易次数: {len(trades)}')
wins = 0
total_ret = 0.0
for t in trades[:10]:
    ret = (t[3] - t[1]) / t[1] * 100 if t[1] > 0 else 0
    total_ret += ret
    if ret > 0:
        wins += 1
    print(f'  {t[0]}→{t[2]} 买{t[1]:.2f} 卖{t[3]:.2f} 收益{ret:+.2f}% [{t[4]}]')
if trades:
    all_rets = [(t[3]-t[1])/t[1]*100 for t in trades if t[1]>0]
    wins_all = sum(1 for r in all_rets if r > 0)
    print(f'  全部交易: {len(trades)}笔, 胜{wins_all}笔({wins_all/len(trades)*100:.1f}%), '
          f'平均收益{sum(all_rets)/len(all_rets):+.2f}%, 累计{sum(all_rets):+.2f}%')
