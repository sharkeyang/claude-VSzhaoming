# -*- coding: utf-8 -*-
"""按新方案重跑 MC3.3.5 §8.1.7 周管数据
新方案（用户确认 2026-10-03）：
  升管基础 = WXAB>0 且 WXZB>0（四态龙）
  跌管基础 = WXAB<0 且 WXZB<0（四态虎）
  扩管 = 当前触顶（BT顶≥-2）
  震管 = 曾触顶，当前未触顶但维持BTZB>0（-BT顶≤BTZB）
  头管 = 未触顶（-BT顶>BTZB）
  窄管 = 管宽≤5（另一个维度，单独判断）
列映射（谕组周，0-based，53列）：
  col3=HR(当周高幅), col4=WXAB护型(a甲/b乙/c丙/z丁/y戊/r己), col15=ZB周,
  col20=AB周(交叉天数), col30=底周, col33=顶周, col43=宽哼JA周
下周P3 = 下一行 HR≥3%
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组周'
files = glob.glob(os.path.join(DATA_DIR, '谕组周_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

stats = defaultdict(lambda: {'n':0,'p3':0})
def add(label, nh):
    st = stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1

total = 0
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()  # 表头
        rows = []
        for line in f:
            r = line.strip().split(',')
            if len(r) < 44: continue
            rows.append(r)
        for i, r in enumerate(rows):
            if i+1 >= len(rows): continue
            nxt = rows[i+1]
            try:
                hx = r[4][0] if r[4] else ''  # 护型首字符
                zb = int(r[15])   # ZB周
                top = int(r[33])  # 顶周
                bot = int(r[30])  # 底周
                gk = r[43].strip()  # 宽哼JA周
                nxt_hr = float(nxt[3])
            except:
                continue
            total += 1
            # WXAB>0 = 护型甲乙己(a/b/r)；WXAB<0 = 护型丙丁戊(c/z/y)
            ab_pos = hx in ('a','b','r')
            ab_neg = hx in ('c','z','y')
            # 窄管判定（另一个维度）
            is_narrow = False
            if gk != '':
                try:
                    is_narrow = float(gk) <= 5
                except:
                    is_narrow = False
            # 升管基础 = WXAB>0 且 WXZB>0
            if ab_pos and zb > 0:
                add('升管_基线', nxt_hr)
                # 按触顶分扩/震/头
                if top >= -2:
                    cls = '扩管'
                elif -top > zb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'升管_{cls}', nxt_hr)
                # 窄管叠加维度
                if is_narrow:
                    add(f'升管_{cls}_窄管', nxt_hr)
                else:
                    add(f'升管_{cls}_宽管', nxt_hr)
                if is_narrow:
                    add('升管_窄管(管宽≤5)', nxt_hr)
                else:
                    add('升管_宽管(管宽>5)', nxt_hr)
            # 跌管基础 = WXAB<0 且 WXZB<0
            elif ab_neg and zb < 0:
                add('跌管_基线', nxt_hr)
                if bot >= -2:
                    cls = '扩管'
                elif -bot > -zb:
                    cls = '头管'
                else:
                    cls = '震管'
                add(f'跌管_{cls}', nxt_hr)
                if is_narrow:
                    add(f'跌管_{cls}_窄管', nxt_hr)
                else:
                    add(f'跌管_{cls}_宽管', nxt_hr)
                if is_narrow:
                    add('跌管_窄管(管宽≤5)', nxt_hr)
                else:
                    add('跌管_宽管(管宽>5)', nxt_hr)

print(f'\n总行数: {total}', flush=True)
print('\n=== 新方案 周管数据（按触顶分扩/震/头，窄管叠加）===', flush=True)
for label in sorted(stats.keys()):
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 下周P3%={st["p3"]/st["n"]*100:.1f}%', flush=True)
