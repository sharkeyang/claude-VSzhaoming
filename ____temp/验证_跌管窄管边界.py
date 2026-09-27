# -*- coding: utf-8 -*-
"""
验证（2026-09-27）：跌管（丙丁戊）窄管边界
=====================================================
待办：跌管管宽哼JA 无负值，需验证跌管窄管(0-4)的边界是否合理。

核心问题：
1. 跌管（丙丁戊 + DXZA<0）管宽哼JA 是否真的无负值？
2. 窄管(0-4) 是否真的极弱？边界 4 是否合理？
3. 细分管宽区间（0-1/1-2/2-3/3-4/4-5/5-6/6-8/8-10/10-15/15-20/20-30/30+）看次日P3%梯度
4. 对比升管（甲乙己 + DXZA>0）同区间，看窄管边界是否镜像一致

列映射（元数据_vba数据映射_日类.md）：
  [9]  DXAB 护型（a甲/b乙/c丙/z丁/y戊/r己+方向+护级+持续）
  [13] 日ZA = DTZA
  [21] 脸哼JA（管宽哼JA）
  [26] 次日高幅
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_跌管窄管边界.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_dxab = 9
i_za = 13
i_kw = 21   # 管宽哼JA
i_hr = 26   # 次日高幅

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
跌管 = {'丙', '丁', '戊'}
升管 = {'甲', '乙', '己'}

# 管宽区间（细粒度，验证窄管边界）
KW_BINS = [('<0',None,-0.0001),(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,8),(8,10),(10,15),(15,20),(20,30),(30,60),(60,None)]
def kw_bin(v):
    if v < 0: return '<0'
    for lo, hi in KW_BINS[1:]:
        if hi is None:
            if v >= lo: return f'{lo}+'
        elif lo <= v < hi:
            return f'{lo}-{hi}'
    return '?'

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
# 负值统计
neg_count = defaultdict(int)
neg_total = defaultdict(int)

files_done = 0
for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            header = next(r)
            for row in r:
                if len(row) <= max(i_dxab, i_za, i_kw, i_hr):
                    continue
                dxab = row[i_dxab].strip()
                if not dxab:
                    continue
                hx = HX_MAP.get(dxab[0], '')
                if not hx:
                    continue
                try:
                    za = float(row[i_za])
                    kw = float(row[i_kw])
                    hr = float(row[i_hr])
                except (ValueError, IndexError):
                    continue
                if hr < -50 or hr > 50:
                    continue
                # 跌管 = 丙丁戊 + DXZA<0；升管 = 甲乙己 + DXZA>0
                if hx in 跌管 and za < 0:
                    grp = '跌管'
                elif hx in 升管 and za > 0:
                    grp = '升管'
                else:
                    continue
                # 负值统计
                if kw < 0:
                    neg_count[grp] += 1
                neg_total[grp] += 1
                # 管宽区间
                b = kw_bin(kw)
                key = (grp, b)
                s = stats[key]
                s[0] += 1
                if hr >= 3:
                    s[1] += 1
                s[2] += hr
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('跌管（丙丁戊+DXZA<0）窄管边界验证')
out('=' * 100)
out('')
out('管宽哼JA 负值统计（跌管管宽无负值？）：')
for grp in ['跌管', '升管']:
    out(f'  {grp}: 负值 {neg_count[grp]:,} / 总 {neg_total[grp]:,} = {neg_count[grp]/neg_total[grp]*100:.4f}%')
out('')

# 输出各区间次日P3%
out('管宽区间 × 次日P3%（跌管 vs 升管）：')
out(f'{"区间":<10} {"跌管n":>12} {"跌管P3%":>9} {"升管n":>12} {"升管P3%":>9}')
out('-' * 60)
line_neg = '<0'.ljust(10)
for grp in ['跌管', '升管']:
    s = stats.get((grp, '<0'), [0, 0, 0.0])
    if s[0] >= 100:
        line_neg += f'{s[0]:>12,} {s[1]/s[0]*100:>8.2f}%'
    else:
        line_neg += f'{s[0]:>12,} {"-":>8}'
out(line_neg)
for lo, hi in KW_BINS[1:]:
    b = f'{lo}-{hi}' if hi is not None else f'{lo}+'
    row = []
    for grp in ['跌管', '升管']:
        s = stats.get((grp, b), [0, 0, 0.0])
        if s[0] >= 100:
            row.append(f'{s[0]:>12,} {s[1]/s[0]*100:>8.2f}%')
        else:
            row.append(f'{s[0]:>12,} {"-":>8}')
    out(f'{b:<10} {row[0]} {row[1]}')
out('')

# 窄管边界分析：0-4 内部细分 + 4-5 边界
out('=' * 100)
out('窄管边界分析（0-4 内部梯度 + 4-5 边界）')
out('=' * 100)
out('')
out('跌管 0-5 细分区间的次日P3%梯度：')
out(f'{"区间":<10} {"n":>12} {"P3%":>8} {"均高幅":>8}')
out('-' * 50)
for lo, hi in [(0,1),(1,2),(2,3),(3,4),(4,5)]:
    b = f'{lo}-{hi}'
    s = stats.get(('跌管', b), [0, 0, 0.0])
    if s[0] >= 100:
        out(f'{b:<10} {s[0]:>12,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
    else:
        out(f'{b:<10} {s[0]:>12,} {"-":>8}')
out('')

# 汇总 0-4 与 4+ 对比
def agg_range(grp, lo, hi):
    n = p3 = 0
    for (g, b), s in stats.items():
        if g != grp:
            continue
        if b == '<0':
            continue
        if b.endswith('+'):
            blo = int(b[:-1])
            if lo <= blo < hi:
                n += s[0]; p3 += s[1]
        else:
            blo, bhi = b.split('-')
            blo, bhi = int(blo), int(bhi)
            if lo <= blo and bhi <= hi:
                n += s[0]; p3 += s[1]
    return n, p3

out('跌管窄管(0-4) vs 平管(4+) 汇总：')
for grp in ['跌管', '升管']:
    n04, p04 = agg_range(grp, 0, 4)
    n4p, p4p = agg_range(grp, 4, 999)
    out(f'  {grp}: 窄管(0-4) n={n04:,} P3%={p04/n04*100:.2f}% | 平管(4+) n={n4p:,} P3%={p4p/n4p*100:.2f}%')
out('')

# 边界敏感性：若边界改为 3 或 5，窄管P3%变化（含<0并入窄管）
out('边界敏感性（窄管上界 3/4/5 的P3%，含<0归窄管）：')
for grp in ['跌管', '升管']:
    line = f'  {grp}: '
    for up in [3, 4, 5]:
        n, p = agg_range(grp, 0, up)
        # 并入<0
        s_neg = stats.get((grp, '<0'), [0, 0, 0.0])
        n += s_neg[0]; p += s_neg[1]
        line += f'0-{up}:{p/n*100:.2f}%({n:,})  '
    out(line)
out('')

out('=' * 100)
out('关键洞察')
out('=' * 100)
out('')
out('1. 跌管管宽哼JA 是否无负值？')
out('2. 窄管(0-4) 是否极弱？边界 4 是否合理？')
out('3. 边界改为 3 或 5 是否更优？')
out('')

OUTF.close()
print('Done')
