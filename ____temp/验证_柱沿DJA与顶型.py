# -*- coding: utf-8 -*-
"""
验证用户猜想（2026-11-14）：
  猜想1：柱沿DJA排列——好排列（升连Q/升吞O/跌孕v/升运）vs 坏排列（跌吞V/跌连W）
  猜想2：顶型识别主升与震荡——龙a触顶/龙b/虎/离顶

数据：昭明算展/谕组日/谕组日_*.csv（GBK，135列）
列索引：0=日期, 5=涨幅, 10=柱排, 16=日ZA, 17=日ZC, 18=日ZE, 28=次日高幅, 36=并符串, 44=顶型, 68=DTZB, 70=DTAB
并符串编码：Q=升连, O=升吞, o=升孕, W=跌连, V=跌吞, v=跌孕
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

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    # 聚合统计：key -> [count, sum_hr, count_p3]
    zhu = {}   # 柱型
    ding = {}  # 顶型
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
            # 柱型：并符串最后一个字符
            bf = row[36].strip()
            if bf:
                last = bf[-1]
                s = zhu.setdefault(last, [0, 0.0, 0])
                s[0] += 1
                s[1] += hr
                if hr >= 3:
                    s[2] += 1
            # 顶型：取类型字母
            dx = row[44].strip()
            if dx:
                t = dx[0]
                s = ding.setdefault(t, [0, 0.0, 0])
                s[0] += 1
                s[1] += hr
                if hr >= 3:
                    s[2] += 1
        if n % 1000 == 0:
            print(f'  已处理 {n} 个文件...', flush=True)
    print(f'有效文件数: {n}', flush=True)
    print('=' * 60)
    print('【猜想1】柱型（并符串末字符）的次日冲高率（次日高幅≥3%）')
    print('-' * 60)
    names = {'Q': '升连', 'O': '升吞', 'o': '升孕', 'W': '跌连', 'V': '跌吞', 'v': '跌孕'}
    for code in ['Q', 'O', 'o', 'V', 'W', 'v']:
        if code not in zhu:
            continue
        cnt, ssum, p3cnt = zhu[code]
        p3 = p3cnt / cnt * 100
        avg = ssum / cnt
        print(f'  {names.get(code, code)}[{code}]: n={cnt}, 次日冲高率={p3:.1f}%, 平均次日高幅={avg:.2f}%')
    print('=' * 60)
    print('【猜想2】顶型的次日冲高率（次日高幅≥3%）')
    print('-' * 60)
    dnames = {'a': '龙a(触顶)', 'b': '龙b(近顶)', 'c': '雀', 'd': '虎', 'e': '非', 'f': '武'}
    for code in ['a', 'b', 'c', 'd', 'e', 'f']:
        if code not in ding:
            continue
        cnt, ssum, p3cnt = ding[code]
        p3 = p3cnt / cnt * 100
        avg = ssum / cnt
        print(f'  {dnames.get(code, code)}[{code}]: n={cnt}, 次日冲高率={p3:.1f}%, 平均次日高幅={avg:.2f}%')

if __name__ == '__main__':
    main()