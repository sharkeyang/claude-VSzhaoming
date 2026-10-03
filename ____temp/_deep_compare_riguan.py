# -*- coding: utf-8 -*-
"""深度对比日线管分类：周线一致思路（按触顶）vs 现有（管宽+推高顶）
周线一致思路（升管基础 = DTAB>0 且 DTZB>0）：
  扩管 = 当前触顶（t顶≥-2）
  震管 = 曾触顶，维持DTZB>0（-t顶≤DTZB）
  头管 = 未触顶（-t顶>DTZB）
  窄管 = 管宽<阈值（另一维度，阈值扫描）
现有日线定义（升管 = 甲乙己+曾触哼）：
  扩管 = 管宽≥4 + 推高顶（触顶+升排）
  平管 = 管宽≥4 + 非推高顶
  窄管 = 0<管宽<4
列映射（谕组日，0-based，66列）：
  col9=DXAB护型, col10=柱排, col13=日ZA, col21=管宽哼JA, col26=次日高幅,
  col53=日龟BT顶, col62=DTZB, col64=DTAB
次日P3 = 次日高幅≥3%
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

stats = defaultdict(lambda: {'n':0,'p3':0})
def add(label, nh):
    st = stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1

total = 0
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        rows = []
        for line in f:
            r = line.strip().split(',')
            if len(r) < 65: continue
            rows.append(r)
        for i, r in enumerate(rows):
            if i+1 >= len(rows): continue
            nxt = rows[i+1]
            try:
                hx = r[9][0] if r[9] else ''
                za = int(r[13])
                gk = r[21].strip()
                nh = float(nxt[26])
                top = int(r[53])
                dtzb = int(r[62])
                dtab = int(r[64])
            except:
                continue
            total += 1
            zp = r[10] if len(r) > 10 else ''
            shengpai = zp.startswith('升.')
            touch = top >= -2
            # ===== 周线一致思路（升管基础 = DTAB>0 且 DTZB>0）=====
            if dtab > 0 and dtzb > 0:
                add('周一致_升管基线', nh)
                if top >= -2:
                    cls = '扩管'
                elif -top > dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'周一致_{cls}', nh)
                # 窄管阈值扫描
                if gk != '':
                    gkv = float(gk)
                    for T in [3,4,5,6,7]:
                        if gkv < T:
                            add(f'周一致_窄管<{T}', nh)
                            add(f'周一致_{cls}_窄管<{T}', nh)
                        else:
                            add(f'周一致_宽管≥{T}', nh)
                            add(f'周一致_{cls}_宽管≥{T}', nh)
            # ===== 现有日线定义（升管 = 甲乙己+曾触哼）=====
            ab_pos = hx in ('a','b','r')
            if ab_pos and za > 0:
                add('现有_升管基线', nh)
                if gk != '':
                    gkv = float(gk)
                    if 0 < gkv < 4:
                        add('现有_窄管', nh)
                    elif gkv >= 4:
                        if touch and shengpai:
                            add('现有_扩管', nh)
                        else:
                            add('现有_平管', nh)

print(f'\n总行数: {total}', flush=True)

print('\n=== 周线一致思路：窄管阈值扫描（升管基础内）===', flush=True)
for T in [3,4,5,6,7]:
    n_n = stats[f'周一致_窄管<{T}']['n']; p3_n = stats[f'周一致_窄管<{T}']['p3']
    n_w = stats[f'周一致_宽管≥{T}']['n']; p3_w = stats[f'周一致_宽管≥{T}']['p3']
    if n_n and n_w:
        print(f'<{T}: 窄管P3={p3_n/n_n*100:.2f}% (n={n_n:,}) | 宽管P3={p3_w/n_w*100:.2f}% (n={n_w:,}) | 差={p3_w/n_w*100-p3_n/n_n*100:.2f}pp', flush=True)

print('\n=== 周线一致思路：扩管/震管/头管 × 窄管阈值<4 ===', flush=True)
for cls in ['扩管','震管','头管']:
    n_all = stats[f'周一致_{cls}']['n']; p3_all = stats[f'周一致_{cls}']['p3']
    n_n = stats[f'周一致_{cls}_窄管<4']['n']; p3_n = stats[f'周一致_{cls}_窄管<4']['p3']
    n_w = stats[f'周一致_{cls}_宽管≥4']['n']; p3_w = stats[f'周一致_{cls}_宽管≥4']['p3']
    if n_all:
        print(f'{cls}: 全部P3={p3_all/n_all*100:.2f}% (n={n_all:,}) | 窄管P3={p3_n/n_n*100:.2f}% (n={n_n:,}) | 宽管P3={p3_w/n_w*100:.2f}% (n={n_w:,}) | 宽窄差={p3_w/n_w*100-p3_n/n_n*100:.2f}pp', flush=True)

print('\n=== 现有日线定义 ===', flush=True)
for label in ['现有_升管基线','现有_窄管','现有_扩管','现有_平管']:
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%', flush=True)