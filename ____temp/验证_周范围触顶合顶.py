# -*- coding: utf-8 -*-
"""
周范围（WXZC>0 + WXAB甲乙己）与周合顶、周触顶的关系分析
========================================
用户观察：周主升过程中，有大量不断推高顶的触顶，也存在少量离顶。

列序（周CSV）：
  [0]主期 [1]周涨 [3]HR [4]WXAB [16]ZC周 [33]顶周 [35]合顶周 [39]顶触周 [41]上符串周

分析：
1. 周主升范围（WXZC>0 + WXAB甲乙己）内的触顶/合顶/离顶分布
2. 触顶推高顶 vs 离顶的比例
3. 触顶/合顶对未来周表现（下周冲高）的影响
"""
import csv, os, sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}
HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

def to_f(v):
    try: return float(v)
    except: return None

stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr

def report(title, keys):
    print(f'\n{"="*84}')
    print(title)
    print('='*84)
    print(f'{"条件":<52} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*80)
    for k in keys:
        if k in stats:
            s = stats[k]
            print(f'{k:<52} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

files_core = 0
for fname in os.listdir('昭明算展/谕组周'):
    p = os.path.join('昭明算展/谕组周', fname)
    try:
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 41: continue
                hr = to_f(row[3])  # 周HR
                if hr is None or hr < -50 or hr > 50: continue
                zc = to_f(row[16])  # 周ZC
                if zc is None: continue
                wxab = row[4].strip()
                hx = HX_MAP.get(wxab[0]) if wxab else None
                sfs = row[41].strip()  # 上符串周
                hetop = to_f(row[35])  # 合顶周
                ding = to_f(row[33])   # 顶周
                # 下周HR（用于未来表现）
                nxt_hr = to_f(rows[i+1][3]) if i+1 < len(rows) else None

                # 周主升范围：WXZC>0 + WXAB甲乙己
                in_range = (zc > 0) and (hx in ('甲','乙','己'))
                # 触顶：上符串末位A
                touch = bool(sfs) and sfs[-1]=='A'
                # 离顶：上符串末位非A（B/v/w/_）
                liding = bool(sfs) and sfs[-1]!='A'

                if in_range:
                    # 触顶 vs 离顶
                    if touch: add('主升+触顶', nxt_hr)
                    else: add('主升+离顶', nxt_hr)
                    # 合顶天数
                    if hetop is not None:
                        if hetop>=3: add('主升+合顶≥3', nxt_hr)
                        elif hetop==1: add('主升+合顶=1', nxt_hr)
                    # 触顶推高顶 vs 离顶
                    if touch: add('主升+触顶(推高顶)', nxt_hr)
                    else: add('主升+离顶(少量)', nxt_hr)
                # 对比：非主升范围
                if not in_range:
                    if touch: add('非主升+触顶', nxt_hr)
                    else: add('非主升+离顶', nxt_hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')

report('周主升范围（WXZC>0 + WXAB甲乙己）内触顶/离顶', [
    '主升+触顶(推高顶)','主升+离顶(少量)',
    '主升+合顶≥3','主升+合顶=1',
])
report('对比：非主升范围', [
    '非主升+触顶','非主升+离顶',
])
