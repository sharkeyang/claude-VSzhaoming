# -*- coding: utf-8 -*-
"""
四域 × 四场 交叉分布（2026-10-11）
验证四域能否与四场统一
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

def 四场(ZC, 护):
    if ZC > 0 and 护 in ('上', '忐'): return '主战场'
    if 护 == '中' or (ZC > 0 and 护 in ('下', '忑')): return '执念'
    if 护 == '忠' or (ZC < 0 and 护 in ('上', '忐')): return '鸡肋'
    if ZC < 0 and 护 in ('下', '忑'): return '禁区'
    return '?'

def main():
    files = glob.glob(DATA_DIR + '/*.csv')
    print(f'文件数: {len(files)}')

    # 四域 × 四场 交叉
    cross = defaultdict(lambda: defaultdict(float))
    # 四域 × 四场 下周均涨
    cross_avg = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))

    for fi, f in enumerate(files):
        code = f.split('_')[-1].replace('.csv', '')
        lst = []
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                if len(row) >= 51:
                    lst.append({
                        '周涨': float(row[1].strip() or 0),
                        '日期': row[0].strip(),
                        'AB': int(row[19].strip() or 0),
                        'ZB': int(row[14].strip() or 0),
                        'ZC': int(row[15].strip() or 0),
                        'ZA': int(row[13].strip() or 0),
                        '四域': row[50].strip(),
                    })
        if not lst:
            continue
        lst.sort(key=lambda x: parse_date(x['日期']))

        for i in range(len(lst) - 1):
            cur = lst[i]
            nxt = lst[i+1]
            护 = 护级(cur['AB'], cur['ZA'], cur['ZB'])
            c = 四场(cur['ZC'], 护)
            y = cur['四域']
            cross[y][c] += 1
            cross_avg[y][c][0] += 1
            cross_avg[y][c][1] += nxt['周涨']

        if (fi+1) % 1000 == 0:
            print(f'  已处理 {fi+1}/{len(files)}', flush=True)

    # 输出交叉分布
    print('\n=== 四域 × 四场 交叉分布 ===')
    print(f'{"四域":<6} {"主战场":>10} {"鸡肋":>10} {"执念":>10} {"禁区":>10} {"合计":>10}')
    for y in ('多长', '多被', '空长', '空看'):
        row = [cross[y][c] for c in ('主战场', '鸡肋', '执念', '禁区')]
        total = sum(row)
        print(f'{y:<6} {row[0]:>10} {row[1]:>10} {row[2]:>10} {row[3]:>10} {int(total):>10}')

    # 输出交叉下周均涨
    print('\n=== 四域 × 四场 下周均涨 ===')
    print(f'{"四域":<6} {"主战场":>10} {"鸡肋":>10} {"执念":>10} {"禁区":>10}')
    for y in ('多长', '多被', '空长', '空看'):
        row = []
        for c in ('主战场', '鸡肋', '执念', '禁区'):
            n, s = cross_avg[y][c]
            row.append(f'{s/n:.3f}%' if n > 0 else '—')
        print(f'{y:<6} {row[0]:>10} {row[1]:>10} {row[2]:>10} {row[3]:>10}')

if __name__ == '__main__':
    main()
