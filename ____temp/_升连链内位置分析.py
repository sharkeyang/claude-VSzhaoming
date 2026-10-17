# -*- coding: utf-8 -*-
"""
升连链内位置分析（2026-10-11，完整7458文件）
课题：哪一个升连是最好的机会？
细分链内位置（第1/2/3/4+个升连）的获利，按四态细分。
数据源：昭明算展/谕组周/（7458文件，GBK编码）
字段：并符串周[48]、周涨[1]、主期[0]、AB周[19]、ZB周[14]
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

    # stat[位置][态][指标]
    stat = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    # 按链长分组：链长2/3/4+
    stat_链长 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))

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
                for k in range(i, j):
                    pos = k - i + 1  # 链内第几个
                    pos_key = '第4+' if pos >= 4 else f'第{pos}'
                    态 = 四态(lst[k]['AB'], lst[k]['ZB'])
                    if k + 1 < len(lst):
                        nxt = lst[k + 1]
                        nxt_zhang = nxt['周涨']
                        nxt_up = 1 if nxt_zhang > 0 else 0
                        stat[pos_key][态]['n'] += 1
                        stat[pos_key][态]['涨'] += nxt_up
                        stat[pos_key][态]['均涨'] += nxt_zhang
                        # 链长分组
                        链长_key = '链长4+' if 链长 >= 4 else f'链长{链长}'
                        stat_链长[链长_key][pos_key][态]['n'] += 1
                        stat_链长[链长_key][pos_key][态]['涨'] += nxt_up
                        stat_链长[链长_key][pos_key][态]['均涨'] += nxt_zhang
                i = j
            else:
                i += 1

    print('\n=== 链内位置 × 四态 → 下周获利（全量） ===')
    print(f'{"位置":<6} {"四态":<4} {"n":>10} {"下周均涨":>10} {"上涨率":>8}')
    for pos in ('第1', '第2', '第3', '第4+'):
        for 态 in ('龙', '武', '虎', '雀'):
            d = stat[pos][态]
            n = d['n']
            if n == 0:
                continue
            print(f'{pos:<6} {态:<4} {int(n):>10} {d["均涨"]/n:>9.2f}% {d["涨"]/n*100:>7.1f}%')

    print('\n=== 龙态下 链内位置 × 链长 → 下周获利 ===')
    print(f'{"链长":<8} {"位置":<6} {"n":>10} {"下周均涨":>10} {"上涨率":>8}')
    for 链长_key in ('链长2', '链长3', '链长4+'):
        for pos in ('第1', '第2', '第3', '第4+'):
            d = stat_链长[链长_key][pos]['龙']
            n = d['n']
            if n == 0:
                continue
            print(f'{链长_key:<8} {pos:<6} {int(n):>10} {d["均涨"]/n:>9.2f}% {d["涨"]/n*100:>7.1f}%')


if __name__ == '__main__':
    main()
