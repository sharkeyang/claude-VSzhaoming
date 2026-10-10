# -*- coding: utf-8 -*-
"""
周类升连研究迁移验证（2026-10-10）
验证：①周类升连聚集性 ②周类升连后第1柱分布
数据源：昭明算展/谕组导出/谕组周/（5789文件，GBK编码）
字段：并符串周[48]、周涨[1]、主期[0]、AB周[19]、ZB周[14]
升连判定：并符串周尾字符=Q（常枚并符升连）
"""
import glob, csv, io, sys, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组导出/谕组周'

def load_data():
    files = glob.glob(DATA_DIR + '/*.csv')
    rows = []
    for f in files:
        code = f.split('_')[-1].replace('.csv','')
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            header = next(r)
            idx = {c: header.index(c) for c in ['并符串周','周涨','主期','AB周','ZB周']}
            for row in r:
                if len(row) >= 60:
                    rows.append({
                        'code': code,
                        '并符': row[idx['并符串周']].strip(),
                        '周涨': float(row[idx['周涨']].strip() or 0),
                        '主期': row[idx['主期']].strip(),
                        'AB': int(row[idx['AB周']].strip() or 0),
                        'ZB': int(row[idx['ZB周']].strip() or 0),
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
    from collections import defaultdict
    by_code = defaultdict(list)
    for row in rows:
        by_code[row['code']].append(row)

    # ① 周类升连聚集性（龙态）
    print('\n=== ① 周类升连链长度(龙态) ===')
    链长 = collections.Counter()
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i] and 四态(lst[i]['AB'], lst[i]['ZB']) == '龙':
                j = i
                while j < len(lst) and 升连标记[j] and 四态(lst[j]['AB'], lst[j]['ZB']) == '龙':
                    j += 1
                链长[j-i] += 1
                i = j
            else:
                i += 1
    total = sum(链长.values())
    print(f'总链数: {total}')
    for k in sorted(链长.keys()):
        if k >= 1:
            print(f'  链长{k}: {链长[k]} ({链长[k]/total:.1%})')

    # ② 周类升连后第1柱分布（龙态）
    print('\n=== ② 周类升连后第1柱分布(龙态) ===')
    cnt = collections.Counter()
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        for i in range(len(lst)-1):
            if 升连标记[i] and 四态(lst[i]['AB'], lst[i]['ZB']) == '龙':
                nxt = lst[i+1]['并符']
                if nxt:
                    last = nxt[-1]
                    if last == 'Q': 形态 = '升连'
                    elif last == 'W': 形态 = '跌连'
                    elif last == 'O': 形态 = '升吞'
                    elif last == 'V': 形态 = '跌吞'
                    elif last == 'o': 形态 = '升孕'
                    elif last == 'v': 形态 = '跌孕'
                    else: 形态 = '其他'
                    cnt[形态] += 1
    total = sum(cnt.values())
    print(f'总样本: {total}')
    for k, v in cnt.most_common():
        print(f'  {k}: {v} ({v/total:.1%})')

if __name__ == '__main__':
    main()