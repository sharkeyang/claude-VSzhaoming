# -*- coding: utf-8 -*-
"""
验证用户算法（仓日类多持）三大命题：
  介入：多持 且 DTZE>0（上破DJE）
  持有：多持 或 空截（两线之上，中间区降入不退出）
  退出：空持 或 多截（两线之下）
命题1：包含所有升势（两线之上持有覆盖率）
命题2：缩短时间跨度（持有时长占比）
命题3：多赚少赔（持有期间收益 vs 始终持有）
列索引（基于实际CSV表头）：
  [0]日期 [1]收 [16]日ZA [17]日ZC [18]日ZE [69]DTZD [28]次日高幅
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
                nxt = parse_float(row[28])
            except: continue
            rows.append((row[0], close, dtzc, dtzd, dtze, nxt))
    return rows

def simulate(rows):
    holding = False
    states = []
    for date, close, dtzc, dtzd, dtze, nxt in rows:
        above_two = dtzd > 0 and dtzc > 0
        below_two = dtzd < 0 and dtzc < 0
        if not holding:
            if above_two and dtze > 0:  # 多持且上破DJE
                holding = True
        else:
            if below_two:  # 两线之下退出
                holding = False
        states.append((date, close, holding, dtzc, dtzd, dtze, nxt))
    return states

def analyze(path):
    rows = load_stock(path)
    if len(rows) < 50: return None
    states = simulate(rows)
    total = len(states)
    holding_days = sum(1 for s in states if s[2])
    above_two = sum(1 for s in states if s[4] > 0 and s[3] > 0)
    above_holding = sum(1 for s in states if s[4] > 0 and s[3] > 0 and s[2])
    # 收益：算法持有 vs 始终持有（用收盘价）
    # 算法收益：持有期间按收盘价累计（简化：持有日收益累加）
    algo_ret = 0.0
    always_ret = 0.0
    prev_close = None
    for date, close, holding, dtzc, dtzd, dtze, nxt in states:
        if prev_close is not None and close is not None and prev_close > 0:
            daily = close / prev_close - 1
            always_ret += daily
            if holding:
                algo_ret += daily
        prev_close = close
    return {
        'total': total, 'holding_days': holding_days,
        'hold_ratio': holding_days/total if total else 0,
        'above_two': above_two, 'above_holding': above_holding,
        'above_cov': above_holding/above_two if above_two else 0,
        'algo_ret': algo_ret, 'always_ret': always_ret,
        'algo_win': algo_ret > 0,
        'algo_beats': algo_ret > always_ret,
    }

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
    print(f'共 {len(files)} 只股票')
    agg = {'total':0,'holding_days':0,'above_two':0,'above_holding':0,
           'algo_ret':0.0,'always_ret':0.0}
    n_valid = 0
    per = []
    for i, fp in enumerate(files):
        res = analyze(fp)
        if res is None: continue
        n_valid += 1
        for k in agg: agg[k] += res[k]
        per.append(res)
        if (i+1) % 500 == 0: print(f'  已处理 {i+1}/{len(files)}')
    print(f'\n有效股票数: {n_valid}')
    print(f'总K线数: {agg["total"]}')
    print(f'持有时长: {agg["holding_days"]} ({agg["holding_days"]/agg["total"]*100:.2f}%)')
    print(f'两线之上天数: {agg["above_two"]} ({agg["above_two"]/agg["total"]*100:.2f}%)')
    print(f'两线之上且持有: {agg["above_holding"]}')
    print(f'两线之上持有覆盖率: {agg["above_holding"]/agg["above_two"]*100:.2f}%')
    print(f'\n累计收益(全市场): 算法 {agg["algo_ret"]:.2f} vs 始终持有 {agg["always_ret"]:.2f}')
    # 每股统计
    ratios = [p['hold_ratio'] for p in per]
    covs = [p['above_cov'] for p in per]
    algo_wins = sum(1 for p in per if p['algo_win'])
    algo_beats = sum(1 for p in per if p['algo_beats'])
    print(f'\n每股持有时长占比: 中位 {statistics.median(ratios)*100:.2f}%, 均值 {statistics.mean(ratios)*100:.2f}%')
    print(f'每股两线之上覆盖率: 中位 {statistics.median(covs)*100:.2f}%, 均值 {statistics.mean(covs)*100:.2f}%')
    print(f'算法收益为正的股票: {algo_wins}/{n_valid} ({algo_wins/n_valid*100:.2f}%)')
    print(f'算法跑赢始终持有的股票: {algo_beats}/{n_valid} ({algo_beats/n_valid*100:.2f}%)')

if __name__ == '__main__':
    main()