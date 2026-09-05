# -*- coding: utf-8 -*-
"""重新跑 MC3.3.3 所有核心数据（高波池全量）"""
import csv, os, sys
from collections import defaultdict

# 列位置（由 VBA 写入代码确定，非表头）
COL = {
    'DXCD': 8, 'DXAB': 9, '日ZA': 13, '日ZC': 14, '日ZE': 15,
    'BSHA': 19, '次日高幅': 26, '柱型': 27, '层界': 28,
    'BT鼎': 40, 'BTZA': 41, 'BT连阳': 42, '顶型': 43, '日等型': 44,
    '仓日类': 45, '日层赢': 47, '合顶哼': 56,
}

# 护型首字符映射
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

# 市板映射
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) >= 2:
            pool[row[0]] = row[1]
high_codes = set(k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit'))

DATA_DIR = '昭明算展/谕组日'

def safe_float(v):
    try:
        return float(v)
    except:
        return None

def safe_int(v):
    try:
        return int(float(v))
    except:
        return None

# 聚合容器
# 位置基准: (等型, ZC符号, 护型) -> [n, h2_cnt, h3_cnt, sum_high]
pos_base = defaultdict(lambda: [0, 0, 0, 0.0])
# BSHA5 增强: (等型, ZC符号, 护型) -> [n, h2_cnt]
pos_bsha5 = defaultdict(lambda: [0, 0])
# 全量
total = [0, 0, 0, 0.0]  # n, h2, h3, sum_high
# 条件边际: 各条件单独
cond = defaultdict(lambda: [0, 0])  # 条件 -> [n, h2]
# 柱型
zhuxing = defaultdict(lambda: [0, 0, 0, 0.0, 0])  # 柱型 -> [n, h2, h3, sum_high, 下柱>0]
# 触顶 (上符串含v) - 需要上符串列[30]
# 前一柱护型 - 需要逐行处理

# 等高线单独 (等型 -> [n, h2])
etc_alone = defaultdict(lambda: [0, 0])

files = sorted(os.listdir(DATA_DIR))
high_files = [f for f in files if f.endswith('.csv') and f.replace('谕组日_','').replace('.csv','') in high_codes]
print(f'高波池文件数: {len(high_files)}', flush=True)

processed = 0
for fname in high_files:
    fpath = os.path.join(DATA_DIR, fname)
    try:
        with open(fpath, encoding='gbk') as f:
            reader = csv.reader(f)
            header = next(reader)
            prev_hx = None  # 前一柱护型
            for row in reader:
                if len(row) <= 56:
                    continue
                etc = row[COL['日等型']].strip()
                if not etc or not etc.startswith('等'):
                    continue
                dxab = row[COL['DXAB']].strip()
                if not dxab:
                    continue
                hx = HX_MAP.get(dxab[0], '?')
                zc = safe_int(row[COL['日ZC']])
                if zc is None:
                    continue
                zc_sym = 'ZC>0' if zc > 0 else 'ZC<0'
                bsha = safe_float(row[COL['BSHA']])
                nxt = safe_float(row[COL['次日高幅']])
                if nxt is None:
                    continue
                h2 = 1 if nxt >= 2 else 0
                h3 = 1 if nxt >= 3 else 0
                # 位置基准
                key = (etc, zc_sym, hx)
                pos_base[key][0] += 1
                pos_base[key][1] += h2
                pos_base[key][2] += h3
                pos_base[key][3] += nxt
                # 全量
                total[0] += 1
                total[1] += h2
                total[2] += h3
                total[3] += nxt
                # 等高线单独
                etc_alone[etc][0] += 1
                etc_alone[etc][1] += h2
                # BSHA5
                if bsha is not None and bsha > 5:
                    pos_bsha5[key][0] += 1
                    pos_bsha5[key][1] += h2
                # 条件边际
                if bsha is not None and bsha > 5:
                    cond['BSHA5'][0] += 1; cond['BSHA5'][1] += h2
                if bsha is not None and bsha > 3:
                    cond['BSHA3'][0] += 1; cond['BSHA3'][1] += h2
                if safe_int(row[COL['BT连阳']]) and safe_int(row[COL['BT连阳']]) > 0:
                    cond['连阳'][0] += 1; cond['连阳'][1] += h2
                if safe_int(row[COL['BT鼎']]) and safe_int(row[COL['BT鼎']]) > 0:
                    cond['BT鼎'][0] += 1; cond['BT鼎'][1] += h2
                if zc > 0:
                    cond['ZC>0'][0] += 1; cond['ZC>0'][1] += h2
                if hx in ('甲', '乙', '己'):
                    cond['甲乙己'][0] += 1; cond['甲乙己'][1] += h2
                # 柱型
                zx = row[COL['柱型']].strip()
                if zx:
                    zhuxing[zx][0] += 1
                    zhuxing[zx][1] += h2
                    zhuxing[zx][2] += h3
                    zhuxing[zx][3] += nxt
                    if nxt > 0:
                        zhuxing[zx][4] += 1
    except Exception as e:
        print(f'错误 {fname}: {e}', flush=True)
    processed += 1
    if processed % 500 == 0:
        print(f'已处理 {processed}/{len(high_files)}', flush=True)

# 输出结果
out = []
out.append('=== 全量基准 ===')
out.append(f'总样本: {total[0]}, H2={total[1]/total[0]*100:.1f}%, H3={total[2]/total[0]*100:.1f}%, 均冲高={total[3]/total[0]:.2f}%')
out.append('')
out.append('=== 等高线单独 (等型 -> H2) ===')
for etc in ['等1','等2','等3','等5','等6','等7']:
    if etc in etc_alone:
        n, h2 = etc_alone[etc]
        out.append(f'{etc}: n={n}, H2={h2/n*100:.1f}%')
out.append('')
out.append('=== 位置基准 H2 (等型 × ZC × 护型) ===')
for etc in ['等1','等2','等3','等5','等6','等7']:
    out.append(f'--- {etc} ---')
    for zc_sym in ['ZC>0','ZC<0']:
        row_str = f'{zc_sym}: '
        for hx in ['甲','乙','丙','丁','戊','己']:
            key = (etc, zc_sym, hx)
            if key in pos_base:
                n, h2, h3, s = pos_base[key]
                row_str += f'{hx}={h2/n*100:.1f}%(n={n}) '
        out.append(row_str)
out.append('')
out.append('=== BSHA5 增强 (等型 × ZC × 护型) ===')
for etc in ['等1','等2','等3','等5','等6','等7']:
    out.append(f'--- {etc} ---')
    for zc_sym in ['ZC>0','ZC<0']:
        row_str = f'{zc_sym}: '
        for hx in ['甲','乙','丙','丁','戊','己']:
            key = (etc, zc_sym, hx)
            if key in pos_bsha5:
                n, h2 = pos_bsha5[key]
                row_str += f'{hx}={h2/n*100:.1f}%(n={n}) '
        out.append(row_str)
out.append('')
out.append('=== 条件边际贡献 ===')
for c in ['BSHA5','BSHA3','连阳','BT鼎','ZC>0','甲乙己']:
    if c in cond:
        n, h2 = cond[c]
        out.append(f'{c}: n={n}, H2={h2/n*100:.1f}%')
out.append('')
out.append('=== 柱型单独 ===')
for zx, v in sorted(zhuxing.items(), key=lambda x: -x[1][1]/x[1][0] if x[1][0] else 0):
    n, h2, h3, s, dn = v
    out.append(f'{zx}: n={n}, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%, 均冲高={s/n:.2f}%, 下柱>0={dn/n*100:.1f}%')

with open('____temp/mc333_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('完成，结果写入 ____temp/mc333_results.txt')
