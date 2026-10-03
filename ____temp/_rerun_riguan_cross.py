# -*- coding: utf-8 -*-
"""重跑日线管分类交叉数据（宽管下：扩管/震管/头管 × 等型/护型/柱排）
新定义：
  升管基础 = DTAB>0 且 DTZB>0
  扩管 = 当前触顶（t顶≥-2）
  震管 = 曾触顶，维持DTZB>0（-t顶≤DTZB）
  头管 = 未触顶（-t顶>DTZB）
  窄管 = 管宽<4（另一维度）
列映射（谕组日，0-based，66列）：
  col9=DXAB护型, col10=柱排, col13=日ZA, col21=管宽哼JA, col26=次日高幅,
  col44=日等型, col53=日龟BT顶, col62=DTZB, col64=DTAB
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

def deng_class(deng):
    # col44 已是中文标签（等1/等2/等3/等5/等6/等7）
    if deng in ('等1','等2','等3','等5','等6','等7'):
        return deng
    return '等其他'

def hx_class(hx):
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(hx, hx)

def zp_class(zp):
    if zp.startswith('升.'):
        if '尾连' in zp: return '升连'
        elif '尾吞' in zp: return '升吞'
        elif '尾反孕' in zp: return '升孕'
        else: return '升排其他'
    elif zp.startswith('跌.'):
        if '尾连' in zp: return '跌连'
        elif '尾吞' in zp: return '跌吞'
        elif '尾反孕' in zp: return '跌孕'
        else: return '跌排其他'
    elif zp.startswith('('):
        return '人排'
    else:
        return '其他'

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
                gk = r[21].strip()
                nh = float(nxt[26])
                top = int(r[53])
                dtzb = int(r[62])
                dtab = int(r[64])
                deng = r[44].strip() if len(r) > 44 else ''
            except:
                continue
            total += 1
            zp = r[10] if len(r) > 10 else ''
            deng_c = deng_class(deng)
            hx_c = hx_class(hx)
            zp_c = zp_class(zp)
            # 窄管判定
            if gk == '': continue
            try: gkv = float(gk)
            except: continue
            if gkv < 4: continue  # 只统计宽管（≥4）
            # 升管基础 = DTAB>0 且 DTZB>0
            if dtab > 0 and dtzb > 0:
                if top >= -2:
                    cls = '扩管'
                elif -top > dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'{cls}_{deng_c}', nh)
                add(f'{cls}_{hx_c}', nh)
                add(f'{cls}_{zp_c}', nh)

print(f'\n总行数: {total}', flush=True)

print('\n=== 宽管下 扩管/震管/头管 × 等型 ===', flush=True)
for cls in ['扩管','震管','头管']:
    print(f'--- {cls} ---', flush=True)
    for deng in ['等1','等2','等3','等5','等6','等7']:
        st = stats[f'{cls}_{deng}']
        if st['n'] == 0: continue
        print(f'  {deng}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%', flush=True)

print('\n=== 宽管下 扩管/震管/头管 × 护型 ===', flush=True)
for cls in ['扩管','震管','头管']:
    print(f'--- {cls} ---', flush=True)
    for hx in ['甲','乙','己']:
        st = stats[f'{cls}_{hx}']
        if st['n'] == 0: continue
        print(f'  {hx}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%', flush=True)

print('\n=== 宽管下 扩管/震管/头管 × 柱排 ===', flush=True)
for cls in ['扩管','震管','头管']:
    print(f'--- {cls} ---', flush=True)
    for zp in ['升连','升吞','升孕','人排','跌连','跌孕','跌吞']:
        st = stats[f'{cls}_{zp}']
        if st['n'] == 0: continue
        print(f'  {zp}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%', flush=True)