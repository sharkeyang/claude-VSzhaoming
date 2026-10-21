# -*- coding: utf-8 -*-
"""镜面映射必要条件验证：转正/转负样本中 WXAB/WXZB 的比例"""
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

# 猜想1：WXZC<0 时，WXAB>0 是升势必要条件？
# 验证：转正(下周ZC>0)的样本中，当前WXAB>0的比例
print('='*90)
print('猜想1：WXZC<0 时，WXAB>0 是升势必要条件？')
print('验证：WXZC<0 中，转正(下周ZC>0)样本的当前WXAB>0比例')
print('='*90)
sub = wk[(wk['WXZC']<0) & (wk['后1周ZC']>0)]
print(f'  WXZC<0 且下周转正: n={len(sub):,}')
print(f'    其中当前WXAB>0: {(sub["WXAB"]>0).mean()*100:.1f}%')
print(f'    其中当前WXAB<0: {(sub["WXAB"]<0).mean()*100:.1f}%')
print(f'    其中当前WXZB>0: {(sub["WXZB"]>0).mean()*100:.1f}%')
print(f'    其中当前WXZB<0: {(sub["WXZB"]<0).mean()*100:.1f}%')
print()

# 猜想2：WXZC>0 时，WXAB<0 是转跌必要条件？
# 验证：转负(下周ZC<0)的样本中，当前WXAB<0比例
print('='*90)
print('猜想2：WXZC>0 时，WXAB<0 是转跌必要条件？')
print('验证：WXZC>0 中，转负(下周ZC<0)样本的当前WXAB<0比例')
print('='*90)
sub = wk[(wk['WXZC']>0) & (wk['后1周ZC']<0)]
print(f'  WXZC>0 且下周转负: n={len(sub):,}')
print(f'    其中当前WXAB<0: {(sub["WXAB"]<0).mean()*100:.1f}%')
print(f'    其中当前WXAB>0: {(sub["WXAB"]>0).mean()*100:.1f}%')
print(f'    其中当前WXZB<0: {(sub["WXZB"]<0).mean()*100:.1f}%')
print(f'    其中当前WXZB>0: {(sub["WXZB"]>0).mean()*100:.1f}%')
print()

# 对照：WXZC>0 中，转正(下周ZC>0)样本的当前WXAB<0比例
print('='*90)
print('对照：WXZC>0 中，转正(下周ZC>0)样本的当前WXAB<0比例')
print('='*90)
sub = wk[(wk['WXZC']>0) & (wk['后1周ZC']>0)]
print(f'  WXZC>0 且下周转正: n={len(sub):,}')
print(f'    其中当前WXAB<0: {(sub["WXAB"]<0).mean()*100:.1f}%')
print(f'    其中当前WXAB>0: {(sub["WXAB"]>0).mean()*100:.1f}%')
print(f'    其中当前WXZB<0: {(sub["WXZB"]<0).mean()*100:.1f}%')
print(f'    其中当前WXZB>0: {(sub["WXZB"]>0).mean()*100:.1f}%')
print()

# 猜想3：WXZB<0 退出截断亏损
print('='*90)
print('猜想3：WXZB<0 退出截断亏损（WXZB<0 是否大概率继续跌破）')
print('='*90)
sub = wk[(wk['WXZC']>0) & (wk['WXZB']<0)]
print(f'  WXZC>0 + WXZB<0: n={len(sub):,}')
print(f'    下周仍ZB<0(继续跌破): {(sub["后1周ZB"]<0).mean()*100:.1f}%')
print(f'    下周转ZB>0(转正): {(sub["后1周ZB"]>0).mean()*100:.1f}%')
print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%')
print(f'    下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
print()

# 猜想4：WXZB<0 不确定继续跌（转正样本表现）
print('='*90)
print('猜想4：WXZB<0 不确定继续跌（下周转ZB>0的样本表现）')
print('='*90)
sub = wk[(wk['WXZC']>0) & (wk['WXZB']<0) & (wk['后1周ZB']>0)]
print(f'  WXZB<0 且下周转ZB>0: n={len(sub):,}')
print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%')
print(f'    下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
print()

# 猜想5：将要下破WXZB<0前 vs 已下破后
print('='*90)
print('猜想5：将要下破WXZB<0前 vs 已下破后')
print('='*90)
sub = wk[(wk['WXZC']>0) & (wk['WXZB'].between(1,3))]
print(f'  WXZB=1-3(接近WJB): n={len(sub):,}')
print(f'    下周ZB<0(跌破): {(sub["后1周ZB"]<0).mean()*100:.1f}%')
print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%')
print(f'    下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
print()
sub = wk[(wk['WXZC']>0) & (wk['WXZB']<0)]
print(f'  WXZB<0(已跌破): n={len(sub):,}')
print(f'    下周ZB<0(仍跌破): {(sub["后1周ZB"]<0).mean()*100:.1f}%')
print(f'    下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%')
print(f'    下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
