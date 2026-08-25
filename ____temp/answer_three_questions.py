# -*- coding: utf-8 -*-
"""Answer three specific questions about weekly transfer"""
import os, csv, json
from collections import defaultdict

board_map = json.load(open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8'))
高波池 = {'Qic','Qim','Qit'}
files = sorted(os.listdir('昭明算展/谕组周0825'))
files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]
gb_files = [f for f in files if board_map.get(f.replace('谕组周_','').replace('.csv',''), '') in 高波池]

HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

def hx_key(dxab, za):
    if len(dxab) < 2: return None
    c = dxab[0]
    if c not in HX_MAP: return None
    hx = HX_MAP[c]
    if hx in '乙戊':
        try: za_f = float(za)
        except: return None
        return f'{hx}(ZA>0)' if za_f > 0 else f'{hx}(ZA≤0)'
    return hx

q1_stats = {'n':0, 'hr_sum':0.0, 'hr3':0, 'hr5':0, 'hr_pos':0}
q2_stats = {'n':0, 'hr_sum':0.0, 'hr3':0, 'hr5':0, 'hr_pos':0}
q3_stats = {'n':0, 'hr_sum':0.0, 'hr3':0, 'hr5':0, 'hr_pos':0}
甲_乙za_stats = {'n':0, 'hr_sum':0.0, 'hr3':0, 'hr5':0, 'hr_pos':0}

q1_cd = defaultdict(lambda: {'n':0, 'hr_sum':0.0, 'hr3':0})
q2_cd = defaultdict(lambda: {'n':0, 'hr_sum':0.0, 'hr3':0})
q3_cd = defaultdict(lambda: {'n':0, 'hr_sum':0.0, 'hr3':0})

count = 0
for fname in gb_files:
    count += 1
    if count % 500 == 0: print(f'  [{count}/{len(gb_files)}]...')
    with open(os.path.join('昭明算展/谕组周0825', fname), 'r', encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        header = next(r)
        prev = None
        for row in r:
            if len(row) < 27: continue
            dxab, za, zc, hr = row[4], row[14], row[16], row[3]
            wxcd = row[13] if len(row) > 13 else ''
            if len(dxab) < 2: continue
            cur = hx_key(dxab, za)
            if not cur: continue
            try: zc_f, hr_f = float(zc), float(hr)
            except: continue
            zc_gt0 = zc_f > 0
            wxcd_cls = wxcd.strip() if wxcd.strip() in ['金','银','唏','嘘','尿','屎'] else ''

            if prev is not None:
                p_hx, p_zc, p_wxcd = prev

                if p_hx in ['甲', '乙(ZA>0)'] and cur == '乙(ZA≤0)':
                    q1_stats['n'] += 1
                    q1_stats['hr_sum'] += hr_f
                    if hr_f >= 3: q1_stats['hr3'] += 1
                    if hr_f >= 5: q1_stats['hr5'] += 1
                    if hr_f > 0: q1_stats['hr_pos'] += 1
                    if p_wxcd:
                        q1_cd[p_wxcd]['n'] += 1
                        q1_cd[p_wxcd]['hr_sum'] += hr_f
                        if hr_f >= 3: q1_cd[p_wxcd]['hr3'] += 1

                if p_hx == '乙(ZA≤0)' and cur == '乙(ZA>0)':
                    q2_stats['n'] += 1
                    q2_stats['hr_sum'] += hr_f
                    if hr_f >= 3: q2_stats['hr3'] += 1
                    if hr_f >= 5: q2_stats['hr5'] += 1
                    if hr_f > 0: q2_stats['hr_pos'] += 1
                    if p_wxcd:
                        q2_cd[p_wxcd]['n'] += 1
                        q2_cd[p_wxcd]['hr_sum'] += hr_f
                        if hr_f >= 3: q2_cd[p_wxcd]['hr3'] += 1

                if p_hx == '丙' and cur == '乙(ZA≤0)':
                    q3_stats['n'] += 1
                    q3_stats['hr_sum'] += hr_f
                    if hr_f >= 3: q3_stats['hr3'] += 1
                    if hr_f >= 5: q3_stats['hr5'] += 1
                    if hr_f > 0: q3_stats['hr_pos'] += 1
                    if p_wxcd:
                        q3_cd[p_wxcd]['n'] += 1
                        q3_cd[p_wxcd]['hr_sum'] += hr_f
                        if hr_f >= 3: q3_cd[p_wxcd]['hr3'] += 1

                if p_hx == '甲' and cur == '乙(ZA>0)':
                    甲_乙za_stats['n'] += 1
                    甲_乙za_stats['hr_sum'] += hr_f
                    if hr_f >= 3: 甲_乙za_stats['hr3'] += 1
                    if hr_f >= 5: 甲_乙za_stats['hr5'] += 1
                    if hr_f > 0: 甲_乙za_stats['hr_pos'] += 1

            prev = (cur, zc_gt0, wxcd_cls)

print()
print('='*80)
print('问题1：甲/乙(ZA>0) → 乙(ZA≤0) 后，是否应退出？')
print('='*80)
s = q1_stats
print(f'总样本: {s["n"]:,}')
print(f'下周均HR: {s["hr_sum"]/s["n"]:.2f}%')
print(f'下周涨率: {s["hr_pos"]/s["n"]*100:.1f}%')
print(f'下周HR≥3%: {s["hr3"]/s["n"]*100:.1f}%')
print(f'下周HR≥5%: {s["hr5"]/s["n"]*100:.1f}%')
print()
print('按WXCD细分：')
print('| WXCD | 样本 | 均HR | HR≥3% |')
print('|:----:|:----:|:----:|:----:|')
for cls in ['金','银','唏','嘘','尿','屎']:
    c = q1_cd[cls]
    if c['n'] > 0:
        print(f'| {cls} | {c["n"]:,} | {c["hr_sum"]/c["n"]:.2f}% | {c["hr3"]/c["n"]*100:.1f}% |')
print()
print(f'对比：甲维持时HR≥3%=57.1%，乙(ZA>0)维持时=57.0%')
print(f'甲/乙(ZA>0)→乙(ZA≤0)后HR≥3%={s["hr3"]/s["n"]*100:.1f}%')
print(f'差距: {57.1 - s["hr3"]/s["n"]*100:.1f}pp')

print()
print('='*80)
print('问题2：乙(ZA≤0) → 乙(ZA>0) 后，是否应介入？')
print('='*80)
s = q2_stats
print(f'总样本: {s["n"]:,}')
print(f'下周均HR: {s["hr_sum"]/s["n"]:.2f}%')
print(f'下周涨率: {s["hr_pos"]/s["n"]*100:.1f}%')
print(f'下周HR≥3%: {s["hr3"]/s["n"]*100:.1f}%')
print(f'下周HR≥5%: {s["hr5"]/s["n"]*100:.1f}%')
print()
print('按WXCD细分：')
print('| WXCD | 样本 | 均HR | HR≥3% |')
print('|:----:|:----:|:----:|:----:|')
for cls in ['金','银','唏','嘘','尿','屎']:
    c = q2_cd[cls]
    if c['n'] > 0:
        print(f'| {cls} | {c["n"]:,} | {c["hr_sum"]/c["n"]:.2f}% | {c["hr3"]/c["n"]*100:.1f}% |')
print()
print(f'对比：乙(ZA>0)维持时HR≥3%=57.0%')
print(f'乙(ZA≤0)→乙(ZA>0)后HR≥3%={s["hr3"]/s["n"]*100:.1f}%')
print(f'差距: {57.0 - s["hr3"]/s["n"]*100:.1f}pp')

print()
print('='*80)
print('问题3：丙 → 乙(ZA≤0) 后，是否应介入？')
print('='*80)
s = q3_stats
print(f'总样本: {s["n"]:,}')
print(f'下周均HR: {s["hr_sum"]/s["n"]:.2f}%')
print(f'下周涨率: {s["hr_pos"]/s["n"]*100:.1f}%')
print(f'下周HR≥3%: {s["hr3"]/s["n"]*100:.1f}%')
print(f'下周HR≥5%: {s["hr5"]/s["n"]*100:.1f}%')
print()
print('按WXCD细分：')
print('| WXCD | 样本 | 均HR | HR≥3% |')
print('|:----:|:----:|:----:|:----:|')
for cls in ['金','银','唏','嘘','尿','屎']:
    c = q3_cd[cls]
    if c['n'] > 0:
        print(f'| {cls} | {c["n"]:,} | {c["hr_sum"]/c["n"]:.2f}% | {c["hr3"]/c["n"]*100:.1f}% |')
print()
print(f'对比：丙维持时HR≥3%=47.9%，乙(ZA≤0)维持时=47.5%')
print(f'丙→乙(ZA≤0)后HR≥3%={q3_stats["hr3"]/q3_stats["n"]*100:.1f}%')

print()
print('='*80)
print('额外：甲→乙(ZA>0) 后如何？（甲转乙但ZA仍>0）')
print('='*80)
s = 甲_乙za_stats
print(f'总样本: {s["n"]:,}')
print(f'下周均HR: {s["hr_sum"]/s["n"]:.2f}%')
print(f'下周涨率: {s["hr_pos"]/s["n"]*100:.1f}%')
print(f'下周HR≥3%: {s["hr3"]/s["n"]*100:.1f}%')
print(f'下周HR≥5%: {s["hr5"]/s["n"]*100:.1f}%')