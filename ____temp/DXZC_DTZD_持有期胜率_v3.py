# -*- coding: utf-8 -*-
"""
验证 DXZC>0 + DTZD>0 持有到条件不满足的胜率（均线价进出 v3）
===============================================================
- 入场：条件满足的当天，以均线价（前一日收盘价）入场
- 出场：条件触发的当天，以均线价（前一日收盘价）出场
- 胜率口径：持有期总收益>0
- 高波池 Qic+Qim+Qit
"""
import csv, os, json, io
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_DXZC_DTZD_持有期胜率_v3.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

def calc_ema60(prices):
    alpha = 2/61
    ema = [prices[0]]
    for p in prices[1:]:
        ema.append(alpha * p + (1-alpha) * ema[-1])
    return ema

files_done = 0

trade_returns = {
    'ZC>0': [],
    'ZC>0+DTZD>0': [],
    'ZE>0+ZC>0(V1必赢)': [],
}
trade_days = {
    'ZC>0': [],
    'ZC>0+DTZD>0': [],
    'ZE>0+ZC>0(V1必赢)': [],
}

for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            header = next(r)
            idx_close = header.index('收')
            idx_zc = header.index('日ZC')
            idx_ze = header.index('日ZE')

            prices = []
            zcs = []
            zes = []
            for row in r:
                if len(row) <= max(idx_close, idx_zc, idx_ze):
                    continue
                try:
                    close = float(row[idx_close])
                    zc = float(row[idx_zc])
                    ze = float(row[idx_ze])
                except (ValueError, IndexError):
                    continue
                prices.append(close)
                zcs.append(zc)
                zes.append(ze)

            if len(prices) < 61:
                continue

            ema60 = calc_ema60(prices)
            dtzds = []
            dtzd = 0
            for i in range(len(prices)):
                if prices[i] > ema60[i]:
                    dtzd += 1
                else:
                    dtzd = 0
                dtzds.append(dtzd)

            # 策略1: ZC>0 入场，ZC<=0 出场
            # 均线价进出：条件满足当天以均线价（前一日收盘价）入场
            in_trade = False
            entry_price = None
            entry_idx = -1
            for i in range(len(prices)):
                if not in_trade:
                    if zcs[i] > 0:
                        in_trade = True
                        entry_idx = i
                        entry_price = prices[i-1] if i > 0 else prices[i]
                else:
                    if zcs[i] <= 0:
                        exit_price = prices[i-1] if i > 0 else prices[i]
                        ret = (exit_price - entry_price) / entry_price * 100
                        trade_returns['ZC>0'].append(ret)
                        trade_days['ZC>0'].append(i - entry_idx)
                        in_trade = False
                        entry_price = None
            if in_trade and entry_price is not None:
                ret = (prices[-1] - entry_price) / entry_price * 100
                trade_returns['ZC>0'].append(ret)
                trade_days['ZC>0'].append(len(prices) - 1 - entry_idx)

            # 策略2: ZC>0+DTZD>0 入场，ZC<=0 或 DTZD<=0 出场
            in_trade = False
            entry_price = None
            entry_idx = -1
            for i in range(len(prices)):
                if not in_trade:
                    if zcs[i] > 0 and dtzds[i] > 0:
                        in_trade = True
                        entry_idx = i
                        entry_price = prices[i-1] if i > 0 else prices[i]
                else:
                    if zcs[i] <= 0 or dtzds[i] <= 0:
                        exit_price = prices[i-1] if i > 0 else prices[i]
                        ret = (exit_price - entry_price) / entry_price * 100
                        trade_returns['ZC>0+DTZD>0'].append(ret)
                        trade_days['ZC>0+DTZD>0'].append(i - entry_idx)
                        in_trade = False
                        entry_price = None
            if in_trade and entry_price is not None:
                ret = (prices[-1] - entry_price) / entry_price * 100
                trade_returns['ZC>0+DTZD>0'].append(ret)
                trade_days['ZC>0+DTZD>0'].append(len(prices) - 1 - entry_idx)

            # 策略3: ZE>0+ZC>0 入场，ZE<=0 或 ZC<=0 出场（V1必赢）
            in_trade = False
            entry_price = None
            entry_idx = -1
            for i in range(len(prices)):
                if not in_trade:
                    if zes[i] > 0 and zcs[i] > 0:
                        in_trade = True
                        entry_idx = i
                        entry_price = prices[i-1] if i > 0 else prices[i]
                else:
                    if zes[i] <= 0 or zcs[i] <= 0:
                        exit_price = prices[i-1] if i > 0 else prices[i]
                        ret = (exit_price - entry_price) / entry_price * 100
                        trade_returns['ZE>0+ZC>0(V1必赢)'].append(ret)
                        trade_days['ZE>0+ZC>0(V1必赢)'].append(i - entry_idx)
                        in_trade = False
                        entry_price = None
            if in_trade and entry_price is not None:
                ret = (prices[-1] - entry_price) / entry_price * 100
                trade_returns['ZE>0+ZC>0(V1必赢)'].append(ret)
                trade_days['ZE>0+ZC>0(V1必赢)'].append(len(prices) - 1 - entry_idx)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('持有到条件不满足的胜率对比（均线价进出v3，高波池）')
out('=' * 100)
out('')
out(f'| {"策略":<30s} | {"交易次数":>8s} | {"胜率":>6s} | {"均收益":>7s} | {"中位收益":>8s} | {"均持有天":>8s} | {"最大亏损":>8s} | {"最大盈利":>8s} |')
out(f'|{"":->30s}|{"":->8s}:|{"":->6s}:|{"":->7s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')

for label in ['ZC>0', 'ZC>0+DTZD>0', 'ZE>0+ZC>0(V1必赢)']:
    vals = np.array(trade_returns[label])
    days = np.array(trade_days[label])
    n = len(vals)
    if n == 0:
        continue
    win_rate = (vals > 0).sum() / n * 100
    mean_ret = np.mean(vals)
    median_ret = np.median(vals)
    max_loss = np.min(vals)
    max_gain = np.max(vals)
    mean_days = np.mean(days)
    out(f'| {label:<30s} | {n:>8,d} | {win_rate:>5.1f}% | {mean_ret:>6.2f}% | {median_ret:>7.2f}% | {mean_days:>7.1f} | {max_loss:>7.2f}% | {max_gain:>7.2f}% |')

out('')
out('=' * 100)
out('收益分布详情')
out('=' * 100)
out('')
out(f'| {"策略":<30s} | {"P5":>6s} | {"P10":>6s} | {"P25":>6s} | {"P50":>6s} | {"P75":>6s} | {"P90":>6s} | {"P95":>6s} |')
out(f'|{"":->30s}|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|')

for label in ['ZC>0', 'ZC>0+DTZD>0', 'ZE>0+ZC>0(V1必赢)']:
    vals = np.array(trade_returns[label])
    n = len(vals)
    if n == 0:
        continue
    p5 = np.percentile(vals, 5)
    p10 = np.percentile(vals, 10)
    p25 = np.percentile(vals, 25)
    p50 = np.percentile(vals, 50)
    p75 = np.percentile(vals, 75)
    p90 = np.percentile(vals, 90)
    p95 = np.percentile(vals, 95)
    out(f'| {label:<30s} | {p5:>5.2f}% | {p10:>5.2f}% | {p25:>5.2f}% | {p50:>5.2f}% | {p75:>5.2f}% | {p90:>5.2f}% | {p95:>5.2f}% |')

out('')
out('=' * 100)
out('持有天数分布')
out('=' * 100)
out('')
out(f'| {"策略":<30s} | {"均持有天":>8s} | {"中位持有天":>9s} | {"P25":>6s} | {"P75":>6s} | {"1-3天":>7s} | {"4-7天":>7s} | {"8-14天":>8s} | {"15天+":>7s} |')
out(f'|{"":->30s}|{"":->8s}:|{"":->9s}:|{"":->6s}:|{"":->6s}:|{"":->7s}:|{"":->7s}:|{"":->8s}:|{"":->7s}:|')

for label in ['ZC>0', 'ZC>0+DTZD>0', 'ZE>0+ZC>0(V1必赢)']:
    days = np.array(trade_days[label])
    n = len(days)
    if n == 0:
        continue
    mean_d = np.mean(days)
    median_d = np.median(days)
    p25_d = np.percentile(days, 25)
    p75_d = np.percentile(days, 75)
    d1_3 = (days <= 3).sum() / n * 100
    d4_7 = ((days >= 4) & (days <= 7)).sum() / n * 100
    d8_14 = ((days >= 8) & (days <= 14)).sum() / n * 100
    d15 = (days >= 15).sum() / n * 100
    out(f'| {label:<30s} | {mean_d:>7.1f} | {median_d:>8.0f} | {p25_d:>5.0f} | {p75_d:>5.0f} | {d1_3:>6.1f}% | {d4_7:>6.1f}% | {d8_14:>7.1f}% | {d15:>6.1f}% |')

OUTF.close()
print('Done')