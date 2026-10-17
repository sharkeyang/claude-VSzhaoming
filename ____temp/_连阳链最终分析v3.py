# -*- coding: utf-8 -*-
"""
连阳链最终分析v3（统一命名，2026-10-11 用户定稿）
====================================================
🔴 统一命名：
  连阳链 = 连续阳柱序列（启动柱O/o + 连续升连Q）
  连阳链第1柱 = 启动柱（升吞O/升孕o，前面是阴柱，从阴转阳第一根）
  连阳链第2柱起 = 升连（Q，前面是阳柱）
  
  Q(升连)定义 = VBA结算.bas 744-747：当前柱阳(PR0>=0)+前柱阳(PR1>=0)
  → Q必然前面是阳柱(或平盘周涨=0，VBA把PR1>=0算成前柱阳)。
  
  🔴 链长定义（用户定稿）：
  升连链长 = 启动柱(1) + 连续Q数 = 连阳链长（含启动柱）
  最小升连链长 = 1(启动柱) + 1(Q) = 2（O,Q）
  "至少2周" = 启动柱 + 至少1根Q
  
  孤立Q = Q前面是平盘(周涨=0)或链首，无启动柱（占少数）
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

def 是阳柱(并符):
    return 并符 and 并符[-1] in ('Q', 'O', 'o')

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def main():
    rows = load_data()
    print('总行数:', len(rows))
    by_code = defaultdict(list)
    for row in rows:
        by_code[row['code']].append(row)

    # ============ ① 连阳链链长分布（龙态，含链长1=单根阳柱） ============
    print('\n=== ① 连阳链链长分布(龙态，含链长1=单根阳柱) ===')
    链长 = collections.Counter()
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        阳标记 = [是阳柱(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 阳标记[i] and 四态(lst[i]['AB'], lst[i]['ZB']) == '龙':
                j = i
                while j < len(lst) and 阳标记[j] and 四态(lst[j]['AB'], lst[j]['ZB']) == '龙':
                    j += 1
                链长[j-i] += 1
                i = j
            else:
                i += 1
    total = sum(链长.values())
    print(f'总链数: {total}')
    for k in sorted(链长.keys()):
        if k <= 8:
            print(f'  链长{k}: {链长[k]} ({链长[k]/total:.1%})')

    # ============ ② 升连链长分布（龙态，含启动柱） ============
    # 升连链 = 启动柱 + 连续Q，链长 = 1 + 连续Q数
    # 孤立Q（前面无启动柱）= 单独计数
    print('\n=== ② 升连链长分布(龙态，含启动柱) ===')
    链长 = collections.Counter()
    孤立Q = 0
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i] and 四态(lst[i]['AB'], lst[i]['ZB']) == '龙':
                j = i
                while j < len(lst) and 升连标记[j] and 四态(lst[j]['AB'], lst[j]['ZB']) == '龙':
                    j += 1
                start = i
                if i > 0 and 是启动柱(lst[i-1]['并符']):
                    start = i - 1
                if start == i:
                    孤立Q += 1  # 前面无启动柱（平盘/链首）
                else:
                    链长[j-start] += 1  # 含启动柱
                i = j
            else:
                i += 1
    total = sum(链长.values()) + 孤立Q
    print(f'总链数: {total}（含启动柱{sum(链长.values())} + 孤立Q{孤立Q}）')
    for k in sorted(链长.keys()):
        if k <= 8:
            print(f'  链长{k}: {链长[k]} ({链长[k]/total:.1%})')
    print(f'  孤立Q(前面无启动柱): {孤立Q} ({孤立Q/total:.1%})')

    # ============ ③ 升连链第k柱介入持有到链末累计收益（龙态，含启动柱） ============
    print('\n=== ③ 升连链第k柱介入持有到链末累计收益(龙态，含启动柱) ===')
    stat = defaultdict(lambda: defaultdict(float))
    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i] and 四态(lst[i]['AB'], lst[i]['ZB']) == '龙':
                j = i
                while j < len(lst) and 升连标记[j] and 四态(lst[j]['AB'], lst[j]['ZB']) == '龙':
                    j += 1
                start = i
                if i > 0 and 是启动柱(lst[i-1]['并符']):
                    start = i - 1
                链长 = j - start
                累计 = [0.0] * 链长
                for k in range(链长-1, -1, -1):
                    累计[k] = lst[start+k]['周涨'] + (累计[k+1] if k+1 < 链长 else 0)
                for k in range(链长):
                    pos = k + 1
                    pos_key = '第4+' if pos >= 4 else f'第{pos}'
                    stat[pos_key]['n'] += 1
                    stat[pos_key]['累计'] += 累计[k]
                i = j
            else:
                i += 1
    print(f'{"位置":<6} {"n":>10} {"累计均涨":>10}')
    for pos in ('第1', '第2', '第3', '第4+'):
        d = stat[pos]
        n = d['n']
        if n == 0: continue
        print(f'{pos:<6} {int(n):>10} {d["累计"]/n:>9.2f}%')

if __name__ == '__main__':
    main()
