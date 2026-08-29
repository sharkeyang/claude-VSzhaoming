#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
综合验证（HR口径）：
1. 甲乙己 vs 其他，DXZC>0 vs DXZC≤0 的次日HR（冲高）
2. 丙首次出现的次日表现（是否立即退出）
3. 甲乙己在DXZC≤0时的表现（能否不管DXZC）
谕组日CSV列：6=高幅(HR), 9=DXAB, 13=日ZA, 14=日ZC
"""
import csv, os, io
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
good_hx = {'甲', '乙(ZA>0)', '己'}

def hx_key(dxab, za):
    if len(dxab) < 1:
        return None
    hx = HX_MAP.get(dxab[0])
    if not hx:
        return None
    try:
        za_f = float(za)
    except:
        za_f = 0
    if hx == '乙':
        return '乙(ZA>0)' if za_f > 0 else '乙(ZA≤0)'
    if hx == '戊':
        return '戊(ZA>0)' if za_f > 0 else '戊(ZA≤0)'
    return hx

def main():
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计: (组, ZC符号) -> [次日HR]
    stats = defaultdict(list)
    # 丙专题: 丙首次出现(持续1天) -> 次日HR; 丙持续2天+ -> 次日HR
    bing_first = defaultdict(list)  # (是否首次, ZC符号) -> [次日HR]
    # 各护型在DXZC≤0的次日HR（用于2.10对比）
    hx_zcle0 = defaultdict(list)

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [处理] {i}/{len(files)}...', flush=True)
        with open(os.path.join(DATA_DIR, fname), encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            rows = []
            for row in r:
                if len(row) < 15:
                    continue
                rows.append(row)
            # 计算次日HR：下一天的HR（高幅）
            for j in range(len(rows) - 1):
                cur = rows[j]
                nxt = rows[j+1]
                try:
                    hr = float(nxt[6])
                except:
                    continue
                if hr > 50:  # 过滤异常
                    continue
                hx = hx_key(cur[9].strip(), cur[13])
                if not hx:
                    continue
                try:
                    zc = float(cur[14])
                except:
                    zc = 0
                zc_sym = 'ZC>0' if zc > 0 else 'ZC≤0'
                # 组分类
                grp = '甲乙己' if hx in good_hx else '其他'
                stats[(grp, zc_sym)].append(hr)
                if zc <= 0:
                    hx_zcle0[hx].append(hr)
                # 丙专题：判断是否首次
                if hx == '丙':
                    # 首次 = 前一日不是丙
                    is_first = (j == 0) or (hx_key(rows[j-1][9].strip(), rows[j-1][13]) != '丙')
                    bing_first[(is_first, zc_sym)].append(hr)

    out = []
    out.append('===== 次日HR：甲乙己 vs 其他，按DXZC =====')
    out.append(f'{"组":<8} {"ZC":<6} {"样本":>10} {"均HR%":>8} {"HR≥3%":>8} {"HR≥5%":>8}')
    for grp in ['甲乙己', '其他']:
        for zc_sym in ['ZC>0', 'ZC≤0']:
            lst = stats.get((grp, zc_sym), [])
            if len(lst) < 100:
                continue
            n = len(lst)
            mean = sum(lst) / n
            hr3 = sum(1 for x in lst if x >= 3) / n * 100
            hr5 = sum(1 for x in lst if x >= 5) / n * 100
            out.append(f'{grp:<8} {zc_sym:<6} {n:>10} {mean:>8.2f} {hr3:>8.1f} {hr5:>8.1f}')

    out.append('\n===== 丙专题：首次出现 vs 持续2天+ 的次日HR =====')
    out.append(f'{"是否首次":<10} {"ZC":<6} {"样本":>10} {"均HR%":>8} {"HR≥3%":>8}')
    for is_first in [True, False]:
        for zc_sym in ['ZC>0', 'ZC≤0']:
            lst = bing_first.get((is_first, zc_sym), [])
            if len(lst) < 100:
                continue
            n = len(lst)
            mean = sum(lst) / n
            hr3 = sum(1 for x in lst if x >= 3) / n * 100
            label = '首次' if is_first else '持续2天+'
            out.append(f'{label:<10} {zc_sym:<6} {n:>10} {mean:>8.2f} {hr3:>8.1f}')

    out.append('\n===== 各护型 DXZC≤0 次日HR（与2.10对比） =====')
    out.append(f'{"护型":<12} {"样本":>10} {"均HR%":>8} {"HR≥3%":>8}')
    for hx in ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']:
        lst = hx_zcle0.get(hx, [])
        if len(lst) < 100:
            continue
        n = len(lst)
        mean = sum(lst) / n
        hr3 = sum(1 for x in lst if x >= 3) / n * 100
        out.append(f'{hx:<12} {n:>10} {mean:>8.2f} {hr3:>8.1f}')

    with open('____temp/_zc_verify.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print('done')

if __name__ == '__main__':
    main()