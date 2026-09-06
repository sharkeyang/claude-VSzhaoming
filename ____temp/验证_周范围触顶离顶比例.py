# -*- coding: utf-8 -*-
"""
周范围触顶/离顶比例与推高顶分析 v2
========================================
用户观察：周主升过程中有大量不断推高顶的触顶，也存在少量离顶。

补充分析：
1. 主升范围内 触顶/触哼/触哈/触底/无 的分布（上符串末位）
2. 连续触顶（合顶）推高顶的比例
3. 触顶推高顶 vs 离顶 的表现对比
4. 离顶后是否重新触顶

列序（周CSV）：[0]主期 [1]周涨 [3]HR [4]WXAB [16]ZC周 [33]顶周 [35]合顶周 [39]顶触周 [41]上符串周
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
# 主升范围内 触顶/离顶 计数
inrange_touch = 0; inrange_liding = 0; inrange_total = 0
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
                hr = to_f(row[3])
                if hr is None or hr < -50 or hr > 50: continue
                zc = to_f(row[16])
                if zc is None: continue
                wxab = row[4].strip()
                hx = HX_MAP.get(wxab[0]) if wxab else None
                sfs = row[41].strip()
                hetop = to_f(row[35])
                nxt_hr = to_f(rows[i+1][3]) if i+1 < len(rows) else None

                in_range = (zc > 0) and (hx in ('甲','乙','己'))
                touch = bool(sfs) and sfs[-1]=='A'
                last_char = sfs[-1] if sfs else '_'

                if in_range:
                    inrange_total += 1
                    if touch: inrange_touch += 1
                    else: inrange_liding += 1
                    # 上符串末位分布
                    if last_char=='A': add('主升+末位A(触顶)', nxt_hr)
                    elif last_char=='B': add('主升+末位B(触哼)', nxt_hr)
                    elif last_char=='v': add('主升+末位v(触哈)', nxt_hr)
                    elif last_char=='w': add('主升+末位w(触底)', nxt_hr)
                    else: add('主升+末位_(无)', nxt_hr)
                    # 合顶推高顶
                    if hetop is not None:
                        if hetop>=3: add('主升+合顶≥3(连续推高顶)', nxt_hr)
                        elif hetop==2: add('主升+合顶=2', nxt_hr)
                        elif hetop==1: add('主升+合顶=1(单次触顶)', nxt_hr)
                    # 离顶后是否重新触顶（看下周）
                    if not touch and i+1 < len(rows):
                        nxt_sfs = rows[i+1][41].strip()
                        if nxt_sfs and nxt_sfs[-1]=='A':
                            add('主升+离顶→下周重新触顶', nxt_hr)
                        else:
                            add('主升+离顶→下周未触顶', nxt_hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')
print(f'\n主升范围内 触顶/离顶 比例:')
print(f'  触顶: {inrange_touch} ({inrange_touch/inrange_total*100:.1f}%)')
print(f'  离顶: {inrange_liding} ({inrange_liding/inrange_total*100:.1f}%)')
print(f'  合计: {inrange_total}')

report('主升范围内 上符串末位分布', [
    '主升+末位A(触顶)','主升+末位B(触哼)','主升+末位v(触哈)','主升+末位w(触底)','主升+末位_(无)',
])
report('主升范围内 合顶推高顶', [
    '主升+合顶≥3(连续推高顶)','主升+合顶=2','主升+合顶=1(单次触顶)',
])
report('主升范围内 离顶后表现', [
    '主升+离顶→下周重新触顶','主升+离顶→下周未触顶',
])
