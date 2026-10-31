# -*- coding: utf-8 -*-
"""
计算周B趋持有期间，DJC之上(日ZC>0)和DJC之下(日ZC<0)的涨幅贡献。
周B趋介入：WXZC>0 且 AB由负转正 且 ZB>0 且 升连周边(并符串周尾字符Q/O/o)。
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

    介入周 = {}  # fid -> set of 周涨值

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

    # 映射到谕组日CSV
    data_dir2 = r'昭明算展\谕组日'
    files2 = glob.glob(os.path.join(data_dir2, '谕组日_*.csv'))

    总涨幅 = 0.0
    日ZC正涨幅 = 0.0
    日ZC负涨幅 = 0.0
    总日 = 0
    日ZC正日 = 0
    日ZC负日 = 0
    上涨日 = 0
    日ZC正上涨日 = 0

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
        介入周值 = 介入周[fid]
        持有 = False
        for i, row in enumerate(rows):
            try:
                涨幅 = float(row[5])
                日ZC = int(row[14])
                周ZC = int(row[87])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[76])
            if not 持有:
                try:
                    周涨 = float(row[70])
                except (ValueError, IndexError):
                    周涨 = None
                if 周涨 in 介入周值:
                    持有 = True
            if 持有:
                if 周ZC <= 0 or (周ZC > 0 and 四波 == '虎'):
                    持有 = False
                    continue
                总日 += 1
                总涨幅 += 涨幅
                if 日ZC > 0:
                    日ZC正日 += 1
                    日ZC正涨幅 += 涨幅
                    if 涨幅 > 0:
                        日ZC正上涨日 += 1
                else:
                    日ZC负日 += 1
                    日ZC负涨幅 += 涨幅
                if 涨幅 > 0:
                    上涨日 += 1

    print(f'周B趋持有总日数: {总日}')
    print(f'日ZC>0 日数: {日ZC正日} ({日ZC正日/总日*100:.1f}%)')
    print(f'日ZC<0 日数: {日ZC负日} ({日ZC负日/总日*100:.1f}%)')
    print()
    print('=== 涨幅贡献 ===')
    print(f'总涨幅: {总涨幅:.1f}%')
    print(f'日ZC>0 涨幅: {日ZC正涨幅:.1f}% ({日ZC正涨幅/总涨幅*100:.1f}%)')
    print(f'日ZC<0 涨幅: {日ZC负涨幅:.1f}% ({日ZC负涨幅/总涨幅*100:.1f}%)')
    print()
    print('=== 平均涨幅 ===')
    print(f'日ZC>0 平均涨幅: {日ZC正涨幅/日ZC正日:.3f}%')
    print(f'日ZC<0 平均涨幅: {日ZC负涨幅/日ZC负日:.3f}%')
    print()
    print('=== 上涨日 ===')
    print(f'上涨日数: {上涨日} ({上涨日/总日*100:.1f}%)')
    print(f'日ZC>0 上涨日: {日ZC正上涨日} ({日ZC正上涨日/上涨日*100:.1f}%)')

if __name__ == '__main__':
    main()