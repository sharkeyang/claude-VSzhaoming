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
# 对比: 原完整规则 vs 综合策略(策略4整合)
# 原规则退出: 跌管退出(乙ZA<0/丙+DTZA<=-2) + 冲高回落减仓(升管内跌排) + DXZC<0
# 综合策略: 原规则 + 跌连后下破未重站才退出(不立即退出)
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
        # 原规则
        exit_price = None
        for j in range(i+1, min(i+1+MAX_HOLD, len(rows))):
            rj = rows[j]
            hx0 = rj[9][0]; za = int(rj[13]); zhu = rj[10]; dxzc = int(rj[14])
            # 跌管退出
            if (hx0 == 'b' and za < 0) or hx0 == 'c':
                if za <= -2:
                    try: exit_price = float(rj[1])
                    except: exit_price = None
                    break
            # 冲高回落减仓
            if hx0 in ('a','b','r') and za > 0:
                if zhu.startswith('跌'):
                    try: exit_price = float(rj[1])
                    except: exit_price = None
                    break
            # DXZC<0
            if dxzc < 0:
                try: exit_price = float(rj[1])
                except: exit_price = None
                break
        if exit_price is None:
            try: exit_price = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
            except: continue
        ret = (exit_price - entry_price) / entry_price * 100
        results['原完整规则'].append(ret)
        # 综合策略: 跌连后下破未重站才退出
        exit_price2 = None
        for j in range(i+1, min(i+1+MAX_HOLD, len(rows))):
            rj = rows[j]
            hx0 = rj[9][0]; za = int(rj[13]); zhu = rj[10]; dxzc = int(rj[14])
            # 跌连信号: 若当前是DJA之上跌连, 不立即退出, 等下破后未重站
            is_dielian = (hx0 in ('a','b','r') and za > 0 and zhu.startswith('跌') and '连' in zhu)
            if is_dielian:
                # 找下破
                brk_idx = -1
                for k in range(j+1, min(j+10, len(rows))):
                    if int(rows[k][13]) < 0:
                        brk_idx = k
                        break
                if brk_idx != -1:
                    # 下破后是否重站
                    rest = False
                    for k in range(brk_idx+1, min(brk_idx+6, len(rows))):
                        if int(rows[k][13]) > 0:
                            rest = True
                            break
                    if not rest:
                        # 未重站, 退出
                        try: exit_price2 = float(rows[brk_idx][1])
                        except: exit_price2 = None
                        break
                    else:
                        # 重站, 继续持有
                        continue
                else:
                    # 未下破, 继续持有
                    continue
            # 跌管退出
            if (hx0 == 'b' and za < 0) or hx0 == 'c':
                if za <= -2:
                    try: exit_price2 = float(rj[1])
                    except: exit_price2 = None
                    break
            # 冲高回落减仓(非跌连)
            if hx0 in ('a','b','r') and za > 0 and not is_dielian:
                if zhu.startswith('跌'):
                    try: exit_price2 = float(rj[1])
                    except: exit_price2 = None
                    break
            # DXZC<0
            if dxzc < 0:
                try: exit_price2 = float(rj[1])
                except: exit_price2 = None
                break
        if exit_price2 is None:
            try: exit_price2 = float(rows[min(i+MAX_HOLD, len(rows)-1)][1])
            except: continue
        ret2 = (exit_price2 - entry_price) / entry_price * 100
        results['综合策略(跌连等确认)'].append(ret2)
    n += 1

print('总文件:', n)
print('\n=== 原完整规则 vs 综合策略(跌连等确认) ===')
for name, rets in results.items():
    rets.sort()
    wins = sum(1 for r in rets if r > 0)
    losses = [r for r in rets if r <= 0]
    avg_loss = sum(losses)/len(losses) if losses else 0
    worst5 = rets[:int(len(rets)*0.05)]
    avg_worst5 = sum(worst5)/len(worst5)
    print(f'{name}: n={len(rets)}, 成功率={wins/len(rets)*100:.2f}%, 平均={sum(rets)/len(rets):.3f}%, 平均亏损={avg_loss:.3f}%, 最差5%={avg_worst5:.3f}%')
