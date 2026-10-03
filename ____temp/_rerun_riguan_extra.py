# -*- coding: utf-8 -*-
"""补充重跑日线管分类：次日均高幅、3天出管率、5日收益
新定义：
  升管基础 = DTAB>0 且 DTZB>0
  跌管基础 = DTAB<0 且 DTZB<0
  扩管 = 当前触顶（t顶≥-2）[跌管：触底]
  震管 = 曾触顶，维持DTZB>0（-t顶≤DTZB）[跌管：曾触底，维持DTZB<0]
  头管 = 未触顶（-t顶>DTZB）[跌管：未触底]
  窄管 = 管宽<4（另一维度）
指标：
  次日均高幅 = 次日高幅（col6）的平均值
  3天出管率 = 未来3日内 日ZA<0（下破DJA）的比例
  5日收益 = 未来5日累计涨幅（col5 涨幅之和）
列映射（谕组日，0-based，66列）：
  col5=涨幅, col6=高幅, col13=日ZA, col21=管宽哼JA, col44=等型,
  col53=日龟BT顶, col62=DTZB, col64=DTAB
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

stats = defaultdict(lambda: {'n':0,'sum_nh':0,'chu3':0,'sum_ret5':0})
def add(label, nh, chu3, ret5):
    st = stats[label]; st['n']+=1
    st['sum_nh']+=nh
    if chu3: st['chu3']+=1
    st['sum_ret5']+=ret5

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
            # 次日高幅
            try: nh = float(rows[i+1][6]) if i+1 < len(rows) else 0
            except: nh = 0
            # 3天出管率：未来3日内 日ZA<0
            chu3 = 0
            for j in range(i+1, min(i+4, len(rows))):
                try:
                    if int(rows[j][13]) < 0:
                        chu3 = 1; break
                except: continue
            # 5日收益：未来5日累计涨幅
            ret5 = 0
            for j in range(i+1, min(i+6, len(rows))):
                try: ret5 += float(rows[j][5])
                except: continue
            total += 1
            # 窄管判定
            if gk == '': continue
            try: gkv = float(gk)
            except: continue
            is_narrow = gkv < 4
            # 升管基础/非升管基础整体
            if dtab > 0 and dtzb > 0:
                add('升管基础', nh, chu3, ret5)
            elif dtab < 0 and dtzb < 0:
                add('跌管基础', nh, chu3, ret5)
            else:
                add('非升管基础', nh, chu3, ret5)
            # 升管基础 = DTAB>0 且 DTZB>0
            if dtab > 0 and dtzb > 0:
                if top >= -2:
                    cls = '扩管'
                elif -top > dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'升管_{cls}', nh, chu3, ret5)
                if is_narrow:
                    add(f'升管_{cls}_窄管', nh, chu3, ret5)
                    add('升管_窄管', nh, chu3, ret5)
                else:
                    add(f'升管_{cls}_宽管', nh, chu3, ret5)
                    add('升管_宽管', nh, chu3, ret5)
                if deng == '等3':
                    add(f'等3_{cls}', nh, chu3, ret5)
                    if is_narrow:
                        add(f'等3_{cls}_窄管', nh, chu3, ret5)
                    else:
                        add(f'等3_{cls}_宽管', nh, chu3, ret5)
            # 跌管基础 = DTAB<0 且 DTZB<0
            elif dtab < 0 and dtzb < 0:
                if top >= -2:
                    cls = '扩管'
                elif -top > -dtzb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'跌管_{cls}', nh, chu3, ret5)
                if is_narrow:
                    add(f'跌管_{cls}_窄管', nh, chu3, ret5)
                    add('跌管_窄管', nh, chu3, ret5)
                else:
                    add(f'跌管_{cls}_宽管', nh, chu3, ret5)
                    add('跌管_宽管', nh, chu3, ret5)

print(f'\n总行数: {total}', flush=True)

def report(prefix):
    print(f'\n=== {prefix} ===', flush=True)
    for label in sorted(stats.keys()):
        if not label.startswith(prefix): continue
        st = stats[label]
        if st['n'] == 0: continue
        print(f'{label}: n={st["n"]}, 次日均高幅={st["sum_nh"]/st["n"]:.2f}%, 3天出管率={st["chu3"]/st["n"]*100:.2f}%, 5日收益={st["sum_ret5"]/st["n"]:.2f}%', flush=True)

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