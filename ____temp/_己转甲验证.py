# -*- coding: utf-8 -*-
"""验证：己转甲概率（整体 vs WXZC≤0）"""
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
wk['护型'] = wk['护型'].astype(str).str[0]
wk['下周护型'] = wk.groupby('fid')['护型'].shift(-1)
print(f'总样本: {len(wk):,}')
print()

# 己转甲：当前护型=r(己)，下周护型=a(甲)
print('=== 己转甲概率 ===')
sub = wk[wk['护型']=='r']
print(f'  己 整体: n={len(sub):,}  转甲率={(sub["下周护型"]=="a").mean()*100:.1f}%')
sub_zc0 = wk[(wk['护型']=='r') & (wk['WXZC']>0)]
print(f'  己 WXZC>0: n={len(sub_zc0):,}  转甲率={(sub_zc0["下周护型"]=="a").mean()*100:.1f}%')
sub_zcle0 = wk[(wk['护型']=='r') & (wk['WXZC']<=0)]
print(f'  己 WXZC<=0: n={len(sub_zcle0):,}  转甲率={(sub_zcle0["下周护型"]=="a").mean()*100:.1f}%')
print()

# 戊转甲
print('=== 戊转甲概率 ===')
sub = wk[wk['护型']=='y']
print(f'  戊 整体: n={len(sub):,}  转甲率={(sub["下周护型"]=="a").mean()*100:.1f}%')
sub_zc0 = wk[(wk['护型']=='y') & (wk['WXZC']>0)]
print(f'  戊 WXZC>0: n={len(sub_zc0):,}  转甲率={(sub_zc0["下周护型"]=="a").mean()*100:.1f}%')
sub_zcle0 = wk[(wk['护型']=='y') & (wk['WXZC']<=0)]
print(f'  戊 WXZC<=0: n={len(sub_zcle0):,}  转甲率={(sub_zcle0["下周护型"]=="a").mean()*100:.1f}%')
print()

# 甲维持（甲是否"极其珍贵"？甲转坏概率）
print('=== 甲 下周表现 ===')
sub = wk[wk['护型']=='a']
print(f'  甲 整体: n={len(sub):,}  下周仍甲={(sub["下周护型"]=="a").mean()*100:.1f}%  下周转坏(丙丁戊)={(sub["下周护型"].isin(["c","z","y"])).mean()*100:.1f}%')
sub_zc0 = wk[(wk['护型']=='a') & (wk['WXZC']>0)]
print(f'  甲 WXZC>0: n={len(sub_zc0):,}  下周仍甲={(sub_zc0["下周护型"]=="a").mean()*100:.1f}%  下周转坏={(sub_zc0["下周护型"].isin(["c","z","y"])).mean()*100:.1f}%')
