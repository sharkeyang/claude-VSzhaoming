#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
课题（用户猜想，2026-10-11）：研究周范围（WXZC>0 且 WXAB 甲乙己）与周合顶、周触顶的关系。
用户观察图形：周主升过程中有大量不断推高顶的触顶，也存在少量离顶。

数据来源：谕组周 CSV（昭明算展/谕组导出/谕组周），GBK 编码，60 列
列索引（以实际表头为准）：
    [0] 主期  [1] 周涨  [4] 护型(WXAB)  [15] ZC周(WXZC)
    [32] 顶周(BT顶)  [34] 合顶周(BT合顶)  [35] 极折周  [36] 顶态周  [37] 顶型周  [38] 顶触周

关键语义：
    BT顶[32] = 当前价 vs 结顶(历史最高) 交叉天数。>0=触顶(在顶上方)，<=0=离顶。
    BT合顶[34] = 结哼(近期高点) vs 结顶(历史最高) 交叉天数。>0=合顶(近期高点创新高)，<=0=离顶。
    顶态[36] = G(顶哼合并/触顶) / K(顶哼分离) / L(未创新高已下跌)。
"""
import csv, os, sys, io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA = '昭明算展/谕组导出/谕组周'
HX = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_rows(fname):
    """读取单个CSV，返回行列表（含表头）。"""
    with open(os.path.join(DATA, fname), encoding='gbk') as fh:
        r = csv.reader(fh)
        return list(r)


def main():
    files = [f for f in os.listdir(DATA) if f.startswith('谕组周_') and f.endswith('.csv')]
    print(f'文件数: {len(files)}')

    # 统计结构
    # stat[状态][指标] = 计数
    stat = defaultdict(lambda: defaultdict(int))
    n_main = 0

    for fi, fname in enumerate(files):
        if fi % 1000 == 0:
            print(f'  [处理] {fi}/{len(files)}...')
        rows = load_rows(fname)
        for i, row in enumerate(rows):
            if i == 0:
                continue  # 跳过表头
            if len(row) < 39:
                continue
            try:
                zc = int(row[15])
            except (ValueError, IndexError):
                continue
            hx = HX.get(row[4][0], '?')
            if not (zc > 0 and hx in ('甲', '乙', '己')):
                continue
            n_main += 1
            try:
                bt_top = int(row[32])
                bt_he = int(row[34])
            except (ValueError, IndexError):
                continue
            top_state = '触顶' if bt_top > 0 else '离顶'
            he_state = '合顶' if bt_he > 0 else '离顶'

            # 下周走势
            if i + 1 < len(rows):
                nxt = rows[i + 1]
                if len(nxt) < 39:
                    continue
                try:
                    nxt_zc = int(nxt[15])
                    nxt_zhang = float(nxt[1])
                except (ValueError, IndexError):
                    continue
                nxt_hx = HX.get(nxt[4][0], '?')
                nxt_main = nxt_zc > 0 and nxt_hx in ('甲', '乙', '己')
                nxt_bad = nxt_zc < 0
                nxt_up = nxt_zhang > 0
                for st in (top_state, he_state, top_state + '/' + he_state):
                    stat[st]['下周涨'] += int(nxt_up)
                    stat[st]['下周主升'] += int(nxt_main)
                    stat[st]['下周转坏'] += int(nxt_bad)
                    stat[st]['n'] += 1

    print(f'\n周主升(WXZC>0+甲乙己)行数: {n_main}')
    print()
    print('=== 按BT顶状态: 触顶 vs 离顶 ===')
    for st in ('触顶', '离顶'):
        d = stat[st]
        n = d['n']
        if n == 0:
            continue
        print(f'  {st}: n={n} | 下周涨 {d["下周涨"]/n*100:.1f}% | '
              f'下周主升 {d["下周主升"]/n*100:.1f}% | 下周转坏 {d["下周转坏"]/n*100:.1f}%')
    print()
    print('=== 按BT合顶状态: 合顶 vs 离顶 ===')
    for st in ('合顶', '离顶'):
        d = stat[st]
        n = d['n']
        if n == 0:
            continue
        print(f'  {st}: n={n} | 下周涨 {d["下周涨"]/n*100:.1f}% | '
              f'下周主升 {d["下周主升"]/n*100:.1f}% | 下周转坏 {d["下周转坏"]/n*100:.1f}%')
    print()
    print('=== 按BT顶×BT合顶交叉: 触顶/合顶 vs 触顶/离顶 vs 离顶/合顶 vs 离顶/离顶 ===')
    for st in ('触顶/合顶', '触顶/离顶', '离顶/合顶', '离顶/离顶'):
        d = stat[st]
        n = d['n']
        if n == 0:
            continue
        print(f'  {st}: n={n} | 下周涨 {d["下周涨"]/n*100:.1f}% | '
              f'下周主升 {d["下周主升"]/n*100:.1f}% | 下周转坏 {d["下周转坏"]/n*100:.1f}%')


if __name__ == '__main__':
    main()
