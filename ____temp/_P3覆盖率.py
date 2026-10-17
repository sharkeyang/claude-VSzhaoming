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
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 四波(row):
    a,b = row['WXAB'], row['WXZB']
    if a>0 and b>0: return '龙'
    if a<0 and b>0: return '武'
    if a<0 and b<0: return '虎'
    if a>0 and b<0: return '雀'
    return ''
wk['四波'] = wk.apply(四波, axis=1)
wk['金银'] = wk['周势型(WXCD护型)'].astype(str).str[1]
wk['柱型'] = wk['并符串周'].astype(str).str[-1]
zx_map = {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}
wk['柱型名'] = wk['柱型'].map(zx_map)
wk = wk[wk['WXZC']>0].copy()

# 42个组合（样本>=1000）
grp = wk.groupby(['金银','四波','柱型名'])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
grp.columns = ['n','p3']
covered = grp[grp['n']>=1000]
covered_n = covered['n'].sum()
total = len(wk)
print(f'WXZC>0 全量: {total:,}')
print(f'42组合覆盖: {covered_n:,} ({covered_n/total*100:.1f}%)')
print(f'未覆盖(样本<1000组合): {total-covered_n:,} ({(total-covered_n)/total*100:.1f}%)')
print()
# 未覆盖的组合
uncovered = grp[grp['n']<1000]
print(f'未覆盖组合数: {len(uncovered)}')
print('未覆盖组合明细（金银×四波×柱型: n）:')
for (jy,bo,z), r in uncovered.sort_values('n', ascending=False).iterrows():
    print(f'  {jy}×{bo}×{z}: n={r["n"]:,}  P3={r["p3"]:.1f}%')
