# -*- coding: utf-8 -*-
"""
任务1+任务2：周波型对下周冲高3%的指示作用 + 是否结合周等型
数据源：昭明算展/谕组导出/谕组周/谕组周_<代码>.csv (GBK, 63列)
"""
import os, glob, re, sys
from collections import defaultdict, Counter

BASE = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组导出\谕组周'
OUT = r'D:\@VSwork\VS昭明计划VBA优化\____temp\_任务12_结果.txt'

# 列索引
COL_HR = 3      # 本周最高幅
COL_WAVE = 7    # 波型
COL_DENG = 6    # 等周

# 波型主体：split('.')[0] 后取尾部中文部分（含〇）
def wave_body(w):
    if not w:
        return ''
    base = w.split('.')[0]
    m = re.search(r'[\u4e00-\u9fff〇]+$', base)
    return m.group(0) if m else base

def read_all():
    """批量读取所有CSV，返回每行 (hr, wave_body, deng)。只保留有下一行的行。"""
    files = glob.glob(os.path.join(BASE, '*.csv'))
    rows = []  # (hr_this, hr_next, wave_body, deng)
    for f in files:
        try:
            with open(f, encoding='gbk') as fh:
                fh.readline()  # header
                prev = None  # (hr, wave_body, deng)
                for line in fh:
                    parts = line.rstrip().split(',')
                    if len(parts) <= COL_WAVE:
                        continue
                    try:
                        hr = float(parts[COL_HR])
                    except ValueError:
                        hr = None
                    wb = wave_body(parts[COL_WAVE])
                    deng = parts[COL_DENG]
                    if prev is not None and prev[0] is not None and hr is not None:
                        rows.append((prev[0], hr, prev[1], prev[2]))
                    prev = (hr, wb, deng)
        except Exception as e:
            print('skip', os.path.basename(f), e)
    return rows

def main():
    rows = read_all()
    total = len(rows)
    hit = sum(1 for r in rows if r[1] >= 3)
    baseline = hit / total if total else 0
    print(f'总样本(有下周): {total}, 下周冲高3%: {hit}, 基线冲高率: {baseline:.4f} ({baseline*100:.2f}%)')

    lines = []
    lines.append(f'总样本(有下周): {total}, 下周冲高3%: {hit}, 基线冲高率: {baseline*100:.2f}%')
    lines.append('')

    # ============ 任务1：按波型主体分组 ============
    lines.append('='*70)
    lines.append('任务1：周波型主体对下周冲高3%的指示作用')
    lines.append('='*70)
    grp = defaultdict(lambda: [0, 0])  # wave_body -> [n, hit]
    for hr_this, hr_next, wb, deng in rows:
        grp[wb][0] += 1
        if hr_next >= 3:
            grp[wb][1] += 1
    # 只保留样本>=100的波型
    items = [(wb, n, h) for wb, (n, h) in grp.items() if n >= 100]
    items.sort(key=lambda x: -x[2]/x[1])
    lines.append(f'{"波型主体":<10}{"样本数":>8}{"冲高数":>8}{"冲高率":>10}{"vs基线":>10}{"标注":>6}')
    lines.append('-'*60)
    for wb, n, h in items:
        rate = h / n
        diff = (rate - baseline) * 100
        mark = ''
        if diff > 3:
            mark = '↑↑'
        elif diff < -3:
            mark = '↓↓'
        elif n < 1000:
            mark = '小样本'
        lines.append(f'{wb:<10}{n:>8}{h:>8}{rate*100:>9.2f}%{diff:>+9.2f}pp{mark:>6}')
    lines.append('')
    # 显著高于/低于基线
    hi = [(wb, n, h) for wb, n, h in items if h/n - baseline > 0.03]
    lo = [(wb, n, h) for wb, n, h in items if baseline - h/n > 0.03]
    lines.append(f'显著高于基线(+3pp)的波型({len(hi)}个):')
    for wb, n, h in sorted(hi, key=lambda x: -x[2]/x[1]):
        lines.append(f'  {wb:<10} n={n:<7} 冲高率={h/n*100:.2f}%')
    lines.append(f'显著低于基线(-3pp)的波型({len(lo)}个):')
    for wb, n, h in sorted(lo, key=lambda x: x[2]/x[1]):
        lines.append(f'  {wb:<10} n={n:<7} 冲高率={h/n*100:.2f}%')
    lines.append('')
    # 区分度
    if items:
        best = items[0]
        worst = items[-1]
        lines.append(f'波型单独区分度(最强-最弱): {best[2]/best[1]*100:.2f}% - {worst[2]/worst[1]*100:.2f}% = {(best[2]/best[1]-worst[2]/worst[1])*100:.2f}pp')
        lines.append(f'  最强: {best[0]} ({best[2]/best[1]*100:.2f}%), 最弱: {worst[0]} ({worst[2]/worst[1]*100:.2f}%)')
    lines.append('')

    # ============ 任务2：波型主体 × 等周 交叉 ============
    lines.append('='*70)
    lines.append('任务2：波型主体 × 等周 交叉表')
    lines.append('='*70)
    cross = defaultdict(lambda: [0, 0])  # (wb, deng) -> [n, hit]
    for hr_this, hr_next, wb, deng in rows:
        cross[(wb, deng)][0] += 1
        if hr_next >= 3:
            cross[(wb, deng)][1] += 1
    # 对每个波型主体，看等周细分
    lines.append('对每个波型主体(样本>=500)，按等周细分冲高率:')
    lines.append(f'{"波型主体":<10}{"等周":<6}{"样本":>7}{"冲高率":>9}{"vs波型整体":>12}')
    lines.append('-'*50)
    for wb, n, h in items:
        if n < 500:
            continue
        wb_rate = h / n
        deng_items = [(d, cn, ch) for (w, d), (cn, ch) in cross.items() if w == wb and cn >= 100]
        deng_items.sort(key=lambda x: -x[2]/x[1])
        for d, cn, ch in deng_items:
            drate = ch / cn
            ddiff = (drate - wb_rate) * 100
            lines.append(f'{wb:<10}{d:<6}{cn:>7}{drate*100:>8.2f}%{ddiff:>+11.2f}pp')
        lines.append('')
    lines.append('')
    # 等周整体区分度
    deng_grp = defaultdict(lambda: [0, 0])
    for hr_this, hr_next, wb, deng in rows:
        deng_grp[deng][0] += 1
        if hr_next >= 3:
            deng_grp[deng][1] += 1
    deng_items = [(d, n, h) for d, (n, h) in deng_grp.items() if n >= 100]
    deng_items.sort(key=lambda x: -x[2]/x[1])
    lines.append('等周单独区分度:')
    for d, n, h in deng_items:
        lines.append(f'  {d:<6} n={n:<7} 冲高率={h/n*100:.2f}%')
    if deng_items:
        lines.append(f'  等周区分度(最强-最弱): {(deng_items[0][2]/deng_items[0][1]-deng_items[-1][2]/deng_items[-1][1])*100:.2f}pp')
    lines.append('')

    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print('结果已写入', OUT)

if __name__ == '__main__':
    main()