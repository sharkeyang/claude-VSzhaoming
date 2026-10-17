# -*- coding: utf-8 -*-
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
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['四波'] = ''
wk.loc[(wk['WXAB']>0)&(wk['WXZB']>0),'四波']='龙'
wk.loc[(wk['WXAB']<0)&(wk['WXZB']<0),'四波']='虎'
wk.loc[(wk['WXAB']<0)&(wk['WXZB']>0),'四波']='武'
wk.loc[(wk['WXAB']>0)&(wk['WXZB']<0),'四波']='雀'
wk['柱型'] = wk['并符串周'].astype(str).str[-1]
wk = wk[(wk['WXZC']>0) & (wk['四波']!='虎')].copy()
print('=== 龙×跌吞 各口径对比 ===')
sub = wk[(wk['四波']=='龙') & (wk['柱型']=='V')]
print(f'n={len(sub)}')
print(f'当前周涨>0率: {(sub["周涨"]>0).mean()*100:.2f}%')
print(f'当前均涨: {sub["周涨"].mean():.3f}%')
print(f'下周周涨>0率: {(sub["下周涨"]>0).mean()*100:.2f}%')
print(f'下周均涨: {sub["下周涨"].mean():.3f}%')
print(f'当前HR>=3率: {(sub["HR"]>=3).mean()*100:.2f}%')
print(f'下周HR>=3率: {(sub["下周HR"]>=3).mean()*100:.2f}%')
print(f'当前均高幅: {sub["HR"].mean():.3f}%')
print(f'下周均高幅: {sub["下周HR"].mean():.3f}%')
