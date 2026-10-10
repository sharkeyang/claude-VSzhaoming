# -*- coding: utf-8 -*-
"""
周级别升连研究分析脚本（2026-10-09）
分析：升连位置四态分布、各四态/波型升连获利、龙震芽升吞介入、周首升连+涨幅限制
数据源：昭明算展/谕组周/（全量7459文件）
"""
import glob, csv, io, sys, collections, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'

def load_data():
    files = glob.glob(DATA_DIR + '/*.csv')
    rows = []
    for f in files:
        code = f.split('_')[-1].replace('.csv','')
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            header = next(r)
            idx = {c: header.index(c) for c in ['柱排周','波型','AB周','ZB周','周涨','主期']}
            for row in r:
                if len(row) >= 60:
                    rows.append({
                        'code': code,
                        '柱排': row[idx['柱排周']].strip(),
                        '波型': row[idx['波型']].strip(),
                        'AB': int(row[idx['AB周']].strip() or 0),
                        'ZB': int(row[idx['ZB周']].strip() or 0),
                        '周涨': float(row[idx['周涨']].strip() or 0),
                        '主期': row[idx['主期']].strip(),
                    })
    return rows

def 四态(AB, ZB):
    if AB > 0 and ZB > 0: return '龙'
    if AB < 0 and ZB > 0: return '武'
    if AB < 0 and ZB < 0: return '虎'
    if AB > 0 and ZB < 0: return '雀'
    return '?'

def 是升连(柱排):
    return '升.尾连' in 柱排

def 波型细类(波型):
    if '龙扩' in 波型: return '龙扩'
    if '龙震芽' in 波型: return '龙震芽'
    if '龙震根' in 波型: return '龙震根'
    if '龙震〇' in 波型: return '龙震〇'
    if '龙头返' in 波型: return '龙头返'
    if '龙头交' in 波型: return '龙头交'
    if '龙头' in 波型: return '龙头'
    if '龙震' in 波型: return '龙震'
    return '其他'

def 柱排类(柱排):
    if '升.尾连' in 柱排: return '升连'
    if '升.尾吞' in 柱排: return '升吞'
    if '升.尾反孕' in 柱排: return '升反孕'
    if '升.尾孕' in 柱排: return '升孕'
    return '其他'

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def main():
    rows = load_data()
    print('总行数:', len(rows))
    from collections import defaultdict
    by_code = defaultdict(list)
    for row in rows:
        by_code[row['code']].append(row)

    # 1. 升连位置四态分布
    print('\n=== 1. 升连位置 四态分布 ===')
    cnt = collections.Counter()
    for row in rows:
        if 是升连(row['柱排']):
            cnt[四态(row['AB'], row['ZB'])] += 1
    total = sum(cnt.values())
    for k, v in cnt.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')
    print(f'  升连总数: {total}')

    # 2. 各四态升连获利
    print('\n=== 2. 各四态升连 下周获利 ===')
    获利 = defaultdict(list)
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        for i in range(len(lst)-1):
            if 是升连(lst[i]['柱排']):
                st = 四态(lst[i]['AB'], lst[i]['ZB'])
                获利[st].append(lst[i+1]['周涨'])
    for st in ['龙','武','虎','雀']:
        vals = 获利.get(st, [])
        if vals:
            avg = sum(vals)/len(vals)
            pos = sum(1 for v in vals if v > 0)/len(vals)
            big = sum(1 for v in vals if v >= 3)/len(vals)
            print(f'  {st}: n={len(vals)} 下周均涨={avg:.2f}% 上涨率={pos:.1%} 下周≥3%={big:.1%}')

    # 3. 龙四态下各波型细类升连获利
    print('\n=== 3. 龙四态下各波型细类 升连获利 ===')
    获利 = defaultdict(list)
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        for i in range(len(lst)-1):
            if 四态(lst[i]['AB'], lst[i]['ZB']) == '龙' and 是升连(lst[i]['柱排']):
                wb = 波型细类(lst[i]['波型'])
                获利[wb].append(lst[i+1]['周涨'])
    for wb in ['龙扩','龙震芽','龙震根','龙震〇','龙头返','龙头交']:
        vals = 获利.get(wb, [])
        if vals:
            avg = sum(vals)/len(vals)
            pos = sum(1 for v in vals if v > 0)/len(vals)
            big = sum(1 for v in vals if v >= 3)/len(vals)
            print(f'  {wb}: n={len(vals)} 下周均涨={avg:.2f}% 上涨率={pos:.1%} 下周≥3%={big:.1%}')

    # 4. 龙震芽/龙头返位置 各柱排类获利
    print('\n=== 4. 龙震芽/龙头返位置 各柱排类获利 ===')
    for 波 in ['龙震芽','龙头返']:
        print(f'  --- {波} ---')
        获利 = defaultdict(list)
        for code, lst in by_code.items():
            lst.sort(key=lambda x: parse_date(x['主期']))
            for i in range(len(lst)-1):
                if 波 in lst[i]['波型']:
                    cp = 柱排类(lst[i]['柱排'])
                    获利[cp].append(lst[i+1]['周涨'])
        for cp in ['升连','升吞','升反孕','升孕','其他']:
            vals = 获利.get(cp, [])
            if vals:
                avg = sum(vals)/len(vals)
                pos = sum(1 for v in vals if v > 0)/len(vals)
                big = sum(1 for v in vals if v >= 3)/len(vals)
                print(f'    {cp}: n={len(vals)} 下周均涨={avg:.2f}% 上涨率={pos:.1%} 下周≥3%={big:.1%}')

    # 5. 周首升连(龙扩) + 涨幅限制
    print('\n=== 5. 周首升连(龙扩) + 涨幅限制 下周获利 ===')
    获利 = defaultdict(list)
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        for i in range(len(lst)-1):
            if 四态(lst[i]['AB'], lst[i]['ZB']) == '龙' and '龙扩' in lst[i]['波型'] and 是升连(lst[i]['柱排']):
                is_first = (i == 0) or (not 是升连(lst[i-1]['柱排']))
                if is_first:
                    zf = lst[i]['周涨']
                    if zf >= 3: key = '涨幅≥3%'
                    elif zf >= 2: key = '涨幅≥2%'
                    elif zf >= 1: key = '涨幅≥1%'
                    else: key = '涨幅<1%'
                    获利[key].append(lst[i+1]['周涨'])
    for key in ['涨幅≥3%','涨幅≥2%','涨幅≥1%','涨幅<1%']:
        vals = 获利.get(key, [])
        if vals:
            avg = sum(vals)/len(vals)
            pos = sum(1 for v in vals if v > 0)/len(vals)
            big = sum(1 for v in vals if v >= 3)/len(vals)
            print(f'  {key}: n={len(vals)} 下周均涨={avg:.2f}% 上涨率={pos:.1%} 下周≥3%={big:.1%}')

    # 6. 龙震芽升吞 + 涨幅限制
    print('\n=== 6. 龙震芽升吞 + 涨幅限制 下周获利 ===')
    获利 = defaultdict(list)
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        for i in range(len(lst)-1):
            if '龙震芽' in lst[i]['波型'] and '升.尾吞' in lst[i]['柱排']:
                zf = lst[i]['周涨']
                if zf >= 3: key = '涨幅≥3%'
                elif zf >= 2: key = '涨幅≥2%'
                elif zf >= 1: key = '涨幅≥1%'
                else: key = '涨幅<1%'
                获利[key].append(lst[i+1]['周涨'])
    for key in ['涨幅≥3%','涨幅≥2%','涨幅≥1%','涨幅<1%']:
        vals = 获利.get(key, [])
        if vals:
            avg = sum(vals)/len(vals)
            pos = sum(1 for v in vals if v > 0)/len(vals)
            big = sum(1 for v in vals if v >= 3)/len(vals)
            print(f'  {key}: n={len(vals)} 下周均涨={avg:.2f}% 上涨率={pos:.1%} 下周≥3%={big:.1%}')

if __name__ == '__main__':
    main()