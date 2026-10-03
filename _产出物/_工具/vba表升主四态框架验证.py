# -*- coding: utf-8 -*-
"""
验证：升主/降主/降转/升转 四态框架（基于 WXAB 与 WXZB 符号）
====================================================
用户要求（2026-09-30）：
升主定义 = WXAB>0 且 WXZB>0。是否可定义：
    升主：WXAB>0 且 WXZB>0
    降主：WXAB<0 且 WXZB<0
    降转：WXAB<0 且 WXZB>0
    升转：WXAB>0 且 WXZB<0
进行数据验证。

口径（VBA 权威）：
    WXAB = JA(EMA5) vs JB(EMA12) 交叉天数（WXAB>0=WJA>WJB 短期均线多头）
    WXZB = JZ(价格均线) vs JB(EMA12) 交叉天数（WXZB>0=WJZ>WJB 价格均线在EMA12之上）

列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR（临高幅）
    [14] WXZA  [15] WXZB  [16] WXZC  [17] WXZD  [18] WXZE  [20] WXAB
"""
import csv, os, sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/升主四态框架验证结果.csv'

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)

def to_f(v):
    try: return float(v)
    except: return None

# 统计: (状态) -> [样本, 周涨和, 正周涨数, HR和, P(HR>3%)]
stats = defaultdict(lambda: [0, 0.0, 0, 0.0, 0])

files_core = 0
for fname in sorted(os.listdir(DATA_DIR)):
    if not fname.startswith('谕组周_') or not fname.endswith('.csv'): continue
    cidl = fname.replace('谕组周_', '').replace('.csv', '')
    if board_map.get(cidl, '') not in 高波池板块: continue
    files_core += 1
    try:
        with open(os.path.join(DATA_DIR, fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    for row in rows:
        if len(row) <= 20: continue
        zhang = to_f(row[1]); hr = to_f(row[3])
        wxab = to_f(row[20]); wxzb = to_f(row[15])
        if zhang is None or hr is None or wxab is None or wxzb is None: continue
        if wxab > 0 and wxzb > 0: state = '升主'
        elif wxab < 0 and wxzb < 0: state = '降主'
        elif wxab < 0 and wxzb > 0: state = '降转'
        elif wxab > 0 and wxzb < 0: state = '升转'
        else: state = '边界(AB=0或ZB=0)'
        s = stats[state]
        s[0] += 1
        s[1] += zhang
        if zhang > 0: s[2] += 1
        s[3] += hr
        if hr > 3: s[4] += 1

print(f'高波池文件: {files_core}')
print()
print('升主/降主/降转/升转 四态框架验证（WXAB × WXZB 符号）')
print(f'{"状态":<10}{"样本":>10}{"占比":>8}{"平均周涨":>10}{"正周涨%":>9}{"平均HR":>9}{"P(HR>3%)":>10}')
print('-' * 70)
order = ['升主', '降转', '升转', '降主', '边界(AB=0或ZB=0)']
total = sum(stats[s][0] for s in stats)
for st in order:
    n, zhang_s, pos, hr_s, hr3 = stats[st]
    if n == 0: continue
    print(f'{st:<10}{n:>10,}{n/total*100:>7.1f}%{zhang_s/n:>9.3f}%{pos/n*100:>8.1f}%{hr_s/n:>8.2f}%{hr3/n*100:>9.1f}%')

# 写 CSV
with open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['状态', '定义', '样本', '占比', '平均周涨', '正周涨%', '平均HR', 'P(HR>3%)'])
    defs = {
        '升主': 'WXAB>0 且 WXZB>0',
        '降转': 'WXAB<0 且 WXZB>0',
        '升转': 'WXAB>0 且 WXZB<0',
        '降主': 'WXAB<0 且 WXZB<0',
        '边界(AB=0或ZB=0)': 'WXAB=0 或 WXZB=0',
    }
    for st in order:
        n, zhang_s, pos, hr_s, hr3 = stats[st]
        if n == 0: continue
        w.writerow([st, defs[st], n, f'{n/total*100:.1f}%', f'{zhang_s/n:.3f}%', f'{pos/n*100:.1f}%', f'{hr_s/n:.2f}%', f'{hr3/n*100:.1f}%'])
print(f'\n结果已写入: {OUT_CSV}')
