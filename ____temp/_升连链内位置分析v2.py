# -*- coding: utf-8 -*-
"""
升连链内位置分析v2（2026-10-11，完整7458文件）
区分：链尾升连（链内最后一个，后面无升连）vs 链内升连（后面还有升连）
课题：哪一个升连是最好的机会？
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

    # stat[类型][态][指标]  类型=链尾/链内
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
                for k in range(i, j):
                    # 链尾 = 链内最后一个升连
                    类型 = '链尾' if k == j - 1 else '链内'
                    态 = 四态(lst[k]['AB'], lst[k]['ZB'])
                    if k + 1 < len(lst):
                        nxt = lst[k + 1]
                        nxt_zhang = nxt['周涨']
                        nxt_up = 1 if nxt_zhang > 0 else 0
                        stat[类型][态]['n'] += 1
                        stat[类型][态]['涨'] += nxt_up
                        stat[类型][态]['均涨'] += nxt_zhang
                i = j
            else:
                i += 1

    print('\n=== 链尾升连 vs 链内升连 → 下周获利（全量） ===')
    print(f'{"类型":<6} {"四态":<4} {"n":>10} {"下周均涨":>10} {"上涨率":>8}')
    for 类型 in ('链内', '链尾'):
        for 态 in ('龙', '武', '虎', '雀'):
            d = stat[类型][态]
            n = d['n']
            if n == 0:
                continue
            print(f'{类型:<6} {态:<4} {int(n):>10} {d["均涨"]/n:>9.2f}% {d["涨"]/n*100:>7.1f}%')

    print('\n=== 龙态下 链内升连按位置细分（第1/2/3/4+） ===')
    # 重新统计：龙态链内升连的位置
    stat_pos = defaultdict(lambda: defaultdict(float))
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                for k in range(i, j):
                    if k == j - 1:
                        continue  # 跳过链尾
                    态 = 四态(lst[k]['AB'], lst[k]['ZB'])
                    if 态 != '龙':
                        continue
                    pos = k - i + 1
                    pos_key = '第4+' if pos >= 4 else f'第{pos}'
                    if k + 1 < len(lst):
                        nxt = lst[k + 1]
                        nxt_zhang = nxt['周涨']
                        nxt_up = 1 if nxt_zhang > 0 else 0
                        stat_pos[pos_key]['n'] += 1
                        stat_pos[pos_key]['涨'] += nxt_up
                        stat_pos[pos_key]['均涨'] += nxt_zhang
                i = j
            else:
                i += 1
    for pos in ('第1', '第2', '第3', '第4+'):
        d = stat_pos[pos]
        n = d['n']
        if n == 0:
            continue
        print(f'  龙态{pos}升连(链内): n={int(n)} | 下周均涨 {d["均涨"]/n:.2f}% | 上涨率 {d["涨"]/n*100:.1f}%')


if __name__ == '__main__':
    main()
