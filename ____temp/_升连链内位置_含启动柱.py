# -*- coding: utf-8 -*-
"""
升连链内位置分析（含启动柱）——统一计数规则
====================================================
统一规则（参照日类 §5.3.6 首柱定义）：
  升连链 = 启动柱（升吞O/升孕o，前面是阴柱）+ 连续升连（Q）
  链内第1根 = 启动柱（从阴转阳的第一根）——"第一个升连"
  链内第2根起 = 升连（Q）——"后续升连"

衡量：介入链内第k个位置，持有到链结束（含链尾）的累计收益。
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

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def main():
    rows = load_data()
    print('总行数:', len(rows))
    by_code = defaultdict(list)
    for row in rows:
        by_code[row['code']].append(row)

    # stat[位置][态][指标]：介入链内第k个位置持有到链末的累计收益
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
                # 找链首启动柱
                start = i
                if i > 0 and 是启动柱(lst[i-1]['并符']):
                    start = i - 1
                # 链 = [start, j)，链长 = j - start
                链长 = j - start
                # 预计算：从每个位置到链尾的累计收益（含链尾）
                累计 = [0.0] * 链长
                for k in range(链长 - 1, -1, -1):
                    累计[k] = lst[start + k]['周涨'] + (累计[k+1] if k+1 < 链长 else 0)
                for k in range(链长):
                    pos = k + 1
                    pos_key = '第4+' if pos >= 4 else f'第{pos}'
                    态 = 四态(lst[start + k]['AB'], lst[start + k]['ZB'])
                    stat[pos_key][态]['n'] += 1
                    stat[pos_key][态]['累计'] += 累计[k]
                i = j
            else:
                i += 1

    print('\n=== 介入链内第k个位置（含启动柱）持有到链末累计收益（全量） ===')
    print(f'{"位置":<6} {"四态":<4} {"n":>10} {"累计均涨":>10}')
    for pos in ('第1', '第2', '第3', '第4+'):
        for 态 in ('龙', '武', '虎', '雀'):
            d = stat[pos][态]
            n = d['n']
            if n == 0: continue
            print(f'{pos:<6} {态:<4} {int(n):>10} {d["累计"]/n:>9.2f}%')

    print('\n=== 龙态下 介入链内第k个位置持有到链末 ===')
    for pos in ('第1', '第2', '第3', '第4+'):
        d = stat[pos]['龙']
        n = d['n']
        if n == 0: continue
        print(f'  龙态{pos}升连: n={int(n)} | 持有到链末累计均涨 {d["累计"]/n:.2f}%')

if __name__ == '__main__':
    main()
