# -*- coding: utf-8 -*-
"""
验证周B趋介入点之后，DJC之上(日ZC>0)是否覆盖主要上升机会、能否提高收益。
周B趋介入：WXZC>0 且 AB由负转正 且 ZB>0 且 升连周边(并符串周尾字符Q/O/o)。
用周类CSV找介入周，映射到谕组日CSV验证。
"""
import os
import glob
import csv

COL_周涨 = 1
COL_波型 = 7
COL_ZB周 = 17
COL_ZC周 = 18
COL_AB周 = 22
COL_并符串周 = 51

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 是升连周边(并符串):
    if not 并符串:
        return False
    return 并符串[-1] in ('Q', 'O', 'o')

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    # 每只股票的周B趋介入周集合（用周涨标记介入周）
    介入周 = {}  # fid -> set of 周涨值（介入当周）

    for f in files:
        fid = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_并符串周:
                    rows.append(row)
        if not rows:
            continue
        前AB = None
        for i, row in enumerate(rows):
            try:
                zc = int(row[COL_ZC周])
                ab = int(row[COL_AB周])
                zb = int(row[COL_ZB周])
                周涨 = float(row[COL_周涨])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_波型])
            并符串 = row[COL_并符串周]
            ab转正 = (前AB is not None and 前AB < 0 and ab > 0)
            if zc > 0 and ab转正 and zb > 0 and 是升连周边(并符串):
                介入周.setdefault(fid, set()).add(周涨)
            前AB = ab

    print(f'有周B趋介入的股票数: {len(介入周)}')

    # 映射到谕组日CSV验证
    data_dir2 = r'昭明算展\谕组日'
    files2 = glob.glob(os.path.join(data_dir2, '谕组日_*.csv'))

    # 周B趋持有：介入周之后，WXZC>0 且非虎
    周B_收益 = []
    周B_正日 = 0
    周B_总日 = 0
    周B_内_日ZC正 = 0
    周B_内_上涨日 = 0
    周B_内_日ZC正_上涨 = 0
    # 周B趋+DJC之上
    日B_收益 = []
    日B_正日 = 0
    日B_总日 = 0

    for f in files2:
        fid = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        if fid not in 介入周:
            continue
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > 87:
                    rows.append(row)
        if not rows:
            continue
        # 介入周值 = 周CSV介入周的周涨值集合（同一周多日周涨相同，可唯一匹配）
        介入周值 = 介入周[fid]
        # 遍历日线，从介入周开始持有
        持有 = False
        for i, row in enumerate(rows):
            try:
                涨幅 = float(row[5])
                日ZC = int(row[14])
                周ZC = int(row[87])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[76])
            # 判断是否进入介入周
            if not 持有:
                try:
                    周涨 = float(row[70])
                except (ValueError, IndexError):
                    周涨 = None
                if 周涨 in 介入周值:
                    持有 = True
            if 持有:
                # 退出：WXZC<=0 或虎（持有条件=WXZC>0 且非虎）
                if 周ZC <= 0 or (周ZC > 0 and 四波 == '虎'):
                    持有 = False
                    continue
                周B_收益.append(涨幅)
                周B_总日 += 1
                if 涨幅 > 0:
                    周B_正日 += 1
                    周B_内_上涨日 += 1
                if 日ZC > 0:
                    周B_内_日ZC正 += 1
                    if 涨幅 > 0:
                        周B_内_日ZC正_上涨 += 1
                    日B_收益.append(涨幅)
                    日B_总日 += 1
                    if 涨幅 > 0:
                        日B_正日 += 1

    if not 周B_收益:
        print('无周B趋持有数据')
        return
    周B_期望 = sum(周B_收益)/len(周B_收益)
    日B_期望 = sum(日B_收益)/len(日B_收益)
    周B_年化 = (1 + 周B_期望/100)**250 - 1
    日B_年化 = (1 + 日B_期望/100)**250 - 1

    print(f'周B趋持有日数: {周B_总日}')
    print(f'周B趋持有内 日ZC>0: {周B_内_日ZC正} ({周B_内_日ZC正/周B_总日*100:.1f}%)')
    print(f'周B趋持有内 上涨日: {周B_内_上涨日} ({周B_内_上涨日/周B_总日*100:.1f}%)')
    print(f'上涨日中 日ZC>0 覆盖: {周B_内_日ZC正_上涨}/{周B_内_上涨日} = {周B_内_日ZC正_上涨/周B_内_上涨日*100:.1f}%')
    print()
    print('=== 周B趋 vs 周B趋+DJC之上 收益对比 ===')
    print(f'周B趋: 平均日收益 {周B_期望:.3f}%, 上涨率 {周B_正日/周B_总日*100:.1f}%, 年化 {周B_年化*100:.1f}%')
    print(f'周B趋+DJC之上: 平均日收益 {日B_期望:.3f}%, 上涨率 {日B_正日/日B_总日*100:.1f}%, 年化 {日B_年化*100:.1f}%')
    print(f'DJC之上 vs 周B趋: {日B_期望 - 周B_期望:+.3f}pp/日')
    print(f'DJC之上持有日占比: {日B_总日}/{周B_总日} = {日B_总日/周B_总日*100:.1f}%')

if __name__ == '__main__':
    main()