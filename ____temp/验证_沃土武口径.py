# -*- coding: utf-8 -*-
"""
确认 84.04%(沃×武) 的 P(≥3%) 口径：当前周涨幅≥3% 还是 下周涨幅≥3%？
同时统计 沃土×武 vs 沃土×龙 的多个口径，判断周层大局"P备B1初"是否合理。
"""
import os
import glob
import csv
from collections import defaultdict

COL_周涨 = 1
COL_PR = 2
COL_HR = 3
COL_护型 = 4
COL_波型 = 7
COL_ZC周 = 18

def 提取护级AB(护型):
    if len(护型) >= 4:
        return 护型[3]
    return ''

def 提取值周四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 算周层土型(zc, 护级):
    if zc < 0 and 护级 in ('下', '忑'):
        return '禁'
    elif 护级 in ('中', '下', '忑'):
        return '念'
    elif zc > 0 and 护级 in ('上', '忐'):
        return '沃'
    else:
        return '肋'

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    # 统计: (土型, 四波) -> {口径: [总, 命中]}
    stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))

    n_rows = 0
    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_ZC周:
                    rows.append(row)
        for i, row in enumerate(rows):
            try:
                周涨 = float(row[COL_周涨])
                hr = float(row[COL_HR])
            except (ValueError, IndexError):
                continue
            if i + 1 < len(rows):
                try:
                    下周涨 = float(rows[i+1][COL_周涨])
                    下周hr = float(rows[i+1][COL_HR])
                except (ValueError, IndexError):
                    continue
            else:
                continue
            try:
                zc = int(row[COL_ZC周])
            except (ValueError, IndexError):
                continue
            n_rows += 1
            护级 = 提取护级AB(row[COL_护型])
            四波 = 提取值周四波(row[COL_波型])
            土型 = 算周层土型(zc, 护级)
            key = (土型, 四波)
            # 当前周涨幅≥3%
            stats[key]['当前周涨≥3%'][0] += 1
            if 周涨 >= 3:
                stats[key]['当前周涨≥3%'][1] += 1
            # 下周涨幅≥3%
            stats[key]['下周涨≥3%'][0] += 1
            if 下周涨 >= 3:
                stats[key]['下周涨≥3%'][1] += 1
            # 下周HR≥3%
            stats[key]['下周HR≥3%'][0] += 1
            if 下周hr >= 3:
                stats[key]['下周HR≥3%'][1] += 1

    print(f'总行数: {n_rows}')
    print()
    print('=== 沃土×武 vs 沃土×龙 多口径对比 ===')
    for key in [('沃', '武'), ('沃', '龙')]:
        print(f'\n{key[0]}土×{key[1]}:')
        for 口径 in ('当前周涨≥3%', '下周涨≥3%', '下周HR≥3%'):
            tot, hit = stats[key][口径]
            if tot:
                print(f'  {口径}: {tot} 行, 比例 {hit/tot*100:.2f}%')

if __name__ == '__main__':
    main()