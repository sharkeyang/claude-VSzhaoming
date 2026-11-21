# -*- coding: utf-8 -*-
"""
按持有时长比例分组，分析各组收益差异。
算法：仓日类多持（§6.8）
  介入：多持 且 DTZE>0（上破DJE）
  持有：多持 或 空截（两线之上）
  退出：空持 或 多截（两线之下）
列索引： [0]日期 [1]收 [17]日ZC [69]DTZD [18]日ZE
"""
import csv, sys, glob, os, statistics
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组日'

def parse_int(s):
    try: return int(float(s))
    except: return 0
def parse_float(s):
    try: return float(s)
    except: return None

def load_stock(path):
    rows = []
    with open(path, encoding='gbk') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 70: continue
            try:
                close = parse_float(row[1])
                dtzc = parse_int(row[17])
                dtzd = parse_int(row[69])
                dtze = parse_int(row[18])
            except: continue
            rows.append((close, dtzc, dtzd, dtze))
    return rows

def analyze(path):
    rows = load_stock(path)
    if len(rows) < 50: return None
    total = len(rows)
    holding = 0
    is_hold = False
    algo_ret = 0.0
    always_ret = 0.0
    prev_close = None
    for close, dtzc, dtzd, dtze in rows:
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
        if prev_close is not None and close is not None and prev_close > 0:
            daily = close / prev_close - 1
            always_ret += daily
            if is_hold:
                algo_ret += daily
        prev_close = close
    return {
        'ratio': holding/total,
        'algo_ret': algo_ret,
        'always_ret': always_ret,
        'algo_win': algo_ret > 0,
        'algo_beats': algo_ret > always_ret,
    }

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
    results = []
    for i, fp in enumerate(files):
        res = analyze(fp)
        if res is not None:
            results.append(res)
        if (i+1) % 500 == 0:
            print(f'  已处理 {i+1}/{len(files)}')
    n = len(results)
    print(f'\n有效股票数: {n}')
    # 按持有时长比例分组
    groups = [(0,0.30),(0.30,0.35),(0.35,0.40),(0.40,0.45),(0.45,0.50),(0.50,0.60),(0.60,1.0)]
    print(f'\n{"分组":<14} {"股票数":>6} {"占比":>7} {"算法中位收益":>12} {"始终持有中位":>12} {"正收益%":>8} {"跑赢%":>7}')
    for lo, hi in groups:
        grp = [r for r in results if lo <= r['ratio'] < hi]
        if not grp: continue
        g = len(grp)
        algo_m = statistics.median([r['algo_ret'] for r in grp])
        always_m = statistics.median([r['always_ret'] for r in grp])
        win = sum(1 for r in grp if r['algo_win'])/g*100
        beat = sum(1 for r in grp if r['algo_beats'])/g*100
        print(f'  {lo*100:.0f}-{hi*100:.0f}%     {g:6d} {g/n*100:6.2f}% {algo_m:12.2f} {always_m:12.2f} {win:7.2f}% {beat:6.2f}%')

if __name__ == '__main__':
    main()