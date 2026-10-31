# -*- coding: utf-8 -*-
"""
周级别对照：重建周层Q链①/②/③/④，统计下周冲高率(下一周HR>=3%)。
重建逻辑复现 神谕.bas 2536-2554 行。用 groupby(fid).shift(-1) 取下一周HR。
"""
import os
import glob
import csv
from collections import defaultdict

# 周类列索引
COL_主期 = 0
COL_HR = 3
COL_护型 = 4
COL_波型 = 7
COL_大局周 = 8
COL_层界周 = 9
COL_ZC周 = 18
COL_并符串周 = 51

def 提取护级AB(护型):
    """周护型格式同日护型，护级在第4字符"""
    if len(护型) >= 4:
        return 护型[3]
    return ''

def 提取值周四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 算周层大局(ZC, 护级, 四波, 层界):
    """复现神谕.bas 周层大局逻辑（与日层同构，用周类数据）"""
    if ZC < 0 and 护级 in ('下', '忑'):
        return 'Z退z禁'
    elif ZC < 0:
        if 护级 in ('中', '下', '忑'):
            return 'P备A2储'
        elif 护级 in ('忠', '上', '忐'):
            if 四波 == '龙':
                return 'P备A1储'
            elif 四波 == '武':
                return 'P备B3储'
            else:
                return 'Z退x弃'
    else:
        if 护级 == '忠':
            return 'P备B2再'
        elif 护级 in ('上', '忐'):
            if 四波 == '武':
                return 'P备B1初'
            elif 层界 and 层界[0] == '初':
                return 'A入A初'
            elif 层界 and 层界[0] == '再':
                return 'A入B再'
            else:
                return 'H持G主'
        elif 护级 in ('中', '下', '忑'):
            if 四波 == '龙':
                return 'H持e根'
            elif 四波 == '雀':
                return 'H持v破'
            else:
                return 'Z退y虎'
    return ''

def 算周层Q链(大局, 并符串):
    if not 大局:
        return '_'
    首 = 大局[0]
    if 首 not in ('A', 'H', 'P'):
        return '_'
    if not 并符串:
        return '_'
    if 并符串[-3:] in ('QvO', 'Qvo', 'QVO', 'QVo'):
        return 首 + '③'
    if 并符串[-1:] == 'Q':
        return 首 + '①'
    if 并符串[-2:] in ('Qv', 'QV'):
        return 首 + '②'
    if 并符串[-3:] in ('QvW', 'QVW'):
        return 首 + '④'
    return '_'

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    q_stats = defaultdict(lambda: [0, 0])
    qnum_stats = defaultdict(lambda: [0, 0])
    all_stats = [0, 0]
    noq_stats = [0, 0]
    首_stats = defaultdict(lambda: [0, 0])   # 大局首字符 A/H/P/Z 冲高率（含无Q链）
    首_q_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # 首字符 x Q链

    n_rows = 0
    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_并符串周:
                    rows.append(row)
        # 逐行，下一周HR = 下一行HR
        for i, row in enumerate(rows):
            try:
                hr = float(row[COL_HR])
            except (ValueError, IndexError):
                continue
            # 下一周HR
            if i + 1 < len(rows):
                try:
                    next_hr = float(rows[i+1][COL_HR])
                except (ValueError, IndexError):
                    continue
            else:
                continue
            try:
                zc = int(row[COL_ZC周])
            except (ValueError, IndexError):
                continue
            n_rows += 1
            all_stats[0] += 1
            if next_hr >= 3:
                all_stats[1] += 1

            护级 = 提取护级AB(row[COL_护型])
            四波 = 提取值周四波(row[COL_波型])
            大局 = 算周层大局(zc, 护级, 四波, row[COL_层界周])
            首 = 大局[0] if 大局 else ''
            首_stats[首][0] += 1
            if next_hr >= 3:
                首_stats[首][1] += 1
            q链 = 算周层Q链(大局, row[COL_并符串周])
            if q链 != '_':
                q_stats[q链][0] += 1
                if next_hr >= 3:
                    q_stats[q链][1] += 1
                qnum_stats[q链[1:]][0] += 1
                if next_hr >= 3:
                    qnum_stats[q链[1:]][1] += 1
                首_q_stats[首][q链][0] += 1
                if next_hr >= 3:
                    首_q_stats[首][q链][1] += 1
            else:
                noq_stats[0] += 1
                if next_hr >= 3:
                    noq_stats[1] += 1

    print(f'总行数: {n_rows}')
    tot, hit = all_stats
    print(f'=== 整体基准: {tot} 行, 下周冲高率 {hit/tot*100:.2f}% ===')
    tot, hit = noq_stats
    print(f'=== 无Q链(_): {tot} 行, 冲高率 {hit/tot*100:.2f}% ===')
    print()
    print('=== 周层大局首字符分布（含无Q链） ===')
    for 首 in sorted(首_stats):
        tot, hit = 首_stats[首]
        if tot:
            print(f'  {首}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    print()
    print('=== 按Q链数字汇总 ===')
    for q in sorted(qnum_stats):
        tot, hit = qnum_stats[q]
        if tot:
            print(f'  {q}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    print()
    print('=== 周层Q链 下周冲高率 ===')
    for q in sorted(q_stats):
        tot, hit = q_stats[q]
        if tot:
            print(f'  {q}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    print()
    print('=== 按 大局首字符 x Q链 下周冲高率 ===')
    for 首 in sorted(首_q_stats):
        for q in sorted(首_q_stats[首]):
            tot, hit = 首_q_stats[首][q]
            if tot:
                print(f'  {首} {q}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')

if __name__ == '__main__':
    main()