# -*- coding: utf-8 -*-
"""
待完成任务47：龙/雀跌连镜面对称验证（2026-10-11，完整数据7458文件）
====================================================
课题：依据镜面对称原理：虎/武升连不应介入（不值得），则龙/雀跌连也无需恐惧或剔除。
需数据验证：
  ① 虎/武升连后：下周获利差（不值得介入）—— 升连在下跌趋势是诱多
  ② 龙/雀跌连后：下周获利不差（无需恐惧）—— 跌连在上升趋势是回调，不是转坏

数据源：昭明算展/谕组周/（7458文件，GBK编码）
字段（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    并符串周[48]、周涨[1]、主期[0]、AB周[19]、ZB周[14]
升连判定：并符串周尾字符=Q；跌连判定：尾字符=W
四态判定：AB>0且ZB>0=龙，AB<0且ZB>0=武，AB<0且ZB<0=虎，AB>0且ZB<0=雀
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
            next(r)  # 跳过表头
            for row in r:
                if len(row) >= 49:
                    rows.append({
                        'code': code,
                        '并符': row[48].strip(),
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

    # 统计：升连/跌连 × 四态 → 下周获利
    # stat[形态][态][指标]
    stat = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        for i in range(len(lst) - 1):
            cur = lst[i]
            nxt = lst[i + 1]
            last = 尾符(cur['并符'])
            if last not in ('Q', 'W'):
                continue
            形态 = '升连' if last == 'Q' else '跌连'
            态 = 四态(cur['AB'], cur['ZB'])
            nxt_zhang = nxt['周涨']
            nxt_up = 1 if nxt_zhang > 0 else 0
            stat[形态][态]['n'] += 1
            stat[形态][态]['下周涨'] += nxt_up
            stat[形态][态]['下周均涨'] += nxt_zhang

    print('\n=== 升连/跌连 × 四态 → 下周获利（全量7458文件） ===')
    print(f'{"形态":<4} {"四态":<4} {"n":>10} {"下周均涨":>10} {"上涨率":>8}')
    for 形态 in ('升连', '跌连'):
        for 态 in ('龙', '武', '虎', '雀'):
            d = stat[形态][态]
            n = d['n']
            if n == 0:
                continue
            print(f'{形态:<4} {态:<4} {int(n):>10} {d["下周均涨"]/n:>9.2f}% {d["下周涨"]/n*100:>7.1f}%')

    print('\n=== 镜面对称验证 ===')
    # ① 虎/武升连（下跌趋势升连=诱多，应不值得介入）
    for 态 in ('虎', '武'):
        d = stat['升连'][态]
        n = d['n']
        if n > 0:
            print(f'  ① {态}升连: n={int(n)} | 下周均涨 {d["下周均涨"]/n:.2f}% | 上涨率 {d["下周涨"]/n*100:.1f}%')
    # ② 龙/雀跌连（上升趋势跌连=回调，应无需恐惧）
    for 态 in ('龙', '雀'):
        d = stat['跌连'][态]
        n = d['n']
        if n > 0:
            print(f'  ② {态}跌连: n={int(n)} | 下周均涨 {d["下周均涨"]/n:.2f}% | 上涨率 {d["下周涨"]/n*100:.1f}%')


if __name__ == '__main__':
    main()
