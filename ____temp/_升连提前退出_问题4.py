# -*- coding: utf-8 -*-
"""
C7 §8.8 问题4：三类提前退出条件综合
验证三类条件是否互补、能否形成完整提前退出框架。
核心：直接对比"跌连在WJA上 vs 跌破WJA"的退出信号强弱。
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
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['前柱型'] = wk.groupby('fid')['并符串周'].shift(1).astype(str).apply(柱型)
wk['前前柱型'] = wk.groupby('fid')['并符串周'].shift(2).astype(str).apply(柱型)
for k in range(1, 5):
    wk[f'后{k}周涨'] = wk.groupby('fid')['周涨'].shift(-k)
    wk[f'后{k}周HR'] = wk.groupby('fid')['HR'].shift(-k)
    wk[f'后{k}周ZA'] = wk.groupby('fid')['ZA周'].shift(-k)
    wk[f'后{k}周柱型'] = wk.groupby('fid')['并符串周'].shift(-k).astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk):,}')
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
    print(f'    下周ZA<0(跌破WJA): {(sub["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'    持有4周累计均涨: {sub["累计4周"].mean():.2f}%')
    print()

print('='*90)
print('核心对比：跌连 在WJA上 vs 跌破WJA')
print('='*90)
报告('跌连 + WXZA>0 (WJA上)', wk[(wk['柱型']=='跌连') & (wk['WXZA']>0)])
报告('跌连 + WXZA<0 (跌破WJA)', wk[(wk['柱型']=='跌连') & (wk['WXZA']<0)])
print()

print('='*90)
print('对照：跌破WXZA<0 各柱型')
print('='*90)
报告('跌破WXZA<0 + 跌连', wk[(wk['WXZA']<0) & (wk['柱型']=='跌连')])
报告('跌破WXZA<0 + 跌吞', wk[(wk['WXZA']<0) & (wk['柱型']=='跌吞')])
报告('跌破WXZA<0 + 跌孕', wk[(wk['WXZA']<0) & (wk['柱型']=='跌孕')])
报告('跌破WXZA<0 + 升孕', wk[(wk['WXZA']<0) & (wk['柱型']=='升孕')])
报告('跌破WXZA<0 + 升吞', wk[(wk['WXZA']<0) & (wk['柱型']=='升吞')])
print()

print('='*90)
print('对照：WXZA>0 各柱型（WJA上）')
print('='*90)
报告('WXZA>0 + 跌连', wk[(wk['WXZA']>0) & (wk['柱型']=='跌连')])
报告('WXZA>0 + 跌吞', wk[(wk['WXZA']>0) & (wk['柱型']=='跌吞')])
报告('WXZA>0 + 跌孕', wk[(wk['WXZA']>0) & (wk['柱型']=='跌孕')])
报告('WXZA>0 + 升孕', wk[(wk['WXZA']>0) & (wk['柱型']=='升孕')])
报告('WXZA>0 + 升吞', wk[(wk['WXZA']>0) & (wk['柱型']=='升吞')])
报告('WXZA>0 + 升连', wk[(wk['WXZA']>0) & (wk['柱型']=='升连')])
print()

print('='*90)
print('第三类细分：一串升连后 跌破WXZA<0且跌连')
print('='*90)
# 前2周内是升连链（升连→跌孕→跌连 或 升连→跌吞→跌连 等）
前2升连 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & ((wk['前柱型']=='升连') | (wk['前前柱型']=='升连'))]
报告('前2周内升连→跌破跌连', 前2升连)
# 前1周是跌孕/跌吞（升连链末柱后）
前1末柱 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & (wk['前柱型'].isin(['跌孕','跌吞']))]
报告('前1周跌孕/跌吞→跌破跌连', 前1末柱)
print()

print('='*90)
print('第三类 vs 第二类seq3 对比（是否跌破WJA是关键）')
print('='*90)
报告('第二类seq3: 升连→跌孕→跌连 (WJA上)', wk[(wk['柱型']=='跌连') & (wk['前柱型']=='跌孕') & (wk['前前柱型']=='升连') & (wk['WXZA']>0)])
报告('第三类: 跌破WXZA<0且跌连', wk[(wk['WXZA']<0) & (wk['柱型']=='跌连')])
