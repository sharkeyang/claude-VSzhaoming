# -*- coding: utf-8 -*-
"""
找出"链内第1根Q前面是阴柱"的样本，打印出来看
验证：Q(升连)定义=当前柱阳+前柱阳，前面不可能是阴柱
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

    # 找出"链内第1根Q前面是阴柱"的样本
    samples = []
    cnt_prev = collections.Counter()
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
                    prev = lst[i-1]
                    prev_zhang = prev['周涨']
                    cnt_prev['阳' if prev_zhang > 0 else '阴'] += 1
                    if prev_zhang <= 0:  # 前面是阴柱
                        samples.append({
                            'code': code,
                            '主期': lst[i]['主期'],
                            '前柱并符': prev['并符'],
                            '前柱周涨': prev_zhang,
                            '当前并符': lst[i]['并符'],
                            '当前周涨': lst[i]['周涨'],
                        })
                i = j
            else:
                i += 1

    total = sum(cnt_prev.values())
    print(f'\n=== 链内第1根Q的前一根是阳/阴 ===')
    for k, v in cnt_prev.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')

    print(f'\n=== 前面是阴柱的样本（共{len(samples)}个） ===')
    for s in samples[:30]:
        print(f"  {s['code']} {s['主期']} | 前柱并符={s['前柱并符']} 前柱周涨={s['前柱周涨']:.2f}% | 当前并符={s['当前并符']} 当前周涨={s['当前周涨']:.2f}%")

if __name__ == '__main__':
    main()
