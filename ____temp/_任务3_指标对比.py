# -*- coding: utf-8 -*-
"""
任务3：各种周类指标对预测下周冲高3%的有效性对比
数据源：昭明算展/谕组导出/谕组周/谕组周_<代码>.csv (GBK, 63列)
"""
import os, glob, re
from collections import defaultdict

BASE = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组周'
OUT = r'D:\@VSwork\VS昭明计划VBA优化\____temp\_任务3_结果.txt'

COL_HR = 3

# 指标定义: (名称, 列索引, 类型)  类型: 'str'=按取值分组, 'num'=按>0/<0/分段
INDICATORS = [
    ('波型主体', 7, 'wave'),
    ('等周', 6, 'str'),
    ('护型', 4, 'str'),
    ('地型周', 5, 'str'),
    ('柱排周', 8, 'str'),
    ('周势型', 12, 'str'),
    ('ZA周', 16, 'num'),
    ('ZC周', 18, 'num'),
    ('AB周', 22, 'num'),
    ('CD周', 27, 'num'),
    ('顶周', 35, 'num'),
    ('合顶周', 37, 'num'),
    ('极折周', 38, 'str'),
    ('顶态周', 39, 'str'),
    ('顶型周', 40, 'str'),
    ('顶触周', 41, 'str'),
    ('BT鼎周', 49, 'str'),
    ('并符串周', 51, 'str'),
    ('层类周', 52, 'str'),
    ('四域', 53, 'str'),
    ('周策略P3', 54, 'str'),
    ('周策分P3', 55, 'str'),
    ('周策略P1', 56, 'str'),
    ('周策分P1', 57, 'str'),
    ('周策略ZA', 58, 'str'),
    ('周策分ZA', 59, 'str'),
    ('周策分坏', 60, 'str'),
    ('周策分好', 61, 'str'),
]

def wave_body(w):
    if not w:
        return ''
    base = w.split('.')[0]
    m = re.search(r'[\u4e00-\u9fff〇]+$', base)
    return m.group(0) if m else base

def num_bucket(v):
    """数值型指标分段：>0 / =0 / <0"""
    try:
        f = float(v)
    except (ValueError, TypeError):
        return '空'
    if f > 0:
        return '>0'
    elif f < 0:
        return '<0'
    else:
        return '=0'

def read_all():
    files = glob.glob(os.path.join(BASE, '*.csv'))
    # 每行: (hr_next, [各指标取值])
    rows = []
    for f in files:
        try:
            with open(f, encoding='gbk') as fh:
                fh.readline()
                prev = None  # list of values
                for line in fh:
                    parts = line.rstrip().split(',')
                    if len(parts) <= 61:
                        continue
                    try:
                        hr = float(parts[COL_HR])
                    except ValueError:
                        hr = None
                    vals = []
                    for name, col, typ in INDICATORS:
                        raw = parts[col] if col < len(parts) else ''
                        if typ == 'wave':
                            vals.append(wave_body(raw))
                        elif typ == 'num':
                            vals.append(num_bucket(raw))
                        else:
                            vals.append(raw)
                    if prev is not None and prev[0] is not None and hr is not None:
                        rows.append((hr, prev[1]))
                    prev = (hr, vals)
        except Exception as e:
            print('skip', os.path.basename(f), e)
    return rows

def main():
    rows = read_all()
    total = len(rows)
    hit = sum(1 for r in rows if r[0] >= 3)
    baseline = hit / total
    print(f'总样本: {total}, 基线冲高率: {baseline*100:.2f}%')

    lines = []
    lines.append(f'总样本: {total}, 基线冲高率: {baseline*100:.2f}%')
    lines.append('')

    results = []  # (name, 区分度pp, 最强组, 最弱组, 组详情)
    for idx, (name, col, typ) in enumerate(INDICATORS):
        grp = defaultdict(lambda: [0, 0])
        for hr_next, vals in rows:
            v = vals[idx]
            grp[v][0] += 1
            if hr_next >= 3:
                grp[v][1] += 1
        # 只保留样本>=1000的组
        items = [(v, n, h) for v, (n, h) in grp.items() if n >= 1000]
        if len(items) < 2:
            lines.append(f'--- {name}: 有效组不足(<2组样本>=1000), 跳过')
            lines.append('')
            continue
        items.sort(key=lambda x: -x[2]/x[1])
        best = items[0]
        worst = items[-1]
        diff = (best[2]/best[1] - worst[2]/worst[1]) * 100
        results.append((name, diff, best, worst, items))

    # 按区分度排序
    results.sort(key=lambda x: -x[1])
    lines.append('='*80)
    lines.append('任务3：各周类指标区分度排序（区分度 = 最强组冲高率 - 最弱组冲高率）')
    lines.append('='*80)
    lines.append(f'{"排名":<4}{"指标":<12}{"区分度":>8}{"最强组":>16}{"最强率":>9}{"最弱组":>16}{"最弱率":>9}')
    lines.append('-'*80)
    for rank, (name, diff, best, worst, items) in enumerate(results, 1):
        lines.append(f'{rank:<4}{name:<12}{diff:>7.2f}pp{best[0]:>16}{best[2]/best[1]*100:>8.2f}%{worst[0]:>16}{worst[2]/worst[1]*100:>8.2f}%')
    lines.append('')

    # 详细表
    lines.append('='*80)
    lines.append('各指标详细分组表（样本>=1000的组）')
    lines.append('='*80)
    for rank, (name, diff, best, worst, items) in enumerate(results, 1):
        lines.append(f'')
        lines.append(f'### {rank}. {name} (区分度 {diff:.2f}pp)')
        lines.append(f'{"取值":<16}{"样本":>9}{"冲高率":>10}{"vs基线":>10}')
        lines.append('-'*50)
        for v, n, h in items:
            rate = h/n
            d = (rate - baseline) * 100
            mark = '小样本' if n < 1000 else ''
            lines.append(f'{v:<16}{n:>9}{rate*100:>9.2f}%{d:>+9.2f}pp{mark:>6}')
    lines.append('')

    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print('结果已写入', OUT)

if __name__ == '__main__':
    main()