# -*- coding: utf-8 -*-
"""验证转跌信号：三种阴阳阴三柱组合的次日表现
组合1: 跌吞+升孕+跌吞 (代表向下)
组合2: 跌孕+升孕+跌吞 (代表顶部转向下)
组合3: 跌孕+升吞+跌孕 (代表向上)
"""
import csv, io, os
from collections import Counter

COL_ZC = 14
COL_ZP = 10
COL_GAOFU = 6

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

def classify(zp):
    """解析柱排，返回 (首柱, 尾柱)"""
    if zp.startswith('('):
        head = zp[1:2]
        body = zp[3:]
    else:
        head = zp[0:1]
        body = zp[1:]
    # 尾柱判断
    if '吞' in body:
        tail = '吞'
    elif '孕' in body:
        tail = '孕'
    elif '连' in body:
        tail = '连'
    else:
        tail = '其他'
    return head, tail

# 统计三种组合的次日表现
# 组合 -> [总数, 次日冲高≥3%, 次日涨幅均值]
stats = {
    '跌吞+升孕+跌吞': [0, 0, 0.0],
    '跌孕+升孕+跌吞': [0, 0, 0.0],
    '跌孕+升吞+跌孕': [0, 0, 0.0],
}

for fi, fname in enumerate(files):
    path = os.path.join('昭明算展/谕组日', fname)
    try:
        with io.open(path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader)
            rows = []
            for row in reader:
                if len(row) <= COL_GAOFU:
                    continue
                try:
                    zc = float(row[COL_ZC])
                except (ValueError, IndexError):
                    continue
                rows.append((zc, row[COL_ZP], row[COL_GAOFU]))
            # 遍历连续三天
            for i in range(len(rows) - 3):
                zc0, zp0, _ = rows[i]
                zc1, zp1, _ = rows[i+1]
                zc2, zp2, _ = rows[i+2]
                # 只统计 DXZC>0 的起始柱
                if zc0 <= 0:
                    continue
                h0, t0 = classify(zp0)
                h1, t1 = classify(zp1)
                h2, t2 = classify(zp2)
                # 组合1: 跌吞+升孕+跌吞
                if h0=='跌' and t0=='吞' and h1=='升' and t1=='孕' and h2=='跌' and t2=='吞':
                    key = '跌吞+升孕+跌吞'
                # 组合2: 跌孕+升孕+跌吞
                elif h0=='跌' and t0=='孕' and h1=='升' and t1=='孕' and h2=='跌' and t2=='吞':
                    key = '跌孕+升孕+跌吞'
                # 组合3: 跌孕+升吞+跌孕
                elif h0=='跌' and t0=='孕' and h1=='升' and t1=='吞' and h2=='跌' and t2=='孕':
                    key = '跌孕+升吞+跌孕'
                else:
                    continue
                # 次日表现（第4天）
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
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print('\n=== 三种阴阳阴组合的次日表现（DXZC>0起始） ===')
print(f'{"组合":<20}{"样本":<12}{"次日冲高≥3%":<12}{"冲高率":<10}{"次日均高幅":<10}')
for key in ['跌吞+升孕+跌吞', '跌孕+升孕+跌吞', '跌孕+升吞+跌孕']:
    t, g, s = stats[key]
    if t:
        print(f'{key:<20}{t:<12}{g:<12}{g/t*100:<10.1f}{s/t:<10.2f}')
    else:
        print(f'{key:<20} 无样本')