# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# DJA之上跌连后的细分策略
# 跌连后: 1.立即退出(踏空) 2.等下破DJA再退出 3.等确认(下破后重新站上再持有)
# 核心: 跌连后下破DJA, 下破后是否重新站上(§2.9.3: 63-68%重新站上)
# 验证: 跌连后下破DJA, 下破后重新站上的概率, 以及不同退出时机的收益
r = defaultdict(lambda:[0,0,0,0.0])  # (策略) -> [样本, 5日创新高, 10日创新高, 5日收益和]

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
        if not (zhu.startswith('跌') and '连' in zhu): continue  # 只看跌连
        try:
            cur_close = float(row[1])
        except:
            continue
        # 策略1: 立即退出(跌连当日收盘)
        # 策略2: 等下破DJA再退出(下破当日收盘)
        # 策略3: 持有到5日(不退出)
        # 策略4: 下破后重新站上再持有(最优?)
        # 5日创新高
        hi5 = 0
        for j in range(i+1, min(i+6, len(rows))):
            try:
                if float(rows[j][1]) > cur_close:
                    hi5 = 1
                    break
            except: pass
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
        # 策略1: 立即退出(跌连当日收盘=cur_close, 收益0)
        r['策略1:跌连立即退出'][0] += 1
        r['策略1:跌连立即退出'][4] += 0
        # 策略2: 等下破DJA再退出
        if brk_idx != -1:
            try:
                brk_close = float(rows[brk_idx][1])
                ret2 = (brk_close - cur_close) / cur_close * 100
            except:
                ret2 = 0
            r['策略2:等下破再退出'][0] += 1
            r['策略2:等下破再退出'][4] += ret2
        # 策略3: 持有到5日
        try:
            exit5 = float(rows[min(i+5, len(rows)-1)][1])
            ret3 = (exit5 - cur_close) / cur_close * 100
        except:
            ret3 = 0
        r['策略3:持有5日'][0] += 1
        r['策略3:持有5日'][4] += ret3
        # 策略4: 下破后重新站上再持有(否则下破退出)
        if brk_idx != -1:
            if rest_idx != -1:
                # 重新站上, 持有到5日
                try:
                    exit4 = float(rows[min(i+5, len(rows)-1)][1])
                    ret4 = (exit4 - cur_close) / cur_close * 100
                except:
                    ret4 = 0
            else:
                # 未重新站上, 下破退出
                try:
                    brk_close = float(rows[brk_idx][1])
                    ret4 = (brk_close - cur_close) / cur_close * 100
                except:
                    ret4 = 0
            r['策略4:下破后重站再持有'][0] += 1
            r['策略4:下破后重站再持有'][4] += ret4
        else:
            # 未下破, 持有到5日
            try:
                exit4 = float(rows[min(i+5, len(rows)-1)][1])
                ret4 = (exit4 - cur_close) / cur_close * 100
            except:
                ret4 = 0
            r['策略4:下破后重站再持有'][0] += 1
            r['策略4:下破后重站再持有'][4] += ret4
    n += 1

print('总文件:', n)
print('\n=== DJA之上跌连后 不同退出策略 ===')
print(f"{'策略':<24}{'样本':>9}{'平均收益':>10}")
for k,(tot,hi5,hi10,sret) in r.items():
    print(f"{k:<24}{tot:>9}{sret/tot:>9.3f}%")
