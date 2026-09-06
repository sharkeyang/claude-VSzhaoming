# -*- coding: utf-8 -*-
"""
验证乙的差异 + 主升阶段覆盖
========================================
假设4：乙的差异（再次突破DXZA）
- 没有DXAB由负转正的特权
- 必须形成突破回踩、启动结构

假设5：正交护型是否包含所有主升阶段
- 次日冲高≥3%的样本中，各护型占比

磁盘CSV列序：5=涨幅, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = glob.glob(DATA_DIR + '谕组日_*.csv')
print(f'共 {len(files)} 个文件')

# 聚合1：key=(护型码, 场景) → [n, 次日冲高n]  场景=首次回踩/连阳后首阴/刚正交阴
agg1 = defaultdict(lambda: [0, 0])
# 聚合2：key=护型码 → [n, 次日冲高n]  主升阶段覆盖
agg2 = defaultdict(lambda: [0, 0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,13,14,26])
    df.columns = ['涨幅','DXAB','日ZA','日ZC','次日高幅']
    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df = df.dropna(subset=['DXAB','涨幅','次日高幅'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['持续'] = df['DXAB'].str.extract(r'([0-9]+)').astype(float)
    df['阴阳'] = df['涨幅'].apply(lambda x: '阳' if x > 0 else ('阴' if x < 0 else '平'))
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    # 只看 ZC>0
    df = df[df['日ZC'] > 0]
    if df.empty:
        continue
    # 场景标记
    df['前日ZA'] = df['日ZA'].shift(1)
    df['首次回踩'] = (df['日ZA'] == 1) & (df['前日ZA'] > 1)
    df['前日阴阳'] = df['阴阳'].shift(1)
    df['前二日阴阳'] = df['阴阳'].shift(2)
    df['连阳后首阴'] = (df['阴阳'] == '阴') & (df['前日阴阳'] == '阳') & (df['前二日阴阳'] == '阳')
    df['刚正交阴'] = (df['持续'].between(1, 2)) & (df['阴阳'] == '阴')

    # 聚合1：各护型 × 场景
    for 护型码 in ['a','b','r','y','z','c']:
        sub = df[df['护型码'] == 护型码]
        if sub.empty:
            continue
        for 场景, mask in [('首次回踩', sub['首次回踩']), ('连阳后首阴', sub['连阳后首阴']), ('刚正交阴', sub['刚正交阴'])]:
            s = sub[mask]
            if s.empty:
                continue
            a = agg1[(护型码, 场景)]
            a[0] += len(s)
            a[1] += s['冲高'].sum()
    # 聚合2：主升阶段覆盖（各护型在冲高样本中的占比）
    for 护型码, grp in df.groupby('护型码'):
        a = agg2[护型码]
        a[0] += len(grp)
        a[1] += grp['冲高'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

print('\n=== 各护型 × 场景 次日冲高(≥3%)概率 (ZC>0) ===')
print(f"{'护型':<4}{'场景':<8}{'样本':>10}{'冲高%':>8}")
rows = []
for (护型码, 场景), (n, 冲高n) in agg1.items():
    if n < 100:
        continue
    护型 = 护型映射.get(护型码, 护型码)
    rows.append((护型, 场景, n, 冲高n/n*100))
rows.sort(key=lambda r: (r[0], r[1]))
for 护型, 场景, n, 冲高p in rows:
    print(f"{护型:<4}{场景:<8}{n:>10}{冲高p:>8.2f}")

print('\n=== 主升阶段覆盖：各护型在冲高样本中的占比 (ZC>0) ===')
print(f"{'护型':<4}{'总样本':>10}{'冲高样本':>10}{'冲高%':>8}{'占冲高比%':>10}")
总冲高 = sum(v[1] for v in agg2.values())
rows2 = []
for 护型码, (n, 冲高n) in agg2.items():
    护型 = 护型映射.get(护型码, 护型码)
    rows2.append((护型, n, 冲高n, 冲高n/n*100, 冲高n/总冲高*100))
rows2.sort(key=lambda r: -r[4])
for 护型, n, 冲高n, 冲高p, 占比 in rows2:
    print(f"{护型:<4}{n:>10}{冲高n:>10}{冲高p:>8.2f}{占比:>10.2f}")
