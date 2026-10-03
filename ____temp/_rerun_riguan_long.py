# -*- coding: utf-8 -*-
"""重跑日线管分类长周期数据（5日/10日/20日P3）
新定义：
  升管基础 = DTAB>0 且 DTZB>0
  跌管基础 = DTAB<0 且 DTZB<0
  扩管 = 当前触顶（t顶≥-2）[跌管：触底]
  震管 = 曾触顶，维持DTZB>0（-t顶≤DTZB）[跌管：曾触底，维持DTZB<0]
  头管 = 未触顶（-t顶>DTZB）[跌管：未触底]
  窄管 = 管宽<4（另一维度）
长周期P3：未来N日内任意一天高幅≥3%
列映射（谕组日，0-based，66列）：
  col9=DXAB护型, col13=日ZA, col21=管宽哼JA, col26=次日高幅,
  col53=日龟BT顶, col62=DTZB, col64=DTAB
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

stats = defaultdict(lambda: {'n':0,'p3_5':0,'p3_10':0,'p3_20':0})
def add(label, p3_5, p3_10, p3_20):
    st = stats[label]; st['n']+=1
    if p3_5: st['p3_5']+=1
    if p3_10: st['p3_10']+=1
    if p3_20: st['p3_20']+=1

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
            try:
                gk = r[21].strip()
                top = int(r[53])
                dtzb = int(r[62])
                dtab = int(r[64])
                deng = r[44].strip() if len(r) > 44 else ''
            except:
                continue
            # 长周期P3：未来5/10/20日内任意一天高幅≥3%
            p3_5 = p3_10 = p3_20 = 0
            for j in range(i+1, min(i+21, len(rows))):
                try:
                    hr = float(rows[j][6])  # col6=高幅
                except:
                    continue
                if hr >= 3:
                    if j - i <= 5: p3_5 = 1
                    if j - i <= 10: p3_10 = 1
                    p3_20 = 1
                    if p3_5 and p3_10 and p3_20:
                        break
            total += 1
            # 窄管判定
            if gk == '': continue
            try: gkv = float(gk)
            except: continue
            is_narrow = gkv < 4
            # 升管基础/非升管基础整体
            if dtab > 0 and dtzb > 0:
                add('升管基础', p3_5, p3_10, p3_20)
            elif dtab < 0 and dtzb < 0:
                add('跌管基础', p3_5, p3_10, p3_20)
            else:
                add('非升管基础', p3_5, p3_10, p3_20)
            # 升管基础 = DTAB>0 且 DTZB>0
            if dtab > 0 and dtzb > 0:
                if top >= -2:
                    cls = '扩管'
                elif -top > dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'升管_{cls}', p3_5, p3_10, p3_20)
                if is_narrow:
                    add(f'升管_{cls}_窄管', p3_5, p3_10, p3_20)
                    add('升管_窄管', p3_5, p3_10, p3_20)
                else:
                    add(f'升管_{cls}_宽管', p3_5, p3_10, p3_20)
                    add('升管_宽管', p3_5, p3_10, p3_20)
                # 等3限定
                if deng == '等3':
                    add(f'等3_{cls}', p3_5, p3_10, p3_20)
                    if is_narrow:
                        add(f'等3_{cls}_窄管', p3_5, p3_10, p3_20)
                    else:
                        add(f'等3_{cls}_宽管', p3_5, p3_10, p3_20)
            # 跌管基础 = DTAB<0 且 DTZB<0
            elif dtab < 0 and dtzb < 0:
                if top >= -2:
                    cls = '扩管'
                elif -top > -dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'跌管_{cls}', p3_5, p3_10, p3_20)
                if is_narrow:
                    add(f'跌管_{cls}_窄管', p3_5, p3_10, p3_20)
                    add('跌管_窄管', p3_5, p3_10, p3_20)
                else:
                    add(f'跌管_{cls}_宽管', p3_5, p3_10, p3_20)
                    add('跌管_宽管', p3_5, p3_10, p3_20)

print(f'\n总行数: {total}', flush=True)

def report(prefix):
    print(f'\n=== {prefix} ===', flush=True)
    for label in sorted(stats.keys()):
        if not label.startswith(prefix): continue
        st = stats[label]
        if st['n'] == 0: continue
        print(f'{label}: n={st["n"]}, 5日P3%={st["p3_5"]/st["n"]*100:.2f}%, 10日P3%={st["p3_10"]/st["n"]*100:.2f}%, 20日P3%={st["p3_20"]/st["n"]*100:.2f}%', flush=True)

report('升管基础')
report('跌管基础')
report('非升管基础')
report('升管_扩管')
report('升管_震管')
report('升管_头管')
report('升管_窄管')
report('升管_宽管')
report('跌管_扩管')
report('跌管_震管')
report('跌管_头管')
report('跌管_窄管')
report('跌管_宽管')
report('等3_扩管')
report('等3_震管')
report('等3_头管')