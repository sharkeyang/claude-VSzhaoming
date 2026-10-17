# -*- coding: utf-8 -*-
"""
检查周类升连链首柱形态：链内第1根Q前面是什么柱？
验证用户观点：第一个升连前面是阴柱，所以第一个升连其实不是升连（是启动柱）
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

def 尾符(并符):
    return 并符[-1] if 并符 else ''

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def main():
    rows = load_data()
    print('总行数:', len(rows))
    by_code = defaultdict(list)
    for row in rows:
        by_code[row['code']].append(row)

    # 检查：链内第1根Q的前一根柱是什么形态？
    # 以及：链内第1根Q本身，它前面是阳柱还是阴柱？
    cnt_prev = collections.Counter()  # 第1根Q的前一根柱形态
    cnt_first = collections.Counter()  # 第1根Q本身形态（应该都是Q）
    cnt_prev_阴阳 = collections.Counter()  # 第1根Q的前一根是阳/阴

    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                # 链内第1根Q = lst[i]，看它前一根 lst[i-1]
                if i > 0:
                    prev = lst[i-1]['并符']
                    cnt_prev[尾符(prev)] += 1
                    # 判断前一根是阳还是阴（用周涨）
                    prev_zhang = lst[i-1]['周涨']
                    if prev_zhang > 0: cnt_prev_阴阳['阳'] += 1
                    else: cnt_prev_阴阳['阴'] += 1
                else:
                    cnt_prev['(链首无前柱)'] += 1
                i = j
            else:
                i += 1

    total = sum(cnt_prev.values())
    print(f'\n=== 链内第1根Q的前一根柱形态（全量） ===')
    print(f'总样本: {total}')
    for k, v in cnt_prev.most_common():
        print(f'  前柱={k}: {v} ({v/total:.1%})')

    print(f'\n=== 链内第1根Q的前一根是阳/阴 ===')
    for k, v in cnt_prev_阴阳.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')

if __name__ == '__main__':
    main()
