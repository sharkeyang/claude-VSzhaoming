# -*- coding: utf-8 -*-
"""完整重跑日线管分类（周线一致思路，升管/跌管镜面对称）
新定义：
  升管基础 = DTAB>0 且 DTZB>0
  跌管基础 = DTAB<0 且 DTZB<0
  扩管 = 当前触顶（t顶≥-2）[跌管：触底 t底≥-2]
  震管 = 曾触顶，维持DTZB>0（-t顶≤DTZB）[跌管：曾触底，维持DTZB<0]
  头管 = 未触顶（-t顶>DTZB）[跌管：未触底]
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

def deng_class(dv):
    if dv == 1: return '等1'
    elif dv == 2: return '等2'
    elif dv >= 3: return '等3'
    elif dv == -1: return '等5'
    elif dv == -2: return '等6'
    elif dv <= -3: return '等7'
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
                za = int(r[13])
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
            # 等型
            try: dv = int(deng)
            except: dv = None
            deng_c = deng_class(dv) if dv is not None else '等其他'
            hx_c = hx_class(hx)
            zp_c = zp_class(zp)
            # 窄管判定
            is_narrow = False
            if gk != '':
                try: is_narrow = float(gk) < 4
                except: is_narrow = False
            # ===== 升管基础 = DTAB>0 且 DTZB>0 =====
            if dtab > 0 and dtzb > 0:
                add('升管_基线', nh)
                if top >= -2:
                    cls = '扩管'
                elif -top > dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'升管_{cls}', nh)
                add(f'升管_{cls}_{deng_c}', nh)
                add(f'升管_{cls}_{hx_c}', nh)
                add(f'升管_{cls}_{zp_c}', nh)
                if is_narrow:
                    add(f'升管_{cls}_窄管', nh)
                    add('升管_窄管', nh)
                else:
                    add(f'升管_{cls}_宽管', nh)
                    add('升管_宽管', nh)
            # ===== 跌管基础 = DTAB<0 且 DTZB<0 =====
            elif dtab < 0 and dtzb < 0:
                add('跌管_基线', nh)
                if top >= -2:
                    cls = '扩管'
                elif -top > -dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'跌管_{cls}', nh)
                add(f'跌管_{cls}_{deng_c}', nh)
                add(f'跌管_{cls}_{hx_c}', nh)
                add(f'跌管_{cls}_{zp_c}', nh)
                if is_narrow:
                    add(f'跌管_{cls}_窄管', nh)
                    add('跌管_窄管', nh)
                else:
                    add(f'跌管_{cls}_宽管', nh)
                    add('跌管_宽管', nh)

print(f'\n总行数: {total}', flush=True)

def report(prefix, filter_suffix=None):
    print(f'\n=== {prefix} ===', flush=True)
    for label in sorted(stats.keys()):
        if not label.startswith(prefix): continue
        if filter_suffix and not any(s in label for s in filter_suffix): continue
        st = stats[label]
        if st['n'] == 0: continue
        print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%', flush=True)

# 主表
report('升管_基线')
report('升管_扩管', ['_等','_甲','_乙','_丙','_丁','_戊','_己','_升','_跌','_人'])
report('升管_震管', ['_等','_甲','_乙','_丙','_丁','_戊','_己','_升','_跌','_人'])
report('升管_头管', ['_等','_甲','_乙','_丙','_丁','_戊','_己','_升','_跌','_人'])
report('升管_窄管')
report('升管_宽管')
report('跌管_基线')
report('跌管_扩管', ['_等','_甲','_乙','_丙','_丁','_戊','_己','_升','_跌','_人'])
report('跌管_震管', ['_等','_甲','_乙','_丙','_丁','_戊','_己','_升','_跌','_人'])
report('跌管_头管', ['_等','_甲','_乙','_丙','_丁','_戊','_己','_升','_跌','_人'])
report('跌管_窄管')
report('跌管_宽管')