# -*- coding: utf-8 -*-
"""
验证周B趋涨幅贡献（修复版）：直接用谕组日CSV的周类指标判断周B趋介入，不依赖周涨值匹配。
周B趋介入：周ZC>0 且 周AB由负转正(前一日周AB<0,当日>0) 且 周ZB>0 且 升连周边(周并符串尾字符Q/O/o)。
持有：介入后，周ZC>0 且非虎；退出：周ZC<=0 或(周ZC>0且虎)。
"""
import os
import glob
import csv

COL_涨幅 = 5
COL_日ZC = 14
COL_周波型 = 76
COL_周ZB = 86
COL_周ZC = 87
COL_周AB = 91
COL_周并符串 = 120

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 是升连周边(并符串):
    if not 并符串:
        return False
    return 并符串[-1] in ('Q', 'O', 'o')

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    总涨幅 = 0.0
    日ZC正涨幅 = 0.0
    日ZC负涨幅 = 0.0
    总日 = 0
    日ZC正日 = 0
    日ZC负日 = 0
    上涨日 = 0
    日ZC正上涨日 = 0
    介入次数 = 0
    周B_收益 = []      # 周B趋全持有日收益
    日B_收益 = []      # 周B趋+DJC之上日收益

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_周并符串:
                    rows.append(row)
        if not rows:
            continue
        持有 = False
        前AB = None
        for i, row in enumerate(rows):
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
                周ZC = int(row[COL_周ZC])
                周AB = int(row[COL_周AB])
                周ZB = int(row[COL_周ZB])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_周波型])
            并符串 = row[COL_周并符串]

            # 退出检测（持有中）
            if 持有:
                if 周ZC <= 0 or (周ZC > 0 and 四波 == '虎'):
                    持有 = False

            # 介入检测（空仓中）：周ZC>0 且 AB由负转正 且 ZB>0 且 升连周边
            if not 持有:
                ab转正 = (前AB is not None and 前AB < 0 and 周AB > 0)
                if 周ZC > 0 and ab转正 and 周ZB > 0 and 是升连周边(并符串):
                    持有 = True
                    介入次数 += 1

            if 持有:
                总日 += 1
                总涨幅 += 涨幅
                周B_收益.append(涨幅)
                if 日ZC > 0:
                    日ZC正日 += 1
                    日ZC正涨幅 += 涨幅
                    日B_收益.append(涨幅)
                    if 涨幅 > 0:
                        日ZC正上涨日 += 1
                else:
                    日ZC负日 += 1
                    日ZC负涨幅 += 涨幅
                if 涨幅 > 0:
                    上涨日 += 1

            前AB = 周AB

    print(f'周B趋介入次数: {介入次数}')
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
    print()
    print('=== 年化收益（250日复利） ===')
    周B_期望 = sum(周B_收益)/len(周B_收益)
    日B_期望 = sum(日B_收益)/len(日B_收益)
    周B_年化 = (1 + 周B_期望/100)**250 - 1
    日B_年化 = (1 + 日B_期望/100)**250 - 1
    print(f'周B趋全持有: 平均日收益 {周B_期望:.3f}%, 年化 {周B_年化*100:.1f}%')
    print(f'周B趋+DJC之上: 平均日收益 {日B_期望:.3f}%, 年化 {日B_年化*100:.1f}%')
    print(f'DJC之上 vs 周B趋: {日B_期望 - 周B_期望:+.3f}pp/日')

if __name__ == '__main__':
    main()