# -*- coding: utf-8 -*-
"""拆解3：周层大局细分 A入 vs H持 分别看收益
+ 按DXCD介入时状态细分（上/中/忐/下）
策略：A/H介入 + 忠/忑截断 + Z退
"""
import csv, sys, io, os, glob, time
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL_DATE = 0
COL_CLOSE = 1
COL_DXCD = 8
COL_ZDJ = 81
TWO_LINE_BELOW = {'忠', '忑'}
ZD_AH = {'A', 'H'}

def load_rows(filepath):
    try:
        with open(filepath, encoding='gbk') as fp:
            r = csv.reader(fp)
            next(r)
            return list(r)
    except:
        return None

files = sorted(glob.glob('昭明算展/谕组日/谕组日_*.csv'))
t0 = time.time()

# 按介入时周大局首字符(A/H) × 介入时DXCD 细分
seg_rets = defaultdict(list)  # key=(zdj_first, dxcd_at_buy)
# 也按退出原因细分
exit_seg = defaultdict(list)  # key=(zdj_first, exit_reason)

for i, f in enumerate(files):
    rows = load_rows(f)
    if not rows:
        continue
    in_pos = False
    buy_price = 0.0
    buy_zdj = ''
    buy_dxcd = ''
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
            if zdj_first in ZD_AH and dxcd not in TWO_LINE_BELOW:
                in_pos = True
                buy_price = close
                buy_zdj = zdj_first
                buy_dxcd = dxcd
        else:
            exit_reason = ''
            if zdj_first == 'Z':
                exit_reason = '周Z退'
            elif dxcd in TWO_LINE_BELOW:
                exit_reason = '两线截断'
            if exit_reason:
                if buy_price > 0:
                    ret = (close - buy_price) / buy_price * 100
                    seg_rets[(buy_zdj, buy_dxcd)].append(ret)
                    exit_seg[(buy_zdj, exit_reason)].append(ret)
                in_pos = False
    if (i+1) % 1000 == 0:
        print(f'  进度 {i+1}/{len(files)} 用时{time.time()-t0:.0f}s')

print(f'\n========== 拆解3：按介入状态细分 ==========')
print(f'用时: {time.time()-t0:.0f}s')

print(f'\n--- 按介入时周大局首字符(A入/H持) ---')
for zdj in ['A', 'H']:
    allr = []
    for dxcd in ['上', '中', '忐', '下']:
        allr.extend(seg_rets.get((zdj, dxcd), []))
    n = len(allr)
    if n == 0:
        continue
    w = sum(1 for r in allr if r > 0)
    print(f'  {zdj}入/持: {n}笔 胜率{w/n*100:.1f}% 平均{sum(allr)/n:+.3f}% 中位{sorted(allr)[n//2]:+.3f}% 累计{sum(allr):+.1f}% 大赚{sum(1 for r in allr if r>10)/n*100:.1f}% 大亏{sum(1 for r in allr if r<-10)/n*100:.1f}%')

print(f'\n--- 按介入时周大局×DXCD细分 ---')
print(f'{"介入状态":<12} {"笔数":>7} {"胜率":>7} {"平均":>9} {"中位":>9} {"累计":>11} {"大赚%":>7} {"大亏%":>7}')
for zdj in ['A', 'H']:
    for dxcd in ['上', '中', '忐', '下']:
        rets = seg_rets.get((zdj, dxcd), [])
        n = len(rets)
        if n == 0:
            continue
        w = sum(1 for r in rets if r > 0)
        print(f'  {zdj}+{dxcd:<8} {n:>7} {w/n*100:>6.1f}% {sum(rets)/n:>+8.3f}% {sorted(rets)[n//2]:>+8.3f}% {sum(rets):>+10.1f}% {sum(1 for r in rets if r>10)/n*100:>6.1f}% {sum(1 for r in rets if r<-10)/n*100:>6.1f}%')

print(f'\n--- 按介入时周大局×退出原因 ---')
print(f'{"介入→退出":<16} {"笔数":>7} {"胜率":>7} {"平均":>9} {"中位":>9} {"累计":>11}')
for zdj in ['A', 'H']:
    for reason in ['两线截断', '周Z退', '未平仓']:
        rets = exit_seg.get((zdj, reason), [])
        n = len(rets)
        if n == 0:
            continue
        w = sum(1 for r in rets if r > 0)
        print(f'  {zdj}→{reason:<10} {n:>7} {w/n*100:>6.1f}% {sum(rets)/n:>+8.3f}% {sorted(rets)[n//2]:>+8.3f}% {sum(rets):>+10.1f}%')
