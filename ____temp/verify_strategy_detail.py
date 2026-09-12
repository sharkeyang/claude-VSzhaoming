# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 详细比较策略2(等下破再退出) vs 策略4(下破后重站再持有)
# 以及策略3(持有5日) vs 策略1(立即退出)
# 用更严格定义: 下破后重新站上(日ZA>0)再持有
results = defaultdict(list)

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
        hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
        if hx0 not in ('a','b','r') or za <= 0: continue
        if not (zhu.startswith('跌') and '连' in zhu): continue
        try: cur_close = float(row[1])
        except: continue
        # 下破DJA
        brk_idx = -1
        for j in range(i+1, min(i+10, len(rows))):
            if int(rows[j][13]) < 0:
                brk_idx = j
                break
        # 下破后重新站上
        rest_idx = -1
        if brk_idx != -1:
            for j in range(brk_idx+1, min(brk_idx+6, len(rows))):
                if int(rows[j][13]) > 0:
                    rest_idx = j
                    break
        # 策略1: 立即退出(0)
        results['策略1:立即退出'].append(0)
        # 策略2: 等下破再退出
        if brk_idx != -1:
            try:
                brk_close = float(rows[brk_idx][1])
                results['策略2:等下破再退出'].append((brk_close-cur_close)/cur_close*100)
            except: pass
        # 策略3: 持有5日
        try:
            exit5 = float(rows[min(i+5, len(rows)-1)][1])
            results['策略3:持有5日'].append((exit5-cur_close)/cur_close*100)
        except: pass
        # 策略4: 下破后重站再持有
        if brk_idx != -1:
            if rest_idx != -1:
                # 重新站上, 持有到5日
                try:
                    exit4 = float(rows[min(i+5, len(rows)-1)][1])
                    results['策略4:重站再持有'].append((exit4-cur_close)/cur_close*100)
                except: pass
            else:
                # 未重新站上, 下破退出
                try:
                    brk_close = float(rows[brk_idx][1])
                    results['策略4:重站再持有'].append((brk_close-cur_close)/cur_close*100)
                except: pass
        else:
            # 未下破, 持有到5日
            try:
                exit4 = float(rows[min(i+5, len(rows)-1)][1])
                results['策略4:重站再持有'].append((exit4-cur_close)/cur_close*100)
            except: pass
    n += 1

print('总文件:', n)
print('\n=== DJA之上跌连后 策略详细比较 ===')
for name, rets in results.items():
    rets.sort()
    wins = sum(1 for r in rets if r > 0)
    losses = [r for r in rets if r <= 0]
    avg_loss = sum(losses)/len(losses) if losses else 0
    worst5 = rets[:int(len(rets)*0.05)]
    avg_worst5 = sum(worst5)/len(worst5)
    # 收益分布
    p25 = rets[int(len(rets)*0.25)]
    p50 = rets[int(len(rets)*0.50)]
    p75 = rets[int(len(rets)*0.75)]
    print(f'{name}: n={len(rets)}, 成功率={wins/len(rets)*100:.2f}%, 平均={sum(rets)/len(rets):.3f}%, 平均亏损={avg_loss:.3f}%, 最差5%={avg_worst5:.3f}%, 分位[25/50/75]={p25:.2f}/{p50:.2f}/{p75:.2f}%')
