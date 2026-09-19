# -*- coding: utf-8 -*-
"""
验证 6 个待验证护型日机假设（2026-09-13）
========================================
数据：昭明算展/谕组日/谕组日_*.csv（GBK编码，7455文件）
权威列映射（csv-column-mapping-vba）：
  5=涨幅, 9=DXAB护型, 10=柱排, 13=日ZA, 14=日ZC, 26=次日高幅, 27=柱型, 30=上符串
护型码：a=甲 b=乙 c=丙 z=丁 y=戊 r=己

6个假设：
  甲-1/2 甲特权按0<DXAB≤4更细口径（阴柱转阳、连阳后首阴）
  甲-3   首次回踩DJA后反弹
  甲-4   好阴柱/坏阴柱（悬浮在顶+升排 vs 冲高回落）
  乙-3   升排延续 vs 触顶后推顶
  乙-6   防诱多（DJA之下升孕/连阳、DJA之上连跌）
  乙-7   a-b-c浪充分调整后再次上破DJA
  己     四柱栅转甲
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = glob.glob(DATA_DIR + '谕组日_*.csv')
print(f'共 {len(files)} 个文件')

# 聚合容器
# 甲-1/2: key=(持续天数, 阴阳) -> [n, 次日收阳n, 次日冲高n]
jia_priv = defaultdict(lambda: [0, 0, 0])
# 甲-3: key=是否首次回踩DJA -> [n, 次日冲高n]
jia_huicai = defaultdict(lambda: [0, 0])
# 甲-4: key=阴柱类型 -> [n, 次日冲高n]
jia_yinzhu = defaultdict(lambda: [0, 0])
# 乙-3: key=柱排类型 -> [n, 次日冲高n]
yi_zhuipai = defaultdict(lambda: [0, 0])
# 乙-6: key=诱多类型 -> [n, 次日冲高n]
yi_youdou = defaultdict(lambda: [0, 0])
# 乙-7: key=调整深度 -> [n, 次日冲高n]
yi_abc = defaultdict(lambda: [0, 0])
# 己: key=是否四柱栅 -> [n, 次日转甲n, 次日冲高n]
ji_sizhushan = defaultdict(lambda: [0, 0, 0])

# 基线：各护型整体次日冲高率
baseline = defaultdict(lambda: [0, 0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26,27,30])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅','柱型','上符串']
    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df = df.dropna(subset=['DXAB','涨幅','次日高幅','日ZA'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['持续'] = df['DXAB'].str.extract(r'([0-9]+)').astype(float)
    df['阴阳'] = df['涨幅'].apply(lambda x: '阳' if x > 0 else ('阴' if x < 0 else '平'))
    df['次日收阳'] = (df['涨幅'].shift(-1) > 0).astype(int)
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    df['前日ZA'] = df['日ZA'].shift(1)
    df['柱排前缀'] = df['柱排'].astype(str).str[:2]
    df['上符末位'] = df['上符串'].astype(str).str[-1]

    # 基线：各护型整体
    for hx, grp in df.groupby('护型码'):
        b = baseline[hx]
        b[0] += len(grp)
        b[1] += grp['冲高'].sum()

    # ===== 甲-1/2: 甲特权 0<DXAB≤4 =====
    jia = df[df['护型码'] == 'a']
    jia14 = jia[jia['持续'].between(1, 4)]
    for (持续, 阴阳), grp in jia14.groupby(['持续','阴阳']):
        a = jia_priv[(持续, 阴阳)]
        a[0] += len(grp)
        a[1] += grp['次日收阳'].sum()
        a[2] += grp['冲高'].sum()

    # ===== 甲-3: 首次回踩DJA（当日ZA<0 且 前日ZA>0）=====
    jia_huicai_mask = jia[(jia['日ZA'] < 0) & (jia['前日ZA'] > 0)]
    jia_huicai['首次回踩'][0] += len(jia_huicai_mask)
    jia_huicai['首次回踩'][1] += jia_huicai_mask['冲高'].sum()
    # 非首次回踩（对照）
    jia_non = jia[~((jia['日ZA'] < 0) & (jia['前日ZA'] > 0))]
    jia_huicai['非首次'][0] += len(jia_non)
    jia_huicai['非首次'][1] += jia_non['冲高'].sum()

    # ===== 甲-4: 好阴柱/坏阴柱 =====
    jia_yin = jia[jia['阴阳'] == '阴']
    # 好阴柱：悬浮在顶（上符末位=A触顶）+ 升排（柱排前缀=升）
    hao = jia_yin[(jia_yin['上符末位'] == 'A') & (jia_yin['柱排前缀'].str.startswith('升'))]
    jia_yinzhu['好阴柱(触顶+升排)'][0] += len(hao)
    jia_yinzhu['好阴柱(触顶+升排)'][1] += hao['冲高'].sum()
    # 坏阴柱：冲高回落（上影阳柱，即当日涨幅>0但次日高幅低？这里用非触顶非升排）
    huai = jia_yin[~((jia_yin['上符末位'] == 'A') & (jia_yin['柱排前缀'].str.startswith('升')))]
    jia_yinzhu['坏阴柱(其他)'][0] += len(huai)
    jia_yinzhu['坏阴柱(其他)'][1] += huai['冲高'].sum()

    # ===== 乙-3: 升排延续 vs 触顶后推顶 =====
    yi = df[df['护型码'] == 'b']
    yi_za0 = yi[yi['日ZA'] > 0]  # 乙(DXZA>0)
    # 升排延续：柱排前缀=升
    shengpai = yi_za0[yi_za0['柱排前缀'].str.startswith('升')]
    yi_zhuipai['升排延续'][0] += len(shengpai)
    yi_zhuipai['升排延续'][1] += shengpai['冲高'].sum()
    # 触顶后推顶：上符末位=A（触顶）
    chuding = yi_za0[yi_za0['上符末位'] == 'A']
    yi_zhuipai['触顶后推顶'][0] += len(chuding)
    yi_zhuipai['触顶后推顶'][1] += chuding['冲高'].sum()
    # 其他
    other = yi_za0[~(yi_za0['柱排前缀'].str.startswith('升')) & (yi_za0['上符末位'] != 'A')]
    yi_zhuipai['其他'][0] += len(other)
    yi_zhuipai['其他'][1] += other['冲高'].sum()

    # ===== 乙-6: 防诱多 =====
    yi_za_lt0 = yi[yi['日ZA'] < 0]  # 乙(DXZA<0)
    # DJA之下升孕/连阳：日ZA<0 且 柱排前缀=升
    youdou1 = yi_za_lt0[yi_za_lt0['柱排前缀'].str.startswith('升')]
    yi_youdou['DJA之下升孕/连阳'][0] += len(youdou1)
    yi_youdou['DJA之下升孕/连阳'][1] += youdou1['冲高'].sum()
    # DJA之上连跌：日ZA>0 且 柱排前缀=跌
    youdou2 = yi_za0[yi_za0['柱排前缀'].str.startswith('跌')]
    yi_youdou['DJA之上连跌'][0] += len(youdou2)
    yi_youdou['DJA之上连跌'][1] += youdou2['冲高'].sum()

    # ===== 乙-7: a-b-c浪充分调整 =====
    # 充分调整 = 日ZA深度（负值越大调整越深）
    for depth, grp in yi_za_lt0.groupby(pd.cut(yi_za_lt0['日ZA'], bins=[-100,-10,-5,-3,0], labels=['深跌≤-10','中跌-10~-5','浅跌-5~-3','微跌-3~0'])):
        yi_abc[depth][0] += len(grp)
        yi_abc[depth][1] += grp['冲高'].sum()

    # ===== 己: 四柱栅转甲 =====
    ji = df[df['护型码'] == 'r']
    shanzhu = ji[ji['柱型'].astype(str).str.contains('栅', na=False)]
    ji_sizhushan['四柱栅'][0] += len(shanzhu)
    ji_sizhushan['四柱栅'][1] += (shanzhu['护型码'].shift(-1) == 'a').sum()  # 次日转甲
    ji_sizhushan['四柱栅'][2] += shanzhu['冲高'].sum()
    feishan = ji[~ji['柱型'].astype(str).str.contains('栅', na=False)]
    ji_sizhushan['非四柱栅'][0] += len(feishan)
    ji_sizhushan['非四柱栅'][1] += (feishan['护型码'].shift(-1) == 'a').sum()
    ji_sizhushan['非四柱栅'][2] += feishan['冲高'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

# ===== 输出 =====
print('\n' + '='*70)
print('基线：各护型整体次日冲高≥3%率')
print('='*70)
for hx in ['a','b','c','z','y','r']:
    n, c = baseline[hx]
    if n > 0:
        print(f'  {hx}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('甲-1/2: 甲特权 0<DXAB≤4 更细口径（次日收阳率 / 次日冲高≥3%率）')
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
print('甲-3: 首次回踩DJA后反弹（次日冲高≥3%率）')
print('='*70)
for k, (n, c) in jia_huicai.items():
    if n > 0:
        print(f'  {k}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('甲-4: 好阴柱/坏阴柱（次日冲高≥3%率）')
print('='*70)
for k, (n, c) in jia_yinzhu.items():
    if n > 0:
        print(f'  {k}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('乙-3: 升排延续 vs 触顶后推顶（次日冲高≥3%率）')
print('='*70)
for k, (n, c) in yi_zhuipai.items():
    if n > 0:
        print(f'  {k}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('乙-6: 防诱多（次日冲高≥3%率）')
print('='*70)
for k, (n, c) in yi_youdou.items():
    if n > 0:
        print(f'  {k}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('乙-7: a-b-c浪充分调整（次日冲高≥3%率）')
print('='*70)
for k, (n, c) in yi_abc.items():
    if n > 0:
        print(f'  {k}: n={n}, P(≥3%)={c/n*100:.2f}%')

print('\n' + '='*70)
print('己: 四柱栅转甲（次日转甲率 / 次日冲高≥3%率）')
print('='*70)
for k, (n, za, cg) in ji_sizhushan.items():
    if n > 0:
        print(f'  {k}: n={n}, 次日转甲率={za/n*100:.2f}%, P(≥3%)={cg/n*100:.2f}%')
