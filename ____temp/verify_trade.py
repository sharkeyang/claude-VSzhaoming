# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

def zhu_class(zhu):
    if zhu.startswith('升') and '连' in zhu: return '升连'
    if zhu.startswith('跌') and '孕' in zhu: return '跌孕'
    if zhu.startswith('(人)'): return '阴阳阴'
    if zhu.startswith('(升)人') or zhu.startswith('(跌)人'): return '人排'
    return '其他'

def is_entry(row):
    """入场条件: 基线 + 入管判定过滤"""
    dxcd = row[8]
    dxzc = int(row[14])
    hx0 = row[9][0]
    za = int(row[13])
    zhu = row[10]
    if dxcd not in ('上','忐'): return False
    if dxzc <= 0: return False
    if hx0 not in ('a','b','r'): return False
    # 入管判定过滤
    zc = zhu_class(zhu)
    if za == 1: return False  # DTZA=1不考虑入管
    if za == 2: return zc in ('升连','跌孕')
    if za >= 3: return zc != '阴阳阴'
    return False

def is_exit(row):
    """退出条件: 跌管退出(乙ZA<0/丙+DTZA<=-2) 或 冲高回落减仓(升管内跌排)"""
    hx0 = row[9][0]
    za = int(row[13])
    zhu = row[10]
    # 跌管退出
    if (hx0 == 'b' and za < 0) or hx0 == 'c':
        if za <= -2:
            return '跌管退出'
    # 冲高回落减仓
    if hx0 in ('a','b','r') and za > 0:
        if zhu.startswith('跌'):
            return '冲高回落减仓'
    return None

# 交易模拟
MAX_HOLD = 20
trades = []
n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        if not is_entry(row):
            continue
        try:
            entry_price = float(row[1])  # 入场价=当日收盘
        except:
            continue
        # 持有, 逐日检查退出
        exit_price = None
        exit_reason = None
        for j in range(i+1, min(i+1+MAX_HOLD, len(rows))):
            rj = rows[j]
            reason = is_exit(rj)
            if reason:
                try:
                    exit_price = float(rj[1])
                except:
                    exit_price = None
                exit_reason = reason
                break
        if exit_price is None:
            # 未触发退出, 用最大持有日收盘
            try:
                exit_price = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
            except:
                continue
            exit_reason = '最大持有'
        ret = (exit_price - entry_price) / entry_price * 100
        trades.append((ret, exit_reason))
    n += 1

print('总文件:', n)
print('总交易数:', len(trades))
if trades:
    wins = sum(1 for r,_ in trades if r > 0)
    losses = sum(1 for r,_ in trades if r <= 0)
    print(f'盈利交易: {wins} ({wins/len(trades)*100:.2f}%)')
    print(f'亏损交易: {losses} ({losses/len(trades)*100:.2f}%)')
    print(f'成功率(收益>0): {wins/len(trades)*100:.2f}%')
    avg_ret = sum(r for r,_ in trades)/len(trades)
    print(f'平均收益率: {avg_ret:.3f}%')
    # 按退出原因统计
    by_reason = defaultdict(list)
    for r,reason in trades:
        by_reason[reason].append(r)
    print('\n按退出原因:')
    for reason, rets in by_reason.items():
        w = sum(1 for r in rets if r > 0)
        print(f'  {reason}: n={len(rets)}, 成功率={w/len(rets)*100:.2f}%, 平均收益={sum(rets)/len(rets):.3f}%')
