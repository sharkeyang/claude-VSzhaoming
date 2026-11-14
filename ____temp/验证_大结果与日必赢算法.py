# -*- coding: utf-8 -*-
"""
验证两个算法（2026-11-14 用户提出）：
  算法1（大结果算法）：WXAB>0且WXZB>0 + 不满足(DXZD<0且DXZC<0)
  算法2（日必赢算法）：从多持介入，空截不退出，空持/多截退出

数据：昭明算展/谕组日/谕组日_*.csv（GBK，135列）
列索引（元数据权威）：
  0=日期, 5=涨幅, 16=日ZA, 17=日ZC, 18=日ZE, 28=次日高幅
  68=DTZB, 69=DTZD, 71=DTCD
  89=周ZA, 90=周ZB, 91=周ZC, 92=周ZD, 95=周AB
"""
import csv, glob, os, sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')

def load_rows(path):
    with open(path, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)  # 表头
        return list(r)

def parse_int(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0

def calc_ri_ying(rows):
    """用底层列重新计算日层赢状态（多持/多截/空持/空截），返回每行状态列表。
    状态机（神谕代码）：
      多持：DXZE>0 + 两线之上(BTZD>0且BTZC>0) 或 中间区从C+D降入
      多截：DXZE>0 + 两线之下(BTZD<0且BTZC<0) 或 中间区从C-D升入
      空持：DXZE<0 + 两线之下(BTZD<0且BTZC<0) 或 中间区从C-D升入
      空截：DXZE<0 + 两线之上(BTZD>0且BTZC>0) 或 中间区从C+D降入
    中间区路径：需要历史状态判断从哪边进入。
    """
    states = []
    prev_state = None
    for row in rows:
        ze = parse_int(row[18])
        zd = parse_int(row[69])
        zc = parse_int(row[17])
        cd = parse_int(row[71])
        # 两线之上/之下
        if zd > 0 and zc > 0:
            zone = 'C+D'   # 两线之上
        elif zd < 0 and zc < 0:
            zone = 'C-D'   # 两线之下
        else:
            zone = 'MID'   # 中间区
        # 判断状态
        if ze > 0:
            # 多头策略
            if zone == 'C+D':
                state = '多持'
            elif zone == 'C-D':
                state = '多截'
            else:
                # 中间区：按路径
                if cd > 0:
                    # 多头排列，价格在DJC下、DJD上
                    if abs(zc) < abs(zd):
                        state = '多持'   # 刚跌破DJC，从C+D降入
                    else:
                        state = '多截'   # 刚站上DJD，从C-D升入
                else:
                    # 空头排列，价格在DJD下、DJC上
                    if abs(zd) < abs(zc):
                        state = '多持'   # 刚跌破DJD，从C+D降入
                    else:
                        state = '多截'   # 刚站上DJC，从C-D升入
        else:
            # 空头策略
            if zone == 'C-D':
                state = '空持'
            elif zone == 'C+D':
                state = '空截'
            else:
                # 中间区：按路径（镜面对称）
                if cd < 0:
                    # 空头排列，价格在DJC上、DJD下
                    if abs(zd) < abs(zc):
                        state = '空截'   # 刚跌破DJD，从C+D降入
                    else:
                        state = '空持'   # 刚站上DJC，从C-D升入
                else:
                    # 多头排列，价格在DJD上、DJC下
                    if abs(zc) < abs(zd):
                        state = '空截'   # 刚跌破DJC，从C+D降入
                    else:
                        state = '空持'   # 刚站上DJD，从C-D升入
        states.append(state)
        prev_state = state
    return states

def simulate_alg2(rows, states):
    """算法2：从多持介入，空截不退出，空持/多截退出。
    返回：每笔交易的(介入日, 退出日, 累计涨幅, 持有天数)
    """
    trades = []
    in_pos = False
    entry_idx = None
    entry_price = None
    for i, row in enumerate(rows):
        state = states[i]
        price = parse_int(row[1]) if row[1] else 0
        if not in_pos:
            # 未持仓：多持时介入
            if state == '多持':
                in_pos = True
                entry_idx = i
                entry_price = price if price else 0
        else:
            # 已持仓：空持/多截退出
            if state == '空持' or state == '多截':
                exit_price = price if price else 0
                if entry_price and exit_price:
                    ret = (exit_price - entry_price) / entry_price * 100
                else:
                    ret = 0
                trades.append((rows[entry_idx][0], row[0], ret, i - entry_idx))
                in_pos = False
    return trades

def simulate_alg1(rows):
    """算法1：WXAB>0且WXZB>0 + 不满足(DXZD<0且DXZC<0) 时持有。
    返回：每笔交易的(介入日, 退出日, 累计涨幅, 持有天数)
    """
    trades = []
    in_pos = False
    entry_idx = None
    entry_price = None
    for i, row in enumerate(rows):
        wxab = parse_int(row[95])
        wxzb = parse_int(row[90])
        dxzd = parse_int(row[69])
        dxzc = parse_int(row[17])
        cond1 = wxab > 0 and wxzb > 0
        cond2 = not (dxzd < 0 and dxzc < 0)
        hold = cond1 and cond2
        price = parse_int(row[1]) if row[1] else 0
        if not in_pos:
            if hold:
                in_pos = True
                entry_idx = i
                entry_price = price if price else 0
        else:
            if not hold:
                exit_price = price if price else 0
                if entry_price and exit_price:
                    ret = (exit_price - entry_price) / entry_price * 100
                else:
                    ret = 0
                trades.append((rows[entry_idx][0], row[0], ret, i - entry_idx))
                in_pos = False
    return trades

def stats(trades, label):
    if not trades:
        print(f'{label}: 无交易')
        return
    rets = [t[2] for t in trades]
    days = [t[3] for t in trades]
    pos = sum(1 for r in rets if r > 0)
    total = len(rets)
    avg = sum(rets) / total
    med = sorted(rets)[total // 2]
    cum = sum(rets)
    avg_days = sum(days) / total
    print(f'{label}:')
    print(f'  交易数={total}, 正收益={pos} ({pos/total*100:.1f}%), 负收益={total-pos} ({(total-pos)/total*100:.1f}%)')
    print(f'  平均收益={avg:.2f}%, 中位收益={med:.2f}%, 累计收益={cum:.1f}%')
    print(f'  平均持有天数={avg_days:.1f}')

def per_stock_stats(trades_by_stock, label):
    """按股票统计：策略累计收益为正的股票占比（与文档§6.8"62%为正"口径一致）"""
    n_stock = len(trades_by_stock)
    if n_stock == 0:
        print(f'{label}: 无股票')
        return
    cum_rets = []
    n_trades = 0
    for trades in trades_by_stock.values():
        cum = sum(t[2] for t in trades)
        cum_rets.append(cum)
        n_trades += len(trades)
    pos = sum(1 for c in cum_rets if c > 0)
    avg_cum = sum(cum_rets) / n_stock
    med_cum = sorted(cum_rets)[n_stock // 2]
    print(f'{label}（按股票统计）:')
    print(f'  股票数={n_stock}, 累计收益为正={pos} ({pos/n_stock*100:.1f}%), 累计为负={n_stock-pos} ({(n_stock-pos)/n_stock*100:.1f}%)')
    print(f'  每股累计收益平均={avg_cum:.1f}%, 中位={med_cum:.1f}%')
    print(f'  总交易数={n_trades}')

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'文件数: {len(files)}')
    all_trades_alg1 = []
    all_trades_alg2 = []
    trades_by_stock_alg1 = {}
    trades_by_stock_alg2 = {}
    n = 0
    for f in files:
        rows = load_rows(f)
        if len(rows) < 100:
            continue
        n += 1
        code = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        # 算法1
        trades1 = simulate_alg1(rows)
        all_trades_alg1.extend(trades1)
        trades_by_stock_alg1[code] = trades1
        # 算法2
        states = calc_ri_ying(rows)
        trades2 = simulate_alg2(rows, states)
        all_trades_alg2.extend(trades2)
        trades_by_stock_alg2[code] = trades2
        if n % 500 == 0:
            print(f'  已处理 {n} 个文件...')
    print(f'有效文件数: {n}')
    print('=' * 60)
    stats(all_trades_alg1, '算法1（大结果算法）')
    print('-' * 60)
    stats(all_trades_alg2, '算法2（日必赢算法）')
    print('=' * 60)
    per_stock_stats(trades_by_stock_alg1, '算法1（大结果算法）')
    print('-' * 60)
    per_stock_stats(trades_by_stock_alg2, '算法2（日必赢算法）')

if __name__ == '__main__':
    main()