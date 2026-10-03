# -*- coding: utf-8 -*-
"""按新方案重跑 §8.1.7 阈值评估（窄管阈值 + 顶阈值）
新方案：
  升管基础 = WXAB>0 且 WXZB>0（四态龙）
  扩管 = 当前触顶（BT顶≥-2）
  震管 = 曾触顶，当前未触顶但维持BTZB>0（-BT顶≤BTZB）
  头管 = 未触顶（-BT顶>BTZB）
  窄管 = 管宽≤N（另一个维度）
列映射（谕组周，0-based）：
  col3=HR, col4=WXAB护型, col15=ZB周, col30=底周, col33=顶周, col43=宽哼JA周
下周P3 = 下一行 HR≥3%
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组周'
files = glob.glob(os.path.join(DATA_DIR, '谕组周_*.csv'))

stats = defaultdict(lambda: {'n':0,'p3':0})
def add(label, nh):
    st = stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        rows = []
        for line in f:
            r = line.strip().split(',')
            if len(r) < 44: continue
            rows.append(r)
        for i, r in enumerate(rows):
            if i+1 >= len(rows): continue
            nxt = rows[i+1]
            try:
                hx = r[4][0] if r[4] else ''
                zb = int(r[15])
                top = int(r[33])
                gk = r[43].strip()
                nxt_hr = float(nxt[3])
            except:
                continue
            ab_pos = hx in ('a','b','r')
            if not (ab_pos and zb > 0): continue  # 只统计升管基础
            # 触顶分类
            if top >= -2:
                cls = '扩管'
            elif -top > zb:
                cls = '头管'
            else:
                cls = '震管'
            # 窄管阈值评估（管宽≤N）
            if gk != '':
                gkv = float(gk)
                for N in [3,4,5,6,7]:
                    if gkv <= N:
                        add(f'窄管≤{N}', nxt_hr)
                    else:
                        add(f'宽管>{N}', nxt_hr)
            # 顶阈值评估（扩管/震管/头管 在宽管>5下）
            if gk != '' and float(gk) > 5:
                for T in [-1,-2,-3]:
                    if top >= T:
                        add(f'宽管_顶≥{T}', nxt_hr)
                    else:
                        add(f'宽管_顶<{T}', nxt_hr)

print('\n=== 窄管阈值评估（升管基础内，管宽≤N）===', flush=True)
for N in [3,4,5,6,7]:
    n_n = stats[f'窄管≤{N}']['n']; p3_n = stats[f'窄管≤{N}']['p3']
    n_w = stats[f'宽管>{N}']['n']; p3_w = stats[f'宽管>{N}']['p3']
    if n_n and n_w:
        print(f'≤{N}: 窄管P3={p3_n/n_n*100:.1f}% (n={n_n:,}) | 宽管P3={p3_w/n_w*100:.1f}% (n={n_w:,}) | 差={p3_w/n_w*100-p3_n/n_n*100:.1f}pp', flush=True)

print('\n=== 顶阈值评估（升管基础内，管宽>5）===', flush=True)
for T in [-1,-2,-3]:
    n_ge = stats[f'宽管_顶≥{T}']['n']; p3_ge = stats[f'宽管_顶≥{T}']['p3']
    n_lt = stats[f'宽管_顶<{T}']['n']; p3_lt = stats[f'宽管_顶<{T}']['p3']
    if n_ge and n_lt:
        print(f'顶≥{T}: P3={p3_ge/n_ge*100:.1f}% (n={n_ge:,}) | 顶<{T}: P3={p3_lt/n_lt*100:.1f}% (n={n_lt:,}) | 差={p3_ge/n_ge*100-p3_lt/n_lt*100:.1f}pp', flush=True)
