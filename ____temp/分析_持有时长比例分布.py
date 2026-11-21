# -*- coding: utf-8 -*-
"""
对每只股票计算持有时长比例，分析分布。
算法：仓日类多持（§6.8）
  介入：多持 且 DTZE>0（上破DJE）
  持有：多持 或 空截（两线之上，中间区降入不退出）
  退出：空持 或 多截（两线之下）
列索引： [0]日期 [17]日ZC [69]DTZD [18]日ZE
"""
import csv, sys, glob, os, statistics
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组日'

def parse_int(s):
    try: return int(float(s))
    except: return 0

def load_stock(path):
    rows = []
    with open(path, encoding='gbk') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 70: continue
            try:
                dtzc = parse_int(row[17])
                dtzd = parse_int(row[69])
                dtze = parse_int(row[18])
            except: continue
            rows.append((dtzc, dtzd, dtze))
    return rows

def holding_ratio(rows):
    total = len(rows)
    if total < 50: return None
    holding = 0
    is_hold = False
    for dtzc, dtzd, dtze in rows:
        above_two = dtzd > 0 and dtzc > 0
        below_two = dtzd < 0 and dtzc < 0
        if not is_hold:
            if above_two and dtze > 0:
                is_hold = True
        else:
            if below_two:
                is_hold = False
        if is_hold:
            holding += 1
    return holding / total

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
    ratios = []
    for i, fp in enumerate(files):
        rows = load_stock(fp)
        r = holding_ratio(rows)
        if r is not None:
            ratios.append(r)
        if (i+1) % 500 == 0:
            print(f'  已处理 {i+1}/{len(files)}')
    n = len(ratios)
    print(f'\n有效股票数: {n}')
    print(f'持有时长比例分布:')
    print(f'  最小: {min(ratios)*100:.2f}%')
    print(f'  最大: {max(ratios)*100:.2f}%')
    print(f'  中位: {statistics.median(ratios)*100:.2f}%')
    print(f'  均值: {statistics.mean(ratios)*100:.2f}%')
    print(f'  标准差: {statistics.stdev(ratios)*100:.2f}%')
    # 分位数
    s = sorted(ratios)
    for q in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
        idx = int(q * (n-1))
        print(f'  P{int(q*100):02d}: {s[idx]*100:.2f}%')
    # 直方图分布（按10%区间）
    print(f'\n直方图（每10%区间）:')
    bins = [0]*10
    for r in ratios:
        b = min(int(r*10), 9)
        bins[b] += 1
    for i, cnt in enumerate(bins):
        bar = '#' * int(cnt / max(bins) * 40)
        print(f'  {i*10:2d}-{i*10+10:2d}%: {cnt:5d} ({cnt/n*100:5.2f}%) {bar}')

if __name__ == '__main__':
    main()