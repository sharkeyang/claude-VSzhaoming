# -*- coding: utf-8 -*-
"""
升连链内位置分析v3（2026-10-11，完整7458文件）
课题：哪一个升连是最好的机会？
方法：介入第k个升连后，持有到链结束（含链尾）的累计收益。
"""
import glob, csv, io, sys, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'


def load_data():
    files = glob.glob(DATA_DIR + '/*.csv')
    rows = []
    for f in files:
        code = f.split('_')[-1].replace('.csv', '')
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                if len(row) >= 49:
                    rows.append({
                        'code': code, '并符': row[48].strip(),
                        '周涨': float(row[1].strip() or 0),
                        '主期': row[0].strip(),
                        'AB': int(row[19].strip() or 0),
                        'ZB': int(row[14].strip() or 0),
                    })
    return rows


def 四态(AB, ZB):
    if AB > 0 and ZB > 0: return '龙'
    if AB < 0 and ZB > 0: return '武'
    if AB < 0 and ZB < 0: return '虎'
    if AB > 0 and ZB < 0: return '雀'
    return '?'


def 是升连(并符):
    return 并符 and 并符[-1] == 'Q'


def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max


def main():
    rows = load_data()
    print('总行数:', len(rows))
    by_code = defaultdict(list)
    for row in rows:
        by_code[row['code']].append(row)

    # stat[位置][态][指标]：介入第k个升连后持有到链结束的累计收益
    stat = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                链长 = j - i
                # 预计算：从每个位置到链尾的累计收益
                # 累计[k] = 从第k个升连到链尾所有升连的周涨之和
                累计 = [0.0] * 链长
                for k in range(链长 - 1, -1, -1):
                    累计[k] = lst[i + k]['周涨'] + (累计[k + 1] if k + 1 < 链长 else 0)
                for k in range(链长):
                    pos = k + 1
                    pos_key = '第4+' if pos >= 4 else f'第{pos}'
                    态 = 四态(lst[i + k]['AB'], lst[i + k]['ZB'])
                    stat[pos_key][态]['n'] += 1
                    stat[pos_key][态]['累计'] += 累计[k]
                i = j
            else:
                i += 1

    print('\n=== 介入第k个升连后持有到链结束的累计收益（全量） ===')
    print(f'{"位置":<6} {"四态":<4} {"n":>10} {"累计均涨":>10}')
    for pos in ('第1', '第2', '第3', '第4+'):
        for 态 in ('龙', '武', '虎', '雀'):
            d = stat[pos][态]
            n = d['n']
            if n == 0:
                continue
            print(f'{pos:<6} {态:<4} {int(n):>10} {d["累计"]/n:>9.2f}%')

    print('\n=== 龙态下 介入第k个升连后持有到链结束 ===')
    for pos in ('第1', '第2', '第3', '第4+'):
        d = stat[pos]['龙']
        n = d['n']
        if n == 0:
            continue
        print(f'  龙态{pos}升连: n={int(n)} | 持有到链结束累计均涨 {d["累计"]/n:.2f}%')


if __name__ == '__main__':
    main()
