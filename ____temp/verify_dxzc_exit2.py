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

MAX_HOLD = 20
# 对比: 无DXZC退出 vs 有DXZC<0退出
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
        if not is_entry(row): continue
        try: entry_price = float(row[1])
        except: continue
        # 无DXZC退出(持有到最大持有日)
        try: exit1 = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
        except: continue
        ret1 = (exit1 - entry_price) / entry_price * 100
        results['无DXZC退出'].append(ret1)
        # 有DXZC<0退出
        exit_price = None
        for j in range(i+1, min(i+1+MAX_HOLD, len(rows))):
            if int(rows[j][14]) < 0:  # DXZC<0
                try: exit_price = float(rows[j][1])
                except: exit_price = None
                break
        if exit_price is None:
            try: exit_price = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
            except: continue
        ret2 = (exit_price - entry_price) / entry_price * 100
        results['有DXZC<0退出'].append(ret2)
    n += 1

print('总文件:', n)
print('\n=== DXZC<0退出验证 ===')
for name, rets in results.items():
    rets.sort()
    wins = sum(1 for r in rets if r > 0)
    losses = [r for r in rets if r <= 0]
    avg_loss = sum(losses)/len(losses) if losses else 0
    worst5 = rets[:int(len(rets)*0.05)]
    avg_worst5 = sum(worst5)/len(worst5)
    print(f'{name}: n={len(rets)}, 成功率={wins/len(rets)*100:.2f}%, 平均收益={sum(rets)/len(rets):.3f}%, 平均亏损={avg_loss:.3f}%, 最差5%={avg_worst5:.3f}%')
