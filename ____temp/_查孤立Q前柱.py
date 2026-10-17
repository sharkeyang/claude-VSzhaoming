# -*- coding: utf-8 -*-
"""
查孤立Q（连续Q段第一根，前面无启动柱）的前一根柱形态
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

def 是启动柱(并符):
    return 并符 and 并符[-1] in ('O', 'o')

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

    # 龙态下，连续Q段第一根Q的前一根柱形态
    cnt = collections.Counter()
    cnt_prev_zhang = collections.Counter()
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i] and 四态(lst[i]['AB'], lst[i]['ZB']) == '龙':
                j = i
                while j < len(lst) and 升连标记[j] and 四态(lst[j]['AB'], lst[j]['ZB']) == '龙':
                    j += 1
                if i > 0:
                    prev = lst[i-1]
                    cnt[尾符(prev['并符'])] += 1
                    pz = prev['周涨']
                    if pz > 0: cnt_prev_zhang['阳'] += 1
                    elif pz < 0: cnt_prev_zhang['阴'] += 1
                    else: cnt_prev_zhang['平盘(周涨=0)'] += 1
                else:
                    cnt['(链首无前柱)'] += 1
                i = j
            else:
                i += 1

    total = sum(cnt.values())
    print(f'\n=== 龙态下连续Q段第一根Q的前一根柱形态 ===')
    for k, v in cnt.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')

    print(f'\n=== 龙态下连续Q段第一根Q的前一根周涨分类 ===')
    for k, v in cnt_prev_zhang.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')

if __name__ == '__main__':
    main()
