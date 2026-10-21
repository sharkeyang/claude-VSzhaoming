# -*- coding: utf-8 -*-
"""镜面映射：WXAB vs WXZB 谁更有把握（用户澄清：比把握度，非必要条件）"""
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
wk['后1周ZC'] = wk.groupby('fid')['ZC周'].shift(-1)
wk['后1周AB'] = wk.groupby('fid')['AB周'].shift(-1)
wk['后1周ZB'] = wk.groupby('fid')['ZB周'].shift(-1)
wk['后1周涨'] = wk.groupby('fid')['周涨'].shift(-1)
print(f'总样本: {len(wk):,}')
print()

def 报告(name, sub):
    n = len(sub)
    if n < 100:
        print(f'  {name}: n={n} 样本不足')
        return
    print(f'  {name}: n={n:,}')
    print(f'    下周ZC>0(转正): {(sub["后1周ZC"]>0).mean()*100:.1f}%  下周ZC<0(转负): {(sub["后1周ZC"]<0).mean()*100:.1f}%')
    print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%  下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
    print()

print('='*90)
print('猜想1：WXZC<0 时，WXAB>0 vs WXZB>0 谁更可能升势？')
print('='*90)
报告('WXZC<0 + WXAB>0', wk[(wk['WXZC']<0) & (wk['WXAB']>0)])
报告('WXZC<0 + WXZB>0', wk[(wk['WXZC']<0) & (wk['WXZB']>0)])
报告('WXZC<0 + WXAB>0 + WXZB>0', wk[(wk['WXZC']<0) & (wk['WXAB']>0) & (wk['WXZB']>0)])
报告('WXZC<0 + WXAB>0 + WXZB<0', wk[(wk['WXZC']<0) & (wk['WXAB']>0) & (wk['WXZB']<0)])
报告('WXZC<0 + WXAB<0 + WXZB>0', wk[(wk['WXZC']<0) & (wk['WXAB']<0) & (wk['WXZB']>0)])
print()

print('='*90)
print('猜想2：WXZC>0 时，WXAB<0 vs WXZB<0 谁更可能转跌？')
print('='*90)
报告('WXZC>0 + WXAB<0', wk[(wk['WXZC']>0) & (wk['WXAB']<0)])
报告('WXZC>0 + WXZB<0', wk[(wk['WXZC']>0) & (wk['WXZB']<0)])
报告('WXZC>0 + WXAB<0 + WXZB<0', wk[(wk['WXZC']>0) & (wk['WXAB']<0) & (wk['WXZB']<0)])
报告('WXZC>0 + WXAB<0 + WXZB>0（武）', wk[(wk['WXZC']>0) & (wk['WXAB']<0) & (wk['WXZB']>0)])
报告('WXZC>0 + WXAB>0 + WXZB<0', wk[(wk['WXZC']>0) & (wk['WXAB']>0) & (wk['WXZB']<0)])
print()

print('='*90)
print('基线对照')
print('='*90)
报告('基线（WXZC<0）', wk[wk['WXZC']<0])
报告('基线（WXZC>0）', wk[wk['WXZC']>0])
