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
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周HR'])
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
# 四波
wk['四波'] = ''
wk.loc[(wk['WXAB']>0)&(wk['WXZB']>0),'四波']='龙'
wk.loc[(wk['WXAB']<0)&(wk['WXZB']<0),'四波']='虎'
wk.loc[(wk['WXAB']<0)&(wk['WXZB']>0),'四波']='武'
wk.loc[(wk['WXAB']>0)&(wk['WXZB']<0),'四波']='雀'
# 柱型用并符串尾字符
wk['柱型'] = wk['并符串周'].astype(str).str[-1]
# WXZC>0 非虎
wk = wk[(wk['WXZC']>0) & (wk['四波']!='虎')].copy()
print(f'WXZC>0 非虎 样本: {len(wk)}')
# 复现 §8.9.11 表格
zx_map = {'O':'升吞O','Q':'升连Q','o':'升孕o','V':'跌吞V','W':'跌连W','v':'跌孕v'}
print()
print('=== 复现 §8.9.11：四波×柱型 下周冲高率 ===')
for bo in ['龙','武','雀']:
    row = wk[wk['四波']==bo]
    cells=[]
    for z in ['O','Q','o','V','W','v']:
        sub = row[row['柱型']==z]
        n=len(sub)
        rate=(sub['下周HR']>=3).mean()*100 if n>0 else 0
        cells.append(f'{zx_map[z]}:{rate:.1f}%({n})')
    print(f'{bo}: ' + '  '.join(cells))
