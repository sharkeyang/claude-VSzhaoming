# -*- coding: utf-8 -*-
"""
周类分类区分度验证（2026-10-11）
====================================================
验证四态、四场、四域、六势型的区分度（下周均涨差异）
区分度 = 各分类内下周均涨的最大值 - 最小值，越大越好
"""
import glob, csv, io, sys, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

def 护级(AB, ZA, ZB):
    """WXCD护级：上/中/下/忐/忠/忑"""
    if AB > 0:
        if ZA > 0: return '上'
        elif ZB > 0: return '中'
        else: return '下'
    else:
        if ZB > 0: return '忐'
        elif ZA > 0: return '忠'
        else: return '忑'

def 四态(AB, ZB):
    if AB > 0 and ZB > 0: return '龙'
    if AB < 0 and ZB > 0: return '武'
    if AB < 0 and ZB < 0: return '虎'
    if AB > 0 and ZB < 0: return '雀'
    return '?'

def 四场(ZC, 护):
    if ZC > 0 and 护 in ('上', '忐'): return '主战场'
    if 护 == '中' or (ZC > 0 and 护 in ('下', '忑')): return '执念'
    if 护 == '忠' or (ZC < 0 and 护 in ('上', '忐')): return '鸡肋'
    if ZC < 0 and 护 in ('下', '忑'): return '禁区'
    return '?'

def 六势(CD, ZC, ZD):
    if CD > 0 and ZC > 0: return '金'
    if CD < 0 and ZD > 0: return '仅试_银'
    if CD > 0 and ZD < 0: return '勿_尿'
    if CD > 0 and ZD > 0 and ZC < 0: return '仅观_嘘'
    if CD < 0 and ZD < 0 and ZC > 0: return '仅观_唏'
    if CD < 0 and ZC < 0: return '勿勿勿勿勿_屎'
    return '?'

def main():
    files = glob.glob(DATA_DIR + '/*.csv')
    print(f'文件数: {len(files)}')

    # stat[分类][类别][指标]
    stat = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

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
                        'ZD': int(row[16].strip() or 0),
                        'CD': int(row[24].strip() or 0),
                        'ZA': int(row[13].strip() or 0),
                        '四域': row[50].strip(),
                    })
        if not lst:
            continue
        lst.sort(key=lambda x: parse_date(x['日期']))

        for i in range(len(lst) - 1):
            cur = lst[i]
            nxt = lst[i+1]
            nxt_zhang = nxt['周涨']
            护 = 护级(cur['AB'], cur['ZA'], cur['ZB'])
            # 四态
            t = 四态(cur['AB'], cur['ZB'])
            stat['四态'][t]['n'] += 1
            stat['四态'][t]['下周涨'] += nxt_zhang
            # 四场
            c = 四场(cur['ZC'], 护)
            stat['四场'][c]['n'] += 1
            stat['四场'][c]['下周涨'] += nxt_zhang
            # 四域
            y = cur['四域']
            stat['四域'][y]['n'] += 1
            stat['四域'][y]['下周涨'] += nxt_zhang
            # 六势
            s = 六势(cur['CD'], cur['ZC'], cur['ZD'])
            stat['六势'][s]['n'] += 1
            stat['六势'][s]['下周涨'] += nxt_zhang

        if (fi+1) % 1000 == 0:
            print(f'  已处理 {fi+1}/{len(files)}', flush=True)

    # 输出
    for 分类 in ('四态', '四场', '四域', '六势'):
        print(f'\n=== {分类} 区分度 ===')
        rows = []
        for 类别, d in stat[分类].items():
            n = d['n']
            if n == 0: continue
            rows.append((类别, n, d['下周涨']/n))
        rows.sort(key=lambda r: -r[2])
        print(f'{"类别":<12} {"n":>12} {"下周均涨":>10}')
        for 类别, n, avg in rows:
            print(f'{类别:<12} {int(n):>12} {avg:>9.3f}%')
        if rows:
            max_avg = max(r[2] for r in rows)
            min_avg = min(r[2] for r in rows)
            print(f'  区分度(最大-最小): {max_avg - min_avg:.3f}pp')

if __name__ == '__main__':
    main()
