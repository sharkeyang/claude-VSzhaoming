# -*- coding: utf-8 -*-
"""
补充验证用户猜想（2026-11-14）：
  猜想1：坏信号（离顶后跌连/跌吞+升孕/阴阳阴/下破DJA）、DJA之上vs之下
  猜想2：合顶 vs 离顶

数据：昭明算展/谕组日/谕组日_*.csv（GBK，135列）
列索引：0=日期, 5=涨幅, 16=日ZA, 17=日ZC, 18=日ZE, 28=次日高幅, 36=并符串, 44=顶型, 68=DTZB, 70=DTAB
并符串编码：Q=升连, O=升吞, o=升孕, W=跌连, V=跌吞, v=跌孕
顶型：a=龙a(触顶), b=龙b(近顶), c=雀, d=虎, e=非, f=武
"""
import csv, glob, os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')

def load_rows(path):
    with open(path, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        return list(r)

def parse_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

def parse_int(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    # 聚合统计：key -> [count, sum_hr, count_p3]
    stats = {}
    def add(key, hr):
        s = stats.setdefault(key, [0, 0.0, 0])
        s[0] += 1
        s[1] += hr
        if hr >= 3:
            s[2] += 1
    n = 0
    for f in files:
        rows = load_rows(f)
        if len(rows) < 100:
            continue
        n += 1
        for i in range(len(rows) - 1):
            row = rows[i]
            nxt = rows[i + 1]
            hr = parse_float(nxt[28])
            if hr is None:
                continue
            dx = row[44].strip()   # 顶型
            bf = row[36].strip()   # 并符串
            za = parse_int(row[16])  # 日ZA
            zc = parse_int(row[17])  # 日ZC
            ze = parse_int(row[18])  # 日ZE
            t = dx[0] if dx else '?'
            last = bf[-1] if bf else '?'
            # 猜想2：合顶 vs 离顶
            if t == 'a':
                add('合顶_龙a', hr)
            elif t == 'b':
                add('近顶_龙b', hr)
            elif t in ('c', 'd'):
                add('离顶_雀虎', hr)
            elif t == 'e':
                add('离顶_非', hr)
            # 猜想1：DJA之上 vs 之下
            if za > 0:
                add('DJA之上', hr)
            else:
                add('DJA之下', hr)
            # 猜想1：坏信号（离顶后跌连/跌吞）
            if t in ('c', 'd', 'e') and last in ('W', 'V'):
                add('坏信号_离顶后跌连跌吞', hr)
            # 猜想1：好排列（升连/升吞/跌孕）在DJA之上
            if za > 0 and last in ('Q', 'O', 'v'):
                add('DJA之上_好排列', hr)
            # 猜想1：坏排列（跌连/跌吞）在DJA之上
            if za > 0 and last in ('W', 'V'):
                add('DJA之上_坏排列', hr)
            # 猜想1：下破DJA（ZA由正转负）
            if i > 0:
                prev_za = parse_int(rows[i-1][16])
                if prev_za > 0 and za < 0:
                    add('下破DJA', hr)
        if n % 1000 == 0:
            print(f'  已处理 {n} 个文件...', flush=True)
    print(f'有效文件数: {n}', flush=True)
    print('=' * 60)
    print('【猜想2】合顶 vs 离顶 的次日冲高率')
    print('-' * 60)
    for key in ['合顶_龙a', '近顶_龙b', '离顶_雀虎', '离顶_非']:
        if key not in stats:
            continue
        cnt, ssum, p3cnt = stats[key]
        p3 = p3cnt / cnt * 100
        avg = ssum / cnt
        print(f'  {key}: n={cnt}, 次日冲高率={p3:.1f}%, 平均次日高幅={avg:.2f}%')
    print('=' * 60)
    print('【猜想1】DJA之上 vs 之下')
    print('-' * 60)
    for key in ['DJA之上', 'DJA之下']:
        if key not in stats:
            continue
        cnt, ssum, p3cnt = stats[key]
        p3 = p3cnt / cnt * 100
        avg = ssum / cnt
        print(f'  {key}: n={cnt}, 次日冲高率={p3:.1f}%, 平均次日高幅={avg:.2f}%')
    print('=' * 60)
    print('【猜想1】好排列 vs 坏排列（DJA之上）')
    print('-' * 60)
    for key in ['DJA之上_好排列', 'DJA之上_坏排列']:
        if key not in stats:
            continue
        cnt, ssum, p3cnt = stats[key]
        p3 = p3cnt / cnt * 100
        avg = ssum / cnt
        print(f'  {key}: n={cnt}, 次日冲高率={p3:.1f}%, 平均次日高幅={avg:.2f}%')
    print('=' * 60)
    print('【猜想1】坏信号（离顶后跌连/跌吞）与下破DJA')
    print('-' * 60)
    for key in ['坏信号_离顶后跌连跌吞', '下破DJA']:
        if key not in stats:
            continue
        cnt, ssum, p3cnt = stats[key]
        p3 = p3cnt / cnt * 100
        avg = ssum / cnt
        print(f'  {key}: n={cnt}, 次日冲高率={p3:.1f}%, 平均次日高幅={avg:.2f}%')

if __name__ == '__main__':
    main()