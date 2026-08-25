# -*- coding: utf-8 -*-
"""Analyze improve/maintain/worsen probabilities for weekly"""
import os, csv, json
from collections import defaultdict

board_map = json.load(open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8'))
高波池 = {'Qic','Qim','Qit'}
files = sorted(os.listdir('昭明算展/谕组周0825'))
files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]
gb_files = [f for f in files if board_map.get(f.replace('谕组周_','').replace('.csv',''), '') in 高波池]
print(f'高波池周线文件: {len(gb_files)}')

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

# 转好路径
GOOD_PATHS = {
    '己': ['甲'],
    '戊(ZA>0)': ['己', '甲'],
    '戊(ZA≤0)': ['己', '甲', '戊(ZA>0)'],
    '丁': ['己', '甲', '戊(ZA>0)', '戊(ZA≤0)'],
    '乙(ZA≤0)': ['乙(ZA>0)', '甲'],
    '丙': ['乙(ZA>0)', '乙(ZA≤0)', '甲'],
    '甲': [],
    '乙(ZA>0)': [],
}

# 转坏路径
BAD_PATHS = {
    '甲': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA>0)': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA≤0)': ['丙', '丁'],
    '丙': ['丁'],
    '丁': ['戊(ZA>0)', '戊(ZA≤0)'],
    '戊(ZA>0)': ['戊(ZA≤0)', '丙'],
    '戊(ZA≤0)': ['丙'],
    '己': ['戊(ZA>0)', '戊(ZA≤0)', '丙'],
}

stats = defaultdict(lambda: {
    'total': 0, '维持': 0, '转好': 0, '转坏': 0,
    '转坏_hr_sum': 0.0, '转坏_hr3': 0, '转坏_hr5': 0, '转坏_样本': 0,
    '转坏路径': defaultdict(lambda: {'n':0, 'hr_sum':0.0, 'hr3':0, 'hr5':0})
})

cd_stats = defaultdict(lambda: defaultdict(lambda: {
    'total': 0, '维持': 0, '转好': 0, '转坏': 0,
    '转坏_hr_sum': 0.0, '转坏_hr3': 0, '转坏_样本': 0,
    '转坏路径': defaultdict(lambda: {'n':0, 'hr_sum':0.0, 'hr3':0})
}))

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

            if prev is not None:
                p_hx, p_zc, p_wxcd = prev
                key = (p_hx, p_zc)

                if p_hx == cur:
                    cat = '维持'
                elif cur in GOOD_PATHS.get(p_hx, []):
                    cat = '转好'
                elif cur in BAD_PATHS.get(p_hx, []):
                    cat = '转坏'
                else:
                    cat = '其他'

                stats[key]['total'] += 1
                stats[key][cat] += 1

                if cat == '转坏':
                    stats[key]['转坏_hr_sum'] += hr_f
                    stats[key]['转坏_hr3'] += 1 if hr_f >= 3 else 0
                    stats[key]['转坏_hr5'] += 1 if hr_f >= 5 else 0
                    stats[key]['转坏_样本'] += 1
                    stats[key]['转坏路径'][cur]['n'] += 1
                    stats[key]['转坏路径'][cur]['hr_sum'] += hr_f
                    stats[key]['转坏路径'][cur]['hr3'] += 1 if hr_f >= 3 else 0
                    stats[key]['转坏路径'][cur]['hr5'] += 1 if hr_f >= 5 else 0

                if p_wxcd in ['金','银','唏','嘘','尿','屎']:
                    cd_key = (p_wxcd, p_hx, p_zc)
                    cd_stats[cd_key]['total'] += 1
                    cd_stats[cd_key][cat] += 1
                    if cat == '转坏':
                        cd_stats[cd_key]['转坏_hr_sum'] += hr_f
                        cd_stats[cd_key]['转坏_hr3'] += 1 if hr_f >= 3 else 0
                        cd_stats[cd_key]['转坏_样本'] += 1
                        cd_stats[cd_key]['转坏路径'][cur]['n'] += 1
                        cd_stats[cd_key]['转坏路径'][cur]['hr_sum'] += hr_f
                        cd_stats[cd_key]['转坏路径'][cur]['hr3'] += 1 if hr_f >= 3 else 0

            prev = (cur, zc_gt0, wxcd.strip() if wxcd.strip() in ['金','银','唏','嘘','尿','屎'] else '')

print()
print('='*120)
print('一、各护型转好/维持/转坏概率（按WXZC符号）')
print('='*120)
for zc_label, zc_val in [('WXZC>0', True), ('WXZC≤0', False)]:
    print(f'\n[{zc_label}]')
    print('| 护型 | 总样本 | 维持率 | 转好率 | 转坏率 | 转坏后均HR | 转坏后HR≥3% | 转坏后HR≥5% |')
    print('|:----:|:------:|:------:|:------:|:------:|:----------:|:------------:|:------------:|')
    for hx in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        s = stats[(hx, zc_val)]
        if s['total'] == 0: continue
        maintain = s['维持']/s['total']*100
        improve = s['转好']/s['total']*100
        worsen = s['转坏']/s['total']*100
        w_avg = s['转坏_hr_sum']/s['转坏_样本'] if s['转坏_样本'] > 0 else 0
        w_hr3 = s['转坏_hr3']/s['转坏_样本']*100 if s['转坏_样本'] > 0 else 0
        w_hr5 = s['转坏_hr5']/s['转坏_样本']*100 if s['转坏_样本'] > 0 else 0
        print(f'| {hx} | {s["total"]:,} | {maintain:.1f}% | {improve:.1f}% | {worsen:.1f}% | {w_avg:.2f}% | {w_hr3:.1f}% | {w_hr5:.1f}% |')

print()
print('='*120)
print('二、转坏路径细分：各护型转坏后去了哪里？后果如何？')
print('='*120)
for zc_label, zc_val in [('WXZC>0', True), ('WXZC≤0', False)]:
    print(f'\n[{zc_label}]')
    for hx in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        s = stats[(hx, zc_val)]
        if s['转坏_样本'] == 0: continue
        print(f'\n  {hx}（转坏总样本: {s["转坏_样本"]:,}）')
        print(f'  | →护型 | 样本 | 占比 | 转坏后均HR | 转坏后HR≥3% | 转坏后HR≥5% |')
        print(f'  |:----:|:----:|:----:|:----------:|:------------:|:------------:|')
        for nxt, ns in sorted(s['转坏路径'].items(), key=lambda x: -x[1]['n']):
            pct = ns['n']/s['转坏_样本']*100
            avg = ns['hr_sum']/ns['n'] if ns['n'] > 0 else 0
            hr3 = ns['hr3']/ns['n']*100 if ns['n'] > 0 else 0
            hr5 = ns['hr5']/ns['n']*100 if ns['n'] > 0 else 0
            print(f'  | {nxt} | {ns["n"]:,} | {pct:.1f}% | {avg:.2f}% | {hr3:.1f}% | {hr5:.1f}% |')