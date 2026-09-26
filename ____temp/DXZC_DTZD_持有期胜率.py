# -*- coding: utf-8 -*-
"""
验证 DXZC>0 + DTZD>0 持有到条件不满足的胜率
=============================================
- 入场条件：DXZC>0（且可选 DTZD>0 / ZE>0）
- 出场条件：条件不满足时（ZC<=0 或 DTZD<=0 或 ZE<=0）
- 统计：持有期累计收益、胜率（收益>0占比）
- 高波池 Qic+Qim+Qit
"""
import csv, os, json, io
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_DXZC_DTZD_持有期胜率.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

files_done = 0

# 各策略的持有期收益列表
trade_returns = {
    'ZC>0': [],
    'ZC>0+DTZD>0': [],
    'ZE>0+ZC>0(V1必赢)': [],
}
# 各策略的持有天数
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
            # 固定列索引（对照 _产出物\_工具\元数据_vba数据映射_日类.md，勿信表头名）
            idx_close = 1    # 收
            idx_zc = 14      # 日ZC
            idx_ze = 15      # 日ZE
            idx_涨幅 = 5     # 涨幅
            idx_dtzd = 63    # DTZD（JZ vs JD交叉天数，2026-09-24新增导出）

            prices = []
            zcs = []
            zes = []
            dtzds = []
            for row in r:
                if len(row) <= max(idx_close, idx_zc, idx_ze, idx_涨幅, idx_dtzd):
                    continue
                try:
                    close = float(row[idx_close])
                    zc = float(row[idx_zc])
                    ze = float(row[idx_ze])
                    dtzd = float(row[idx_dtzd])
                except (ValueError, IndexError):
                    continue
                prices.append(close)
                zcs.append(zc)
                zes.append(ze)
                dtzds.append(dtzd)

            if len(prices) < 1:
                continue

            # 策略1: ZC>0 入场，ZC<=0 出场
            in_trade = False
            entry_idx = -1
            for i in range(len(prices)):
                if not in_trade:
                    if zcs[i] > 0:
                        in_trade = True
                        entry_idx = i
                else:
                    if zcs[i] <= 0:
                        ret = (prices[i] - prices[entry_idx]) / prices[entry_idx] * 100
                        trade_returns['ZC>0'].append(ret)
                        trade_days['ZC>0'].append(i - entry_idx)
                        in_trade = False
            if in_trade:
                ret = (prices[-1] - prices[entry_idx]) / prices[entry_idx] * 100
                trade_returns['ZC>0'].append(ret)
                trade_days['ZC>0'].append(len(prices) - 1 - entry_idx)

            # 策略2: ZC>0+DTZD>0 入场，ZC<=0 或 DTZD<=0 出场
            in_trade = False
            entry_idx = -1
            for i in range(len(prices)):
                if not in_trade:
                    if zcs[i] > 0 and dtzds[i] > 0:
                        in_trade = True
                        entry_idx = i
                else:
                    if zcs[i] <= 0 or dtzds[i] <= 0:
                        ret = (prices[i] - prices[entry_idx]) / prices[entry_idx] * 100
                        trade_returns['ZC>0+DTZD>0'].append(ret)
                        trade_days['ZC>0+DTZD>0'].append(i - entry_idx)
                        in_trade = False
            if in_trade:
                ret = (prices[-1] - prices[entry_idx]) / prices[entry_idx] * 100
                trade_returns['ZC>0+DTZD>0'].append(ret)
                trade_days['ZC>0+DTZD>0'].append(len(prices) - 1 - entry_idx)

            # 策略3: ZE>0+ZC>0 入场，ZE<=0 或 ZC<=0 出场（V1必赢）
            in_trade = False
            entry_idx = -1
            for i in range(len(prices)):
                if not in_trade:
                    if zes[i] > 0 and zcs[i] > 0:
                        in_trade = True
                        entry_idx = i
                else:
                    if zes[i] <= 0 or zcs[i] <= 0:
                        ret = (prices[i] - prices[entry_idx]) / prices[entry_idx] * 100
                        trade_returns['ZE>0+ZC>0(V1必赢)'].append(ret)
                        trade_days['ZE>0+ZC>0(V1必赢)'].append(i - entry_idx)
                        in_trade = False
            if in_trade:
                ret = (prices[-1] - prices[entry_idx]) / prices[entry_idx] * 100
                trade_returns['ZE>0+ZC>0(V1必赢)'].append(ret)
                trade_days['ZE>0+ZC>0(V1必赢)'].append(len(prices) - 1 - entry_idx)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('持有到条件不满足的胜率对比（高波池）')
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
out(f'| {"策略":<30s} | {"P10":>6s} | {"P25":>6s} | {"P50":>6s} | {"P75":>6s} | {"P90":>6s} | {"收益>3%":>7s} | {"收益>5%":>7s} | {"收益>10%":>7s} |')
out(f'|{"":->30s}|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->7s}:|{"":->7s}:|{"":->7s}:|')

for label in ['ZC>0', 'ZC>0+DTZD>0', 'ZE>0+ZC>0(V1必赢)']:
    vals = np.array(trade_returns[label])
    n = len(vals)
    if n == 0:
        continue
    p10 = np.percentile(vals, 10)
    p25 = np.percentile(vals, 25)
    p50 = np.percentile(vals, 50)
    p75 = np.percentile(vals, 75)
    p90 = np.percentile(vals, 90)
    gt3 = (vals > 3).sum() / n * 100
    gt5 = (vals > 5).sum() / n * 100
    gt10 = (vals > 10).sum() / n * 100
    out(f'| {label:<30s} | {p10:>5.2f}% | {p25:>5.2f}% | {p50:>5.2f}% | {p75:>5.2f}% | {p90:>5.2f}% | {gt3:>6.1f}% | {gt5:>6.1f}% | {gt10:>6.1f}% |')

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