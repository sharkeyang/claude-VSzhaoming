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
wk = wk[(wk['WXZC']>0) & (wk['四波']!='虎')].copy()

print(f'WXZC>0 非虎 样本: {len(wk)}')
print()
print('='*90)
print('金银 × 四波 × 柱型 下周冲高率(P≥3%) 交叉表')
print('='*90)

# 金银×四波×柱型 分组
grp = wk.groupby(['金银','四波','柱型名'])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
grp.columns = ['n','p3']
grp = grp[grp['n']>=1000]

# 按金银×四波 打印柱型
for jy in ['金','银','唏','嘘','尿','屎']:
    for bo in ['龙','武','雀']:
        sub = grp.loc[(jy,bo)] if (jy,bo) in grp.index else None
        if sub is None or len(sub)==0: continue
        cells=[]
        for z in ['升吞','升连','升孕','跌吞','跌连','跌孕']:
            if z in sub.index:
                r = sub.loc[z]
                cells.append(f'{z}:{r["p3"]:.1f}%({r["n"]:,})')
        if cells:
            print(f'{jy}×{bo}: ' + '  '.join(cells))

print()
print('='*90)
print('金银×四波×柱型 最优/最弱 组合（样本>=1000）')
print('='*90)
grp_sorted = grp.sort_values('p3', ascending=False)
print('最优10:')
for (jy,bo,z), r in grp_sorted.head(10).iterrows():
    print(f'  {jy}×{bo}×{z}: P3={r["p3"]:.1f}%  n={r["n"]:,}')
print('最弱10:')
for (jy,bo,z), r in grp_sorted.tail(10).iterrows():
    print(f'  {jy}×{bo}×{z}: P3={r["p3"]:.1f}%  n={r["n"]:,}')
