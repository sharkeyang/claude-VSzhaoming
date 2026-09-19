# -*- coding: utf-8 -*-
"""
阴阳镜面对称原则验证2: 护型转移/BSHA/触顶触底对称
========================================
验证更多对称原则:
  对称A: 护型转移镜像(阳区甲乙己 vs 阴区丙丁戊)
  对称B: BSHA镜像(阳区BSHA5强触发器 vs 阴区超跌反弹)
  对称C: 触顶/触底镜像(阳区触顶持有 vs 阴区触底介入)

数据: 昭明算展/谕组日/谕组日_*.csv（GBK）
权威列映射: 8=DXCD, 9=DXAB护型, 13=日ZA, 14=日ZC, 19=BSHA, 26=次日高幅, 30=上符串
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 聚合容器
agg_hx = defaultdict(lambda: [0,0])   # (ZC符号,护型)->[n,次日P3]
agg_bsha = defaultdict(lambda: [0,0]) # (ZC符号,BSHA档)->[n,次日P3]
agg_touch = defaultdict(lambda: [0,0]) # (ZC符号,触顶/触底)->[n,次日P3]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,13,14,19,26,30])
    df.columns = ['DXAB','日ZA','日ZC','BSHA','次日高幅','上符串']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['BSHA'] = pd.to_numeric(df['BSHA'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅'])
    if df.empty: continue
    df['P3'] = (df['次日高幅'] >= 3).astype(int)
    df['护型码'] = df['DXAB'].str[0]
    df['ZC符号'] = df['日ZC'].apply(lambda x: '阳' if x > 0 else '阴')
    # 对称A: 护型×ZC符号
    for (zc, hx), grp in df.groupby(['ZC符号','护型码']):
        a = agg_hx[(zc,hx)]; a[0]+=len(grp); a[1]+=grp['P3'].sum()
    # 对称B: BSHA×ZC符号
    df['BSHA档'] = pd.cut(df['BSHA'], bins=[-100,-5,-3,0,3,5,100], labels=['<-5','-5~-3','-3~0','0~3','3~5','>5'])
    for (zc, bsha), grp in df.groupby(['ZC符号','BSHA档']):
        a = agg_bsha[(zc,bsha)]; a[0]+=len(grp); a[1]+=grp['P3'].sum()
    # 对称C: 触顶/触底×ZC符号
    df['触顶'] = df['上符串'].str.endswith('A')
    df['触底'] = df['上符串'].str.endswith('w')
    for zc in ['阳','阴']:
        sub = df[df['ZC符号']==zc]
        touch = sub[sub['触顶']]
        agg_touch[(zc,'触顶')][0]+=len(touch); agg_touch[(zc,'触顶')][1]+=touch['P3'].sum()
        chudi = sub[sub['触底']]
        agg_touch[(zc,'触底')][0]+=len(chudi); agg_touch[(zc,'触底')][1]+=chudi['P3'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('对称A: 护型 × ZC符号 次日P3')
print('='*70)
print(f"{'护型':<6}{'阳区样本':>10}{'阳区P3%':>10}{'阴区样本':>10}{'阴区P3%':>10}")
for hx in ['a','b','c','z','y','r']:
    n_yang, p_yang = agg_hx[('阳',hx)]
    n_yin, p_yin = agg_hx[('阴',hx)]
    py = p_yang/n_yang*100 if n_yang>0 else 0
    pi = p_yin/n_yin*100 if n_yin>0 else 0
    print(f"{hx:<6}{n_yang:>10}{py:>10.2f}{n_yin:>10}{pi:>10.2f}")

print('\n' + '='*70)
print('对称B: BSHA × ZC符号 次日P3')
print('='*70)
print(f"{'BSHA':<8}{'阳区样本':>10}{'阳区P3%':>10}{'阴区样本':>10}{'阴区P3%':>10}")
for bsha in ['<-5','-5~-3','-3~0','0~3','3~5','>5']:
    n_yang, p_yang = agg_bsha[('阳',bsha)]
    n_yin, p_yin = agg_bsha[('阴',bsha)]
    py = p_yang/n_yang*100 if n_yang>0 else 0
    pi = p_yin/n_yin*100 if n_yin>0 else 0
    print(f"{bsha:<8}{n_yang:>10}{py:>10.2f}{n_yin:>10}{pi:>10.2f}")

print('\n' + '='*70)
print('对称C: 触顶/触底 × ZC符号 次日P3')
print('='*70)
print(f"{'形态':<6}{'阳区样本':>10}{'阳区P3%':>10}{'阴区样本':>10}{'阴区P3%':>10}")
for t in ['触顶','触底']:
    n_yang, p_yang = agg_touch[('阳',t)]
    n_yin, p_yin = agg_touch[('阴',t)]
    py = p_yang/n_yang*100 if n_yang>0 else 0
    pi = p_yin/n_yin*100 if n_yin>0 else 0
    print(f"{t:<6}{n_yang:>10}{py:>10.2f}{n_yin:>10}{pi:>10.2f}")
