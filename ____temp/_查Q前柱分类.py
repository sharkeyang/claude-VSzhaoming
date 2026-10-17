# -*- coding: utf-8 -*-
"""
链内第1根Q的前一根柱分类：阳/阴/平盘(周涨=0)
验证：Q(升连)定义=当前柱阳+前柱阳，前面必然是阳柱
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
                    })
    return rows

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

    cnt = collections.Counter()
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                if i > 0:
                    prev_zhang = lst[i-1]['周涨']
                    if prev_zhang > 0: cnt['阳'] += 1
                    elif prev_zhang < 0: cnt['阴'] += 1
                    else: cnt['平盘(周涨=0)'] += 1
                i = j
            else:
                i += 1

    total = sum(cnt.values())
    print(f'\n=== 链内第1根Q的前一根柱分类（全量） ===')
    for k, v in cnt.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')

if __name__ == '__main__':
    main()
