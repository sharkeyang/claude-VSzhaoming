# -*- coding: utf-8 -*-
"""
待完成任务46：第一个升连 vs 后续升连 获利验证（2026-10-11，完整数据7458文件）
====================================================
课题：升连链内，第一个升连 vs 后续升连，哪个获利更好？
初步（部分文件500个）：第一个升连获利弱（-0.01%，上涨率49.9%），后续升连获利更好（0.70%，上涨率55.7%）。
"第一个升连是最好的介入机会"不成立，需全量确认。

数据源：昭明算展/谕组周/（7458文件，GBK编码）
字段（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    并符串周[48]、周涨[1]、主期[0]、AB周[19]、ZB周[14]
升连判定：并符串周尾字符=Q（常枚并符升连）
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

    # 统计：第一个升连 vs 后续升连 的获利（下周周涨、上涨率）
    # stat[位置][指标] = 计数/累加
    stat = defaultdict(lambda: defaultdict(float))
    # 细分：按四态（龙/武/虎/雀）
    stat_态 = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for code, lst in by_code.items():
        lst.sort(key=lambda x: parse_date(x['主期']))
        升连标记 = [是升连(r['并符']) for r in lst]
        i = 0
        while i < len(lst):
            if 升连标记[i]:
                # 识别升连链
                j = i
                while j < len(lst) and 升连标记[j]:
                    j += 1
                # 链内第1个=第一个升连，第2+个=后续升连
                for k in range(i, j):
                    pos = '第一个升连' if k == i else '后续升连'
                    态 = 四态(lst[k]['AB'], lst[k]['ZB'])
                    # 下周获利
                    if k + 1 < len(lst):
                        nxt = lst[k + 1]
                        nxt_zhang = nxt['周涨']
                        nxt_up = 1 if nxt_zhang > 0 else 0
                        stat[pos]['n'] += 1
                        stat[pos]['下周涨'] += nxt_up
                        stat[pos]['下周均涨'] += nxt_zhang
                        stat_态[pos][态]['n'] += 1
                        stat_态[pos][态]['下周涨'] += nxt_up
                        stat_态[pos][态]['下周均涨'] += nxt_zhang
                i = j
            else:
                i += 1

    print('\n=== 第一个升连 vs 后续升连 获利（全量7458文件） ===')
    for pos in ('第一个升连', '后续升连'):
        d = stat[pos]
        n = d['n']
        if n == 0:
            continue
        print(f'  {pos}: n={n} | 下周均涨 {d["下周均涨"]/n:.2f}% | 上涨率 {d["下周涨"]/n*100:.1f}%')

    print('\n=== 按四态细分 ===')
    for pos in ('第一个升连', '后续升连'):
        print(f'  --- {pos} ---')
        for 态 in ('龙', '武', '虎', '雀'):
            d = stat_态[pos][态]
            n = d['n']
            if n == 0:
                continue
            print(f'    {态}: n={n} | 下周均涨 {d["下周均涨"]/n:.2f}% | 上涨率 {d["下周涨"]/n*100:.1f}%')


if __name__ == '__main__':
    main()
