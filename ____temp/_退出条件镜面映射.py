# -*- coding: utf-8 -*-
"""
C7 §8.7.3 退出条件镜面映射验证（2026-10-18 用户课题）
用户观点：
1. 镜面映射：WXZC<0时只有WXAB>0才能基本判定可能形成升势；WXZC>0时只有WXAB<0才能基本确定转为跌势。
2. WXZB<0退出最主要目的是截断亏损，但WXZB<0时并不确定一定会继续下跌，需要权衡。
3. 将要下破WXZB<0前可以提前退出，但真正下破WXZB<0后实际不一定要退出。
"""
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
dfs=[]
for i,f in enumerate(files):
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2:
            df['fid']=i
            dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
for k in range(1, 5):
    wk[f'后{k}周涨'] = wk.groupby('fid')['周涨'].shift(-k)
    wk[f'后{k}周HR'] = wk.groupby('fid')['HR'].shift(-k)
    wk[f'后{k}周ZB'] = wk.groupby('fid')['ZB周'].shift(-k)
    wk[f'后{k}周AB'] = wk.groupby('fid')['AB周'].shift(-k)
    wk[f'后{k}周ZC'] = wk.groupby('fid')['ZC周'].shift(-k)
print(f'总样本: {len(wk):,}')
print()

def 报告(name, sub):
    n = len(sub)
    if n < 100:
        print(f'  {name}: n={n} 样本不足')
        return
    sub = sub.copy()
    sub['累计4周'] = sub[['后1周涨','后2周涨','后3周涨','后4周涨']].sum(axis=1)
    print(f'  {name}: n={n:,}')
    print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%  下周HR>=3%: {(sub["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'    下周平均涨幅: {sub["后1周涨"].mean():.2f}%  下周平均高幅: {sub["后1周HR"].mean():.2f}%')
    print(f'    下周ZB<0(仍跌破WJB): {(sub["后1周ZB"]<0).mean()*100:.1f}%')
    print(f'    下周AB<0(转均线死叉): {(sub["后1周AB"]<0).mean()*100:.1f}%')
    print(f'    持有4周累计均涨: {sub["累计4周"].mean():.2f}%')
    print()

print('='*90)
print('核心验证：WXZC>0 范围内，WXZB<0 vs WXAB<0 谁决定转跌？')
print('='*90)
# 基线
报告('基线（WXZC>0）', wk[wk['WXZC']>0])
# WXZB<0 但 WXAB>0（跌破WJB但均线仍多头）
报告('WXZC>0 + WXZB<0 + WXAB>0', wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['WXAB']>0)])
# WXZB<0 且 WXAB<0（跌破WJB且均线死叉）
报告('WXZC>0 + WXZB<0 + WXAB<0', wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['WXAB']<0)])
# WXZB>0 但 WXAB<0（WJB上但均线死叉，武）
报告('WXZC>0 + WXZB>0 + WXAB<0（武）', wk[(wk['WXZC']>0) & (wk['WXZB']>0) & (wk['WXAB']<0)])
# WXZB>0 且 WXAB>0（龙）
报告('WXZC>0 + WXZB>0 + WXAB>0（龙）', wk[(wk['WXZC']>0) & (wk['WXZB']>0) & (wk['WXAB']>0)])

print()
print('='*90)
print('验证1：WXZB<0 时是否确定继续下跌？（下破WXZB<0后不一定要退出？）')
print('='*90)
# WXZB<0 整体
报告('WXZC>0 + WXZB<0（整体）', wk[(wk['WXZC']>0) & (wk['WXZB']<0)])
# WXZB<0 且下周仍ZB<0
报告('WXZC>0 + WXZB<0 + 下周仍ZB<0', wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['后1周ZB']<0)])
# WXZB<0 且下周转ZB>0
报告('WXZC>0 + WXZB<0 + 下周转ZB>0', wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['后1周ZB']>0)])

print()
print('='*90)
print('验证2：将要下破 WXZB<0 前（WXZB 接近0）的风险')
print('='*90)
# WXZB 接近0（1,2,3）即将转负
报告('WXZC>0 + WXZB=1（刚上破WJB1天）', wk[(wk['WXZC']>0) & (wk['WXZB']==1)])
报告('WXZC>0 + WXZB=2', wk[(wk['WXZC']>0) & (wk['WXZB']==2)])
报告('WXZC>0 + WXZB=3', wk[(wk['WXZC']>0) & (wk['WXZB']==3)])
报告('WXZC>0 + WXZB=1-3（即将下破）', wk[(wk['WXZC']>0) & (wk['WXZB'].between(1,3))])
# 对比 WXZB 已转负
报告('WXZC>0 + WXZB<0（已转负）', wk[(wk['WXZC']>0) & (wk['WXZB']<0)])

print()
print('='*90)
print('验证3：镜面映射——WXZC<0 时 WXAB>0 是否确定形成升势？')
print('='*90)
报告('WXZC<0 + WXAB>0', wk[(wk['WXZC']<0) & (wk['WXAB']>0)])
报告('WXZC<0 + WXAB<0', wk[(wk['WXZC']<0) & (wk['WXAB']<0)])
