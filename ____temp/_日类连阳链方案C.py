# -*- coding: utf-8 -*-
"""
日类连阳链方案C（2026-10-11）
====================================================
方案C：先识别完整连阳链（不被筛选截断），再按链内位置统计介入收益。
- 在原始数据（不过滤）上识别连阳链，连续Q不被筛选条件打断
- 介入收益统计时，只统计满足筛选条件（日ZC>0 + 甲乙己）的介入点
"""
import glob, csv, io, sys, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组日'

def 是升连(并符):
    return 并符 and 并符[-1] == 'Q'

def 是启动柱(并符):
    return 并符 and 并符[-1] in ('O', 'o')

def 是阳柱(并符):
    return 并符 and 并符[-1] in ('Q', 'O', 'o')

def 甲乙己(护型):
    return 护型 and 护型[0] in ('a', 'b', 'r')

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def main():
    files = glob.glob(DATA_DIR + '/*.csv')
    print(f'文件数: {len(files)}')

    # 升连链长分布（含启动柱，原始数据识别）
    链长 = collections.Counter()
    孤立Q = 0
    # 升连链第k柱介入收益（只统计满足筛选条件的介入点）
    stat = defaultdict(lambda: defaultdict(float))

    for fi, f in enumerate(files):
        code = f.split('_')[-1].replace('.csv', '')
        lst = []
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                if len(row) >= 35:
                    lst.append({
                        '并符': row[34].strip(),
                        '涨幅': float(row[5].strip() or 0),
                        '日期': row[0].strip(),
                        'ZC': float(row[14].strip() or 0),
                        '护型': row[9].strip(),
                    })
        if not lst:
            continue
        lst.sort(key=lambda x: parse_date(x['日期']))

        # 在原始数据上识别连阳链（连续Q不被筛选打断）
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                # 找链首启动柱
                start = i
                if i > 0 and 是启动柱(lst[i-1]['并符']):
                    start = i - 1
                if start == i:
                    孤立Q += 1
                else:
                    链长[j-start] += 1
                # 链内第k柱介入收益（只统计满足筛选条件的介入点）
                链长_ = j - start
                累计 = [0.0] * 链长_
                for k in range(链长_-1, -1, -1):
                    累计[k] = lst[start+k]['涨幅'] + (累计[k+1] if k+1 < 链长_ else 0)
                for k in range(链长_):
                    r = lst[start+k]
                    # 只统计满足筛选条件的介入点
                    if r['ZC'] > 0 and 甲乙己(r['护型']):
                        pos = k + 1
                        pos_key = '第4+' if pos >= 4 else f'第{pos}'
                        stat[pos_key]['n'] += 1
                        stat[pos_key]['累计'] += 累计[k]
                i = j
            else:
                i += 1

        if (fi+1) % 1000 == 0:
            print(f'  已处理 {fi+1}/{len(files)}', flush=True)

    # 输出
    print('\n=== 升连链长分布(含启动柱，原始数据识别) ===')
    total = sum(链长.values()) + 孤立Q
    print(f'总链数: {total}（含启动柱{sum(链长.values())} + 孤立Q{孤立Q}）')
    for k in sorted(链长.keys()):
        if k <= 10:
            print(f'  链长{k}: {链长[k]} ({链长[k]/total:.1%})')
    print(f'  孤立Q(前面无启动柱): {孤立Q} ({孤立Q/total:.1%})')

    print('\n=== 升连链第k柱介入持有到链末累计收益(只统计满足筛选条件的介入点) ===')
    print(f'{"位置":<6} {"n":>10} {"累计均涨":>10}')
    for pos in ('第1', '第2', '第3', '第4+'):
        d = stat[pos]
        n = d['n']
        if n == 0: continue
        print(f'{pos:<6} {int(n):>10} {d["累计"]/n:>9.2f}%')

if __name__ == '__main__':
    main()
