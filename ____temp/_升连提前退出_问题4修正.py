# -*- coding: utf-8 -*-
"""
C7 §8.8 问题4（修正版）：三类提前退出条件综合
修正：阴阳阴锚定在第三柱（阴柱）上。
核心：对比三类条件 + 是否跌破WJA 的退出信号强弱。
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
for k in range(1, 5):
    wk[f'前{k}柱型'] = wk.groupby('fid')['并符串周'].shift(k).astype(str).apply(柱型)
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
print('基线')
print('='*90)
报告('基线（WXZC>0）', wk)

print('='*90)
print('第二类：阴阳阴/跌连（确认链结束，锚定阴柱）')
print('='*90)
报告('阴阳阴: 升连→跌吞→升孕→跌吞', wk[(wk['柱型']=='跌吞') & (wk['前1柱型']=='升孕') & (wk['前2柱型']=='跌吞') & (wk['前3柱型']=='升连')])
报告('阴阳阴: 升连→跌孕→升吞→跌孕', wk[(wk['柱型']=='跌孕') & (wk['前1柱型']=='升吞') & (wk['前2柱型']=='跌孕') & (wk['前3柱型']=='升连')])
报告('跌连: 升连→跌孕→跌连', wk[(wk['柱型']=='跌连') & (wk['前1柱型']=='跌孕') & (wk['前2柱型']=='升连')])

print('='*90)
print('第三类：跌破WXZA<0且跌连')
print('='*90)
报告('跌破WXZA<0且跌连', wk[(wk['WXZA']<0) & (wk['柱型']=='跌连')])

print('='*90)
print('关键对比：是否跌破WJA（WXZA<0）决定退出信号强弱')
print('='*90)
# 阴阳阴（跌吞+升孕+跌吞）在WJA上 vs 跌破WJA
报告('阴阳阴(跌吞+升孕+跌吞) + WXZA>0', wk[(wk['柱型']=='跌吞') & (wk['前1柱型']=='升孕') & (wk['前2柱型']=='跌吞') & (wk['前3柱型']=='升连') & (wk['WXZA']>0)])
报告('阴阳阴(跌吞+升孕+跌吞) + WXZA<0', wk[(wk['柱型']=='跌吞') & (wk['前1柱型']=='升孕') & (wk['前2柱型']=='跌吞') & (wk['前3柱型']=='升连') & (wk['WXZA']<0)])
# 跌连在WJA上 vs 跌破WJA
报告('跌连 + WXZA>0', wk[(wk['柱型']=='跌连') & (wk['WXZA']>0)])
报告('跌连 + WXZA<0', wk[(wk['柱型']=='跌连') & (wk['WXZA']<0)])

print('='*90)
print('第三类细分：一串升连后 跌破WXZA<0且跌连')
print('='*90)
报告('前2周内升连→跌破跌连', wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & ((wk['前1柱型']=='升连') | (wk['前2柱型']=='升连'))])
报告('前1周跌孕/跌吞→跌破跌连', wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & (wk['前1柱型'].isin(['跌孕','跌吞']))])
