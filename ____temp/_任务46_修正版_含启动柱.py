# -*- coding: utf-8 -*-
"""
任务46 修正版：统一升连链计数规则（含启动柱）
====================================================
统一规则（参照日类 §5.3.6 首柱定义）：
  升连链 = 从启动柱（升吞O/升孕o，前面是阴柱）开始，到连续升连（Q）结束。
  链内第1根 = 启动柱（升吞/升孕，前面是阴柱）——这才是"第一个升连"（从阴转阳的第一根）
  链内第2根起 = 升连（Q）——"后续升连"

验证：链内第1根Q前面 95.3% 是阳柱（升吞50.4%/升孕48.9%），
      所以链内第1根Q不是链的真正起点，真正的起点是它前面的升吞/升孕。
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
    """启动柱 = 升吞O 或 升孕o（前面是阴柱，从阴转阳的第一根）"""
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

    # 方法A：原脚本（链内第1根Q = 第一个升连）
    statA = defaultdict(lambda: defaultdict(float))
    # 方法B：修正版（链首启动柱 = 第一个升连，后续Q = 后续升连）
    statB = defaultdict(lambda: defaultdict(float))

    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                # 方法A：链内第1根Q = 第一个升连
                for k in range(i, j):
                    pos = '第一个升连' if k == i else '后续升连'
                    态 = 四态(lst[k]['AB'], lst[k]['ZB'])
                    if k + 1 < len(lst):
                        nxt = lst[k+1]
                        statA[pos]['n'] += 1
                        statA[pos]['下周涨'] += 1 if nxt['周涨'] > 0 else 0
                        statA[pos]['下周均涨'] += nxt['周涨']
                # 方法B：链首启动柱 = 第一个升连，后续Q = 后续升连
                # 找链首启动柱：第1根Q的前一根，若是升吞/升孕则纳入
                start = i
                if i > 0 and 是启动柱(lst[i-1]['并符']):
                    start = i - 1  # 启动柱纳入链首
                # 链内第1根 = 启动柱（start），后续 = Q（start+1 到 j-1）
                for k in range(start, j):
                    pos = '第一个升连' if k == start else '后续升连'
                    态 = 四态(lst[k]['AB'], lst[k]['ZB'])
                    if k + 1 < len(lst):
                        nxt = lst[k+1]
                        statB[pos]['n'] += 1
                        statB[pos]['下周涨'] += 1 if nxt['周涨'] > 0 else 0
                        statB[pos]['下周均涨'] += nxt['周涨']
                i = j
            else:
                i += 1

    print('\n=== 方法A（原脚本）：链内第1根Q = 第一个升连 ===')
    for pos in ('第一个升连', '后续升连'):
        d = statA[pos]
        n = d['n']
        if n == 0: continue
        print(f'  {pos}: n={int(n)} | 下周均涨 {d["下周均涨"]/n:.2f}% | 上涨率 {d["下周涨"]/n*100:.1f}%')

    print('\n=== 方法B（修正版）：链首启动柱 = 第一个升连 ===')
    for pos in ('第一个升连', '后续升连'):
        d = statB[pos]
        n = d['n']
        if n == 0: continue
        print(f'  {pos}: n={int(n)} | 下周均涨 {d["下周均涨"]/n:.2f}% | 上涨率 {d["下周涨"]/n*100:.1f}%')

if __name__ == '__main__':
    main()
