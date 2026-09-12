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

def is_exit(row):
    hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
    if (hx0 == 'b' and za < 0) or hx0 == 'c':
        if za <= -2: return '跌管退出'
    if hx0 in ('a','b','r') and za > 0:
        if zhu.startswith('跌'): return '冲高回落减仓'
    return None

MAX_HOLD = 20
# 对比: 有退出规则 vs 无退出规则(一直持有到最大持有日)
trades_with = []  # 有退出
trades_without = []  # 无退出(持有到最大持有日)

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
        # 有退出规则
        exit_price = None; exit_reason = None
        for j in range(i+1, min(i+1+MAX_HOLD, len(rows))):
            reason = is_exit(rows[j])
            if reason:
                try: exit_price = float(rows[j][1])
                except: exit_price = None
                exit_reason = reason
                break
        if exit_price is None:
            try: exit_price = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
            except: continue
            exit_reason = '最大持有'
        ret = (exit_price - entry_price) / entry_price * 100
        trades_with.append((ret, exit_reason))
        # 无退出规则(持有到最大持有日)
        try: exit2 = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
        except: continue
        ret2 = (exit2 - entry_price) / entry_price * 100
        trades_without.append(ret2)
    n += 1

print('总文件:', n)
print('\n=== 有退出规则 vs 无退出规则(持有20日) ===')
for name, trades in [('有退出规则', trades_with), ('无退出规则(持有20日)', trades_without)]:
    wins = sum(1 for r in trades if r > 0)
    avg = sum(trades)/len(trades)
    print(f'{name}: n={len(trades)}, 成功率={wins/len(trades)*100:.2f}%, 平均收益={avg:.3f}%')
