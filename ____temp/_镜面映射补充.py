# -*- coding: utf-8 -*-
"""镜面映射补充：转正/转负概率验证"""
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
for k in range(1, 5):
    wk[f'后{k}周ZC'] = wk.groupby('fid')['ZC周'].shift(-k)
    wk[f'后{k}周AB'] = wk.groupby('fid')['AB周'].shift(-k)
    wk[f'后{k}周涨'] = wk.groupby('fid')['周涨'].shift(-k)
print(f'总样本: {len(wk):,}')
print()

def 报告(name, sub):
    n = len(sub)
    if n < 100:
        print(f'  {name}: n={n} 样本不足')
        return
    print(f'  {name}: n={n:,}')
    print(f'    下周ZC>0(转正): {(sub["后1周ZC"]>0).mean()*100:.1f}%  下周ZC<0(转负): {(sub["后1周ZC"]<0).mean()*100:.1f}%')
    print(f'    下周AB>0(转金叉): {(sub["后1周AB"]>0).mean()*100:.1f}%  下周AB<0(转死叉): {(sub["后1周AB"]<0).mean()*100:.1f}%')
    print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%  下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
    print()

print('='*90)
print('镜面映射1：WXZC<0 时，WXAB>0 是否更可能形成升势？')
print('='*90)
报告('WXZC<0 + WXAB>0', wk[(wk['WXZC']<0) & (wk['WXAB']>0)])
报告('WXZC<0 + WXAB<0', wk[(wk['WXZC']<0) & (wk['WXAB']<0)])

print('='*90)
print('镜面映射2：WXZC>0 时，WXAB<0 是否更可能转跌？')
print('='*90)
报告('WXZC>0 + WXAB>0（龙）', wk[(wk['WXZC']>0) & (wk['WXAB']>0)])
报告('WXZC>0 + WXAB<0（武）', wk[(wk['WXZC']>0) & (wk['WXAB']<0)])

print('='*90)
print('WXZC>0 时，WXZB<0 vs WXAB<0 谁更决定转跌？')
print('='*90)
报告('WXZC>0 + WXZB<0 + WXAB>0', wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['WXAB']>0)])
报告('WXZC>0 + WXZB<0 + WXAB<0', wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['WXAB']<0)])
报告('WXZC>0 + WXZB>0 + WXAB<0（武）', wk[(wk['WXZC']>0) & (wk['WXZB']>0) & (wk['WXAB']<0)])
报告('WXZC>0 + WXZB>0 + WXAB>0（龙）', wk[(wk['WXZC']>0) & (wk['WXZB']>0) & (wk['WXAB']>0)])
