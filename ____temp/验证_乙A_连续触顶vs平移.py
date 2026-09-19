# -*- coding: utf-8 -*-
"""
乙-A: 乙护型(DXZA>0)上破DJA后，连续触顶 vs 管中平移的比例
口径: 乙护型且DXZA>0，触顶=上符串末位A(与乙-3同口径)，统计触顶 vs 非触顶(平移)比例
数据: 昭明算展/谕组日/谕组日_*.csv（GBK，7455文件）
权威列映射: 9=DXAB护型, 13=日ZA, 14=日ZC, 30=上符串, 26=次日高幅
护型码: b=乙
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 聚合: 乙ZA>0 -> 触顶状态 -> [n, 次日冲高]
yi_touch = defaultdict(lambda: [0, 0])
yi_za0_total = [0, 0]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,13,14,26,30])
    df.columns = ['DXAB','日ZA','日ZC','次日高幅','上符串']
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df = df.dropna(subset=['DXAB','次日高幅'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    df['上符末'] = df['上符串'].astype(str).str[-1]

    yi_za0 = df[(df['护型码']=='b') & (df['日ZA']>0)]
    yi_za0_total[0] += len(yi_za0)
    yi_za0_total[1] += yi_za0['冲高'].sum()
    # 触顶(A) vs 非触顶
    touch = yi_za0[yi_za0['上符末']=='A']
    yi_touch['触顶(A)'][0] += len(touch)
    yi_touch['触顶(A)'][1] += touch['冲高'].sum()
    notouch = yi_za0[yi_za0['上符末']!='A']
    yi_touch['非触顶(平移)'][0] += len(notouch)
    yi_touch['非触顶(平移)'][1] += notouch['冲高'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('乙-A: 乙护型(DXZA>0) 触顶 vs 平移比例（触顶=上符末位A）')
print('='*70)
n_total, c_total = yi_za0_total
print(f'乙ZA>0 总数: n={n_total}, P≥3%={c_total/n_total*100:.2f}%')
for k, (n, c) in yi_touch.items():
    if n > 0:
        print(f'  {k}: n={n}, 占比={n/n_total*100:.2f}%, P≥3%={c/n*100:.2f}%')
