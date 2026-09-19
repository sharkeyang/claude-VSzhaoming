# -*- coding: utf-8 -*-
"""纠正转跌信号验证：用码点精确判断柱排类型，统计三种阴阳阴组合
组合1: 跌吞+升孕+跌吞 (代表向下)
组合2: 跌孕+升孕+跌吞 (代表顶部转向下)
组合3: 跌孕+升吞+跌孕 (代表向上)
"""
import csv, io, os
from collections import Counter

COL_ZC = 14
COL_ZP = 10
COL_GF = 6

# 码点
DIE = 0x4e0b  # 跌
SHENG = 0x5347  # 升
REN = 0x4eba  # 人
LIAN = 0x8dcc  # 连
TUN = 0x541e  # 吞
YUN = 0x5b55  # 孕
FAN = 0x53cd  # 反

def classify(zp):
    """解析柱排，返回 (首柱, 尾柱)"""
    if zp.startswith('('):
        head = zp[1:2]
        body = zp[3:]
    else:
        head = zp[0:1]
        body = zp[1:]
    # 尾柱判断：吞/孕/连/反
    if TUN in [ord(c) for c in body]:
        tail = '吞'
    elif YUN in [ord(c) for c in body]:
        tail = '孕'
    elif LIAN in [ord(c) for c in body]:
        tail = '连'
    elif FAN in [ord(c) for c in body]:
        tail = '反'
    else:
        tail = '其他'
    # 首柱
    hc = ord(head)
    if hc == DIE: head_c = '跌'
    elif hc == SHENG: head_c = '升'
    elif hc == REN: head_c = '人'
    elif hc == LIAN: head_c = '连'
    else: head_c = '其他'
    return head_c, tail

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计三种组合
stats = {
    '跌吞+升孕+跌吞': [0, 0, 0.0],
    '跌孕+升孕+跌吞': [0, 0, 0.0],
    '跌孕+升吞+跌孕': [0, 0, 0.0],
}
# 单柱柱排类型统计
single = Counter()

for fi, fname in enumerate(files):
    path = os.path.join('昭明算展/谕组日', fname)
    try:
        with io.open(path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader)
            rows = []
            for row in reader:
                if len(row) <= COL_GF:
                    continue
                try:
                    zc = float(row[COL_ZC])
                except (ValueError, IndexError):
                    continue
                rows.append((zc, row[COL_ZP], row[COL_GF]))
            # 单柱统计
            for zc, zp, _ in rows:
                h, t = classify(zp)
                single[f'{h}{t}'] += 1
            # 三柱组合
            for i in range(len(rows) - 3):
                zc0, zp0, _ = rows[i]
                if zc0 <= 0:
                    continue
                h0, t0 = classify(zp0)
                h1, t1 = classify(zp1) if False else classify(rows[i+1][1])
                h2, t2 = classify(rows[i+2][1])
                if h0=='跌' and t0=='吞' and h1=='升' and t1=='孕' and h2=='跌' and t2=='吞':
                    key = '跌吞+升孕+跌吞'
                elif h0=='跌' and t0=='孕' and h1=='升' and t1=='孕' and h2=='跌' and t2=='吞':
                    key = '跌孕+升孕+跌吞'
                elif h0=='跌' and t0=='孕' and h1=='升' and t1=='吞' and h2=='跌' and t2=='孕':
                    key = '跌孕+升吞+跌孕'
                else:
                    continue
                try:
                    nh = float(rows[i+3][2])
                except (ValueError, TypeError):
                    continue
                stats[key][0] += 1
                if nh >= 3:
                    stats[key][1] += 1
                stats[key][2] += nh
    except Exception:
        pass
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件')

print('\n=== 单柱柱排类型分布 ===')
for k, v in single.most_common(15):
    print(f'  {k}: {v}')

print('\n=== 三种阴阳阴组合的次日表现（DXZC>0起始） ===')
print(f'{"组合":<20}{"样本":<12}{"次日冲高≥3%":<12}{"冲高率":<10}{"次日均高幅":<10}')
for key in ['跌吞+升孕+跌吞', '跌孕+升孕+跌吞', '跌孕+升吞+跌孕']:
    t, g, s = stats[key]
    if t:
        print(f'{key:<20}{t:<12}{g:<12}{g/t*100:<10.1f}{s/t:<10.2f}')
    else:
        print(f'{key:<20} 无样本')