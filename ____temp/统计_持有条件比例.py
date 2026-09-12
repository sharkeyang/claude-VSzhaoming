# -*- coding: utf-8 -*-
"""
统计"持有条件"样本占总天数比例（高波池/低波池，单股分布）
====================================================
持有条件（§4.8定型操作）：DXCD=上/忐 + 护型甲/乙ZA>0/己 + 日ZA>0(DJA丘)

输出：
  ① 高波池/低波池 总体比例
  ② 单股比例分布：最高/最低/中位/均值/标准差/四分位
  ③ 单股比例分布直方图（分桶）

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA
"""
import csv, os, sys, statistics
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 板块映射
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high_boards = {'Qic', 'Qim', 'Qit'}
low_boards = {'Qe', 'Qin', 'Qd', 'Qif', 'Qst'}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

def is_hold(dxcd, hx, za):
    """持有条件：DXCD=上/忐 + 甲/乙ZA>0/己 + 日ZA>0"""
    if dxcd not in ('上', '忐'): return False
    if hx not in ('甲', '乙', '己'): return False
    if hx == '乙' and za <= 0: return False  # 乙需ZA>0
    if za <= 0: return False  # 日ZA>0 (DJA丘)
    return True

# 每只股票: code -> [总天数, 持有天数]
per_stock = defaultdict(lambda: [0, 0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    board = pool.get(code, '')
    if board not in high_boards and board not in low_boards: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 13: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                za = to_f(row[13])
                if za is None: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                per_stock[code][0] += 1
                if is_hold(dxcd, hx, za):
                    per_stock[code][1] += 1
    except Exception:
        pass

print(f'处理文件: {files_core}')
print()

def analyze(group_name, codes):
    """分析一组股票的持有比例分布"""
    props = []
    tot_days = 0
    tot_hold = 0
    for code in codes:
        days, hold = per_stock[code]
        if days == 0: continue
        tot_days += days
        tot_hold += hold
        props.append(hold / days * 100)
    if not props: return
    props_sorted = sorted(props)
    n = len(props)
    print('=' * 70)
    print(f'{group_name}（{n} 只股票）')
    print('=' * 70)
    print(f'  总体持有比例: {tot_hold/tot_days*100:.2f}%  ({tot_hold:,}/{tot_days:,} 天)')
    print(f'  单股比例分布:')
    print(f'    最高: {props_sorted[-1]:.2f}%')
    print(f'    最低: {props_sorted[0]:.2f}%')
    print(f'    中位: {statistics.median(props):.2f}%')
    print(f'    均值: {statistics.mean(props):.2f}%')
    print(f'    标准差: {statistics.stdev(props):.2f}%')
    # 四分位
    q1 = props_sorted[n//4]
    q3 = props_sorted[3*n//4]
    print(f'    Q1(25%): {q1:.2f}%')
    print(f'    Q3(75%): {q3:.2f}%')
    print(f'    IQR: {q3-q1:.2f}%')
    # 直方图
    print(f'  单股比例分布直方图:')
    bins = [(0,5),(5,10),(10,15),(15,20),(20,25),(25,30),(30,35),(35,40),(40,100)]
    for lo, hi in bins:
        cnt = sum(1 for p in props if lo <= p < hi)
        bar = '#' * int(cnt / max(1, n/40))
        print(f'    {lo:>3}-{hi:<3}%: {cnt:>4} ({cnt/n*100:>5.1f}%) {bar}')
    print()

# 高波池
high_codes = [c for c, b in pool.items() if b in high_boards]
low_codes = [c for c, b in pool.items() if b in low_boards]
analyze('高波池（Qic+Qim+Qit）', high_codes)
analyze('低波池（Qe+Qin+Qd+Qif+Qst）', low_codes)
