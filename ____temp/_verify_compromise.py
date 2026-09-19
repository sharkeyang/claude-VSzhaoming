# -*- coding: utf-8 -*-
"""验证折中方案：保留旧入管标准(触哼+ZA>0+第二柱ZA>0)，但用DJB作为出管边界(更晚出管)
入管：触哼 + ZA>0 + 第二柱ZA>0（旧思路）
出管A(旧)：跌破DJA(变非甲乙己或DXZA<0)
出管B(新)：跌破DJB(变丙丁戊，DXZB<0)
验证：入管后，用DJB出管 vs 用DJA出管，出管率和P3对比
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串
# 入管后统计
# 出管A(旧)：变非甲乙己 或 DXZA<0
# 出管B(新)：变丙丁戊(DXZB<0)
# 指标：入管后3天P3, 5天P3, 到出管天数, 出管前累计P3
agg = defaultdict(lambda: [0,0,0,0.0,0,0])  # [n, 3天P3, 5天P3, 均高幅, 到出管A天数, 到出管B天数]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,13,26,30])
    df.columns = ['DXAB','日ZA','次日高幅','上符串']
    for c in ['日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来3天高幅'] = df['次日高幅'].rolling(3, min_periods=1).max()
    df['3天P3'] = (df['未来3天高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA正'] = (df['日ZA']>0).astype(int)
    df['触哼'] = df['上符串'].str.contains('B').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)

    za = df['ZA正'].values
    ch = df['触哼'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    p3_3 = df['3天P3'].values
    p3_5 = df['5天P3'].values
    hf = df['次日高幅'].values
    n = len(df)

    for j in range(n-2):
        # 入管：触哼+ZA>0+第二柱ZA>0
        if ch[j]==1 and za[j]==1 and za[j+1]==1:
            a = agg['入管后']
            a[0]+=1; a[1]+=p3_3[j]; a[2]+=p3_5[j]; a[3]+=hf[j]
            # 到出管A(旧)：变非甲乙己 或 DXZA<0
            daysA = None
            for k in range(1, 15):
                if j+k >= n: break
                if not ab[j+k] or not za[j+k]:
                    daysA = k; break
            # 到出管B(新)：变丙丁戊(DXZB<0)
            daysB = None
            for k in range(1, 15):
                if j+k >= n: break
                if not ab[j+k]:
                    daysB = k; break
            a[4] += daysA if daysA else 15
            a[5] += daysB if daysB else 15

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

a = agg['入管后']
print('\n' + '='*70)
print('折中方案：入管(触哼+ZA>0+第二柱ZA>0)后，DJB出管 vs DJA出管')
print('='*70)
print(f"入管样本: {a[0]}")
print(f"入管后3天P3: {a[1]/a[0]*100:.2f}%")
print(f"入管后5天P3: {a[2]/a[0]*100:.2f}%")
print(f"入管后次日均高幅: {a[3]/a[0]:.2f}")
print(f"到出管A(旧,变非甲乙己或DXZA<0)平均天数: {a[4]/a[0]:.2f}")
print(f"到出管B(新,变丙丁戊/DXZB<0)平均天数: {a[5]/a[0]:.2f}")
print(f"出管B比出管A多容忍天数: {a[5]/a[0]-a[4]/a[0]:.2f}")