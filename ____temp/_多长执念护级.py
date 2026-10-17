# -*- coding: utf-8 -*-
"""
验证：多长（ZC>0且CD>0且ZB>0）落入执念的护级分布
"""
import glob, csv, io, sys, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def 护级(AB, ZA, ZB):
    if AB > 0:
        if ZA > 0: return '上'
        elif ZB > 0: return '中'
        else: return '下'
    else:
        if ZB > 0: return '忐'
        elif ZA > 0: return '忠'
        else: return '忑'

def main():
    files = glob.glob(DATA_DIR + '/*.csv')
    print(f'文件数: {len(files)}')

    # 多长（ZC>0且CD>0且ZB>0）的护级分布
    cnt = collections.Counter()
    for fi, f in enumerate(files):
        code = f.split('_')[-1].replace('.csv', '')
        lst = []
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                if len(row) >= 25:
                    lst.append({
                        'AB': int(row[19].strip() or 0),
                        'ZB': int(row[14].strip() or 0),
                        'ZC': int(row[15].strip() or 0),
                        'CD': int(row[24].strip() or 0),
                        'ZA': int(row[13].strip() or 0),
                    })
        if not lst:
            continue
        for r in lst:
            if r['ZC'] > 0 and r['CD'] > 0 and r['ZB'] > 0:  # 多长
                护 = 护级(r['AB'], r['ZA'], r['ZB'])
                cnt[护] += 1
        if (fi+1) % 1000 == 0:
            print(f'  已处理 {fi+1}/{len(files)}', flush=True)

    total = sum(cnt.values())
    print(f'\n=== 多长（ZC>0且CD>0且ZB>0）的护级分布 ===')
    for k, v in cnt.most_common():
        print(f'  护级{k}: {v} ({v/total:.1%})')

if __name__ == '__main__':
    main()
