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
    dxcd = row[8]; dxzc = int(row[14]); hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
    if dxcd not in ('上','忐') or dxzc <= 0 or hx0 not in ('a','b','r'): return False
    zc = zhu_class(zhu)
    if za == 1: return False
    if za == 2: return zc in ('升连','跌孕')
    if za >= 3: return zc != '阴阳阴'
    return False

def is_exit(row, mode):
    hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
    if mode in ('full','reduce_only'):
        if hx0 in ('a','b','r') and za > 0:
            if zhu.startswith('跌'): return '冲高回落减仓'
    if mode in ('full','exit_only'):
        if (hx0 == 'b' and za < 0) or hx0 == 'c':
            if za <= -2: return '跌管退出'
    return None

MAX_HOLD = 20
# 对比不同退出规则
results = defaultdict(lambda:[0,0,0.0])  # mode -> [n, wins, sum_ret]

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
        if not is_entry(row): continue
        try: entry_price = float(row[1])
        except: continue
        for mode in ['full','reduce_only','exit_only','none']:
            exit_price = None
            for j in range(i+1, min(i+1+MAX_HOLD, len(rows))):
                reason = is_exit(rows[j], mode)
                if reason:
                    try: exit_price = float(rows[j][1])
                    except: exit_price = None
                    break
            if exit_price is None:
                try: exit_price = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
                except: continue
            ret = (exit_price - entry_price) / entry_price * 100
            results[mode][0] += 1
            if ret > 0: results[mode][1] += 1
            results[mode][2] += ret
    n += 1

print('总文件:', n)
print('\n=== 不同退出规则对比 ===')
names = {'full':'完整规则(减仓+跌管退出)','reduce_only':'仅冲高回落减仓','exit_only':'仅跌管退出','none':'无退出(持有20日)'}
for mode in ['full','reduce_only','exit_only','none']:
    tot, wins, sret = results[mode]
    print(f'{names[mode]:<24}: n={tot}, 成功率={wins/tot*100:.2f}%, 平均收益={sret/tot:.3f}%')
