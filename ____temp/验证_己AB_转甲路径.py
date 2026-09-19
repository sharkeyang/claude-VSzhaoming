# -*- coding: utf-8 -*-
"""
己-A/己-B: 己护型转甲路径验证（直接用DXAB护型变量，无需DJB数据）
========================================
用户澄清: "站上DJB后DXAB转正"、"突破DJB"在己护型语境下等价于"己→甲转正"
（己=DXAB正交前过渡态，转甲=DXAB由负转正），无需DJB均线数据。

己-A: 己护型次日转甲率（=DXAB由负转正），按持续天数细分
己-B: 己护型中，沿DJA升排(柱排首=升) vs 非升排，次日转甲率/延续率

数据: 昭明算展/谕组日/谕组日_*.csv（GBK，7455文件）
权威列映射: 9=DXAB护型, 10=柱排, 26=次日高幅
护型码: r=己, a=甲
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 聚合容器
ji_total = [0, 0, 0]            # 己总数: [n, 次日转甲, 次日冲高]
ji_by_dur = defaultdict(lambda: [0, 0])   # 己-A: 持续天数 -> [n, 次日转甲]
ji_by_zp = defaultdict(lambda: [0, 0])    # 己-B: 柱排首 -> [n, 次日转甲]
ji_by_zp_cg = defaultdict(lambda: [0, 0]) # 己-B: 柱排首 -> [n, 次日冲高]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,26])
    df.columns = ['DXAB','柱排','次日高幅']
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df = df.dropna(subset=['DXAB','次日高幅'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['持续'] = df['DXAB'].str.extract(r'([0-9]+)').astype(float)
    df['次日护型码'] = df['护型码'].shift(-1)
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    df['柱排首'] = df['柱排'].astype(str).str[0]

    ji = df[df['护型码']=='r']
    ji_total[0] += len(ji)
    ji_total[1] += (ji['次日护型码']=='a').sum()
    ji_total[2] += ji['冲高'].sum()

    # 己-A: 按持续天数
    for dur, grp in ji.groupby('持续'):
        ji_by_dur[dur][0] += len(grp)
        ji_by_dur[dur][1] += (grp['次日护型码']=='a').sum()

    # 己-B: 按柱排首
    for zp, grp in ji.groupby('柱排首'):
        ji_by_zp[zp][0] += len(grp)
        ji_by_zp[zp][1] += (grp['次日护型码']=='a').sum()
        ji_by_zp_cg[zp][0] += len(grp)
        ji_by_zp_cg[zp][1] += grp['冲高'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('己护型整体: 次日转甲率（=DXAB由负转正）')
print('='*70)
n, za, cg = ji_total
print(f'己总数: n={n}, 次日转甲率={za/n*100:.2f}%, P≥3%={cg/n*100:.2f}%')

print('\n' + '='*70)
print('己-A: 己护型按持续天数 -> 次日转甲率')
print('='*70)
print(f"{'持续':<6}{'样本':>10}{'次日转甲%':>12}")
rows = []
for dur, (n2, za2) in ji_by_dur.items():
    if n2 >= 100:
        rows.append((dur, n2, za2/n2*100))
rows.sort(key=lambda r: r[0])
for dur, n2, p in rows:
    print(f"{dur:<6}{n2:>10}{p:>12.2f}")

print('\n' + '='*70)
print('己-B: 己护型按柱排首 -> 次日转甲率 / 次日冲高率')
print('='*70)
print(f"{'柱排首':<8}{'样本':>10}{'次日转甲%':>12}{'P≥3%':>10}")
rows = []
for zp, (n2, za2) in ji_by_zp.items():
    if n2 >= 100:
        cg2 = ji_by_zp_cg[zp][1]
        rows.append((zp, n2, za2/n2*100, cg2/n2*100))
rows.sort(key=lambda r: -r[2])
for zp, n2, pza, pcg in rows:
    print(f"{zp!r:<8}{n2:>10}{pza:>12.2f}{pcg:>10.2f}")
