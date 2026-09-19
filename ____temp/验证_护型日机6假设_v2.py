# -*- coding: utf-8 -*-
"""
验证 6 个待验证护型日机假设（2026-09-13，全量数据重跑）
========================================
数据：昭明算展/谕组日/谕组日_*.csv（GBK，7455文件，2026-09-12/13重导）
权威列映射：5=涨幅, 9=DXAB护型, 10=柱排, 13=日ZA, 14=日ZC, 26=次日高幅, 27=柱型, 30=上符串
护型码：a=甲 b=乙 c=丙 z=丁 y=戊 r=己

修正：
  甲-3 前提不成立（甲护型日ZA最小=1永不<0），不跑，直接记录
  甲-4 重新探索好阴柱/坏阴柱特征
  己   修shift跨文件bug（完整df先算次日护型码）
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 聚合容器
jia_priv = defaultdict(lambda: [0, 0, 0])   # 甲-1/2: (持续,阴阳)->[n,次日收阳,次日冲高]
jia_yinzhu = defaultdict(lambda: [0, 0])    # 甲-4: 阴柱类型->[n,次日冲高]
yi_zhuipai = defaultdict(lambda: [0, 0])    # 乙-3: 柱排类型->[n,次日冲高]
yi_youdou = defaultdict(lambda: [0, 0])     # 乙-6: 诱多类型->[n,次日冲高]
yi_abc = defaultdict(lambda: [0, 0])        # 乙-7: 调整深度->[n,次日冲高]
ji_sizhushan = defaultdict(lambda: [0, 0, 0]) # 己: 四柱栅->[n,次日转甲,次日冲高]
baseline = defaultdict(lambda: [0, 0])      # 基线: 护型->[n,次日冲高]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26,27,30])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅','柱型','上符串']
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
    # 次日护型码（文件内shift，最后一行会错位到下一文件，但占比极小可忽略）
    df['次日护型码'] = df['护型码'].shift(-1)
    df['柱排首'] = df['柱排'].astype(str).str[0]
    df['上符末'] = df['上符串'].astype(str).str[-1]

    # 基线
    for hx, grp in df.groupby('护型码'):
        baseline[hx][0] += len(grp)
        baseline[hx][1] += grp['冲高'].sum()

    # ===== 甲-1/2: 甲特权 0<DXAB≤4（限ZC>0）=====
    jia = df[(df['护型码']=='a') & (df['日ZC']>0)]
    jia14 = jia[jia['持续'].between(1, 4)]
    for (持续, 阴阳), grp in jia14.groupby(['持续','阴阳']):
        a = jia_priv[(持续, 阴阳)]
        a[0] += len(grp)
        a[1] += (grp['涨幅'].shift(-1) > 0).sum()
        a[2] += grp['冲高'].sum()

    # ===== 甲-4: 好阴柱/坏阴柱（限ZC>0，甲护型阴柱）=====
    jia_yin = jia[jia['阴阳']=='阴']
    # 按柱排首字符 × 上符末位 交叉
    for (zp, sf), grp in jia_yin.groupby(['柱排首','上符末']):
        jia_yinzhu[(zp, sf)][0] += len(grp)
        jia_yinzhu[(zp, sf)][1] += grp['冲高'].sum()

    # ===== 乙-3: 升排延续 vs 触顶后推顶（乙ZA>0）=====
    yi = df[df['护型码']=='b']
    yi_za0 = yi[yi['日ZA']>0]
    shengpai = yi_za0[yi_za0['柱排首']=='升']
    yi_zhuipai['升排延续'][0] += len(shengpai)
    yi_zhuipai['升排延续'][1] += shengpai['冲高'].sum()
    chuding = yi_za0[yi_za0['上符末']=='A']
    yi_zhuipai['触顶后推顶'][0] += len(chuding)
    yi_zhuipai['触顶后推顶'][1] += chuding['冲高'].sum()
    other = yi_za0[(yi_za0['柱排首']!='升') & (yi_za0['上符末']!='A')]
    yi_zhuipai['其他'][0] += len(other)
    yi_zhuipai['其他'][1] += other['冲高'].sum()

    # ===== 乙-6: 防诱多 =====
    yi_za_lt0 = yi[yi['日ZA']<0]
    youdou1 = yi_za_lt0[yi_za_lt0['柱排首']=='升']
    yi_youdou['DJA之下升孕/连阳'][0] += len(youdou1)
    yi_youdou['DJA之下升孕/连阳'][1] += youdou1['冲高'].sum()
    youdou2 = yi_za0[yi_za0['柱排首']=='跌']
    yi_youdou['DJA之上连跌'][0] += len(youdou2)
    yi_youdou['DJA之上连跌'][1] += youdou2['冲高'].sum()

    # ===== 乙-7: a-b-c浪充分调整（乙ZA<0按深度）=====
    for depth, grp in yi_za_lt0.groupby(pd.cut(yi_za_lt0['日ZA'], bins=[-100,-10,-5,-3,0], labels=['深跌≤-10','中跌-10~-5','浅跌-5~-3','微跌-3~0'])):
        yi_abc[depth][0] += len(grp)
        yi_abc[depth][1] += grp['冲高'].sum()

    # ===== 己: 四柱栅转甲 =====
    ji = df[df['护型码']=='r']
    shanzhu = ji[ji['柱型'].astype(str).str.contains('栅', na=False)]
    ji_sizhushan['四柱栅'][0] += len(shanzhu)
    ji_sizhushan['四柱栅'][1] += (shanzhu['次日护型码']=='a').sum()
    ji_sizhushan['四柱栅'][2] += shanzhu['冲高'].sum()
    feishan = ji[~ji['柱型'].astype(str).str.contains('栅', na=False)]
    ji_sizhushan['非四柱栅'][0] += len(feishan)
    ji_sizhushan['非四柱栅'][1] += (feishan['次日护型码']=='a').sum()
    ji_sizhushan['非四柱栅'][2] += feishan['冲高'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

# ===== 输出 =====
print('\n' + '='*70)
print('基线：各护型整体次日冲高≥3%率')
print('='*70)
for hx in ['a','b','c','z','y','r']:
    n, c = baseline[hx]
    if n > 0:
        print(f'  {hx}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('甲-1/2: 甲特权 0<DXAB≤4（ZC>0，次日收阳率/次日冲高≥3%率）')
print('='*70)
print(f"{'持续':<6}{'阴阳':<4}{'样本':>10}{'次日收阳%':>12}{'次日冲高%':>12}")
rows = []
for (持续, 阴阳), (n, sy, cg) in jia_priv.items():
    if n >= 100:
        rows.append((持续, 阴阳, n, sy/n*100, cg/n*100))
rows.sort(key=lambda r: (r[0], r[1]))
for 持续, 阴阳, n, sy, cg in rows:
    print(f"{持续:<6}{阴阳:<4}{n:>10}{sy:>12.2f}{cg:>12.2f}")

print('\n' + '='*70)
print('甲-4: 好阴柱/坏阴柱（甲护型阴柱+ZC>0，柱排首×上符末，样本≥1000）')
print('='*70)
rows = []
for (zp, sf), (n, c) in jia_yinzhu.items():
    if n >= 1000:
        rows.append((zp, sf, n, c/n*100))
rows.sort(key=lambda r: -r[3])
for zp, sf, n, p in rows:
    print(f'  柱排首={zp!r} 上符末={sf!r}: n={n}, P≥3%={p:.2f}%')

print('\n' + '='*70)
print('乙-3: 升排延续 vs 触顶后推顶（乙ZA>0）')
print('='*70)
for k, (n, c) in yi_zhuipai.items():
    if n > 0:
        print(f'  {k}: n={n}, P≥3%={c/n*100:.2f}%')

print('\n' + '='*70)
print('乙-6: 防诱多')
print('='*70)
for k, (n, c) in yi_youdou.items():
    if n > 0:
        print(f'  {k}: n={n}, P≥3%={c/n*100:.2f}%')

print('\n' + '='*70)
print('乙-7: a-b-c浪充分调整（乙ZA<0按深度）')
print('='*70)
for k, (n, c) in yi_abc.items():
    if n > 0:
        print(f'  {k}: n={n}, P≥3%={c/n*100:.2f}%')

print('\n' + '='*70)
print('己: 四柱栅转甲（次日转甲率/次日冲高≥3%率）')
print('='*70)
for k, (n, za, cg) in ji_sizhushan.items():
    if n > 0:
        print(f'  {k}: n={n}, 次日转甲率={za/n*100:.2f}%, P≥3%={cg/n*100:.2f}%')
