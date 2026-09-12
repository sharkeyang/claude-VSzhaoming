# -*- coding: utf-8 -*-
"""
审计日冲策略文档：DXZE>0+DXZC>0 持有周期胜率（高波池）
====================================================
复现日冲策略文档的持有周期统计：
- 入场：条件满足（ZE>0+ZC>0）时，以前一日收盘价买入
- 持有：每日涨幅复利，剔除停牌日
- 出场：条件不满足（ZE<=0或ZC<=0）时卖出
- 胜率：持有期总收益>0的周期占比
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

# ============ 统计容器 ============
# 持有周期统计
total_cycles = 0
win_cycles = 0
sum_ret = 0.0
sum_median = []
sum_days = 0
# 条件覆盖率
total_days = 0
cond_days = 0

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    # 提取字段
    zes = [to_f(rows[i][15]) for i in range(n)]
    zcs = [to_f(rows[i][14]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]  # 涨幅

    # 识别持有周期
    i = 0
    while i < n:
        ze = zes[i]; zc = zcs[i]
        if ze is None or zc is None:
            i += 1; continue
        total_days += 1
        if ze > 0 and zc > 0:
            cond_days += 1
        # 入场：条件满足
        if ze > 0 and zc > 0:
            # 持有周期开始
            start = i
            ret = 1.0
            days = 0
            while i < n:
                ze2 = zes[i]; zc2 = zcs[i]
                zf2 = zfs[i]
                if ze2 is None or zc2 is None: break
                if not (ze2 > 0 and zc2 > 0): break  # 条件不满足，出场
                if zf2 is not None:
                    ret *= (1 + zf2/100)
                    days += 1
                i += 1
            total_cycles += 1
            if ret > 1.0: win_cycles += 1
            sum_ret += (ret - 1) * 100
            sum_median.append((ret - 1) * 100)
            sum_days += days
        else:
            i += 1

print(f'高波池文件: {files_core}')
print()

# 输出
print('='*75)
print('【日冲策略文档验证：DXZE>0+DXZC>0 持有周期】')
print('='*75)
print(f'持有周期数: {total_cycles:,}')
print(f'胜率(总收益>0): {win_cycles/total_cycles*100:.2f}%')
print(f'均收益: {sum_ret/total_cycles:.2f}%')
sum_median.sort()
mid = sum_median[len(sum_median)//2] if sum_median else 0
print(f'中位数收益: {mid:.2f}%')
print(f'平均持有天数: {sum_days/total_cycles:.1f}天')
print(f'条件覆盖率: {cond_days/total_days*100:.2f}%')
print()
print('【日冲策略文档值】')
print('胜率: 92.5%')
print('均收益: 9.35%')
print('中位数: 3.19%')
print('平均持有: 12.3天')
print('条件覆盖率: 36.9%')