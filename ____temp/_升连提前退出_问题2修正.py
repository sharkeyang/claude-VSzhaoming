# -*- coding: utf-8 -*-
"""
C7 §8.8 问题2（修正版）：第二类提前退出条件验证
用户指出：阴阳阴（阴柱后阳柱再阴柱）的最后一柱是阴柱，阴柱后下周不可能回到升连。
修正：锚定在阴阳阴的第三柱（阴柱）上，看阴柱后下周表现。
第二类三种信号（锚定最后一柱）：
1. 升连→跌吞→升孕→跌吞（阴阳阴完整，锚定最后的跌吞）
2. 升连→跌孕→升吞→跌孕（阴阳阴完整，锚定最后的跌孕）
3. 升连→跌孕→跌连（锚定跌连）
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
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
# 前1~前4柱型
for k in range(1, 5):
    wk[f'前{k}柱型'] = wk.groupby('fid')['并符串周'].shift(k).astype(str).apply(柱型)
# 后续多周
for k in range(1, 5):
    wk[f'后{k}周涨'] = wk.groupby('fid')['周涨'].shift(-k)
    wk[f'后{k}周HR'] = wk.groupby('fid')['HR'].shift(-k)
    wk[f'后{k}周ZA'] = wk.groupby('fid')['ZA周'].shift(-k)
    wk[f'后{k}周柱型'] = wk.groupby('fid')['并符串周'].shift(-k).astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk):,}')
print()

# 基线
base = wk
print('=== 基线（所有 WXZC>0） ===')
print(f'  下周涨>0: {(base["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(base["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {base["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {base["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0(跌破WJA): {(base["后1周ZA"]<0).mean()*100:.1f}%')
print()

def 报告(name, sub):
    n = len(sub)
    if n < 100:
        print(f'  {name}: n={n} 样本不足')
        print()
        return
    sub = sub.copy()
    sub['累计4周'] = sub[['后1周涨','后2周涨','后3周涨','后4周涨']].sum(axis=1)
    print(f'=== {name} ===')
    print(f'  n={n:,}')
    print(f'  下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%')
    print(f'  下周HR>=3%: {(sub["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'  下周平均高幅: {sub["后1周HR"].mean():.2f}%')
    print(f'  下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
    print(f'  下周ZA<0(跌破WJA): {(sub["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'  下周回升连率: {(sub["后1周柱型"]=="升连").mean()*100:.1f}%')
    print(f'  下周柱型分布:')
    for t, c in sub['后1周柱型'].value_counts().items():
        print(f'    → {t}: {c:,} ({c/n*100:.1f}%)')
    print(f'  后2周涨>0: {(sub["后2周涨"]>0).mean()*100:.1f}%  后2周ZA<0: {(sub["后2周ZA"]<0).mean()*100:.1f}%')
    print(f'  后3周涨>0: {(sub["后3周涨"]>0).mean()*100:.1f}%  后3周ZA<0: {(sub["后3周ZA"]<0).mean()*100:.1f}%')
    print(f'  后4周涨>0: {(sub["后4周涨"]>0).mean()*100:.1f}%  后4周ZA<0: {(sub["后4周ZA"]<0).mean()*100:.1f}%')
    print(f'  持有4周累计均涨: {sub["累计4周"].mean():.2f}%')
    print()

# 第二类三种信号（锚定最后一柱）
# 1. 升连→跌吞→升孕→跌吞（阴阳阴完整，锚定最后的跌吞）
报告('阴阳阴: 升连→跌吞→升孕→跌吞',
    wk[(wk['柱型']=='跌吞') & (wk['前1柱型']=='升孕') & (wk['前2柱型']=='跌吞') & (wk['前3柱型']=='升连')])
# 2. 升连→跌孕→升吞→跌孕（阴阳阴完整，锚定最后的跌孕）
报告('阴阳阴: 升连→跌孕→升吞→跌孕',
    wk[(wk['柱型']=='跌孕') & (wk['前1柱型']=='升吞') & (wk['前2柱型']=='跌孕') & (wk['前3柱型']=='升连')])
# 3. 升连→跌孕→跌连（锚定跌连）
报告('跌连: 升连→跌孕→跌连',
    wk[(wk['柱型']=='跌连') & (wk['前1柱型']=='跌孕') & (wk['前2柱型']=='升连')])

print()
print('='*90)
print('对照：升连链末柱（升连→下周跌孕/跌吞）')
print('='*90)
末柱 = wk[(wk['柱型']=='升连') & (wk['后1周柱型'].isin(['跌孕','跌吞']))]
print(f'  升连末柱 n={len(末柱):,}')
print(f'  下周涨>0: {(末柱["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(末柱["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {末柱["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {末柱["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0: {(末柱["后1周ZA"]<0).mean()*100:.1f}%')
print()

print('='*90)
print('对照：升连链延续（升连→下周仍升连）')
print('='*90)
延续 = wk[(wk['柱型']=='升连') & (wk['后1周柱型']=='升连')]
print(f'  升连延续 n={len(延续):,}')
print(f'  下周涨>0: {(延续["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(延续["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {延续["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {延续["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0: {(延续["后1周ZA"]<0).mean()*100:.1f}%')
