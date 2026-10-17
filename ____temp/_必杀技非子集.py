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
wk['盈提'] = wk['盈提示'].astype(str)
wk = wk[wk['WXZC']>0].copy()

# 金银×四波×柱型 + 盈提 全组合（样本>=1000），找 P≥3% 高且非必杀技子集
# 必杀技 = 金龙升连+宽高
bsj_mask = (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高'))
print(f'必杀技(金龙升连+宽高) 样本: {bsj_mask.sum():,}')

# 找其他高概率组合（金银×四波×柱型+盈提，样本>=1000，P>=70%）
grp = wk.groupby([wk['金银']+wk['四波']+wk['柱型名'], wk['盈提']])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
grp.columns = ['n','p3']
grp = grp[grp['n']>=1000]
high = grp[grp['p3']>=70].sort_values('p3', ascending=False)
print()
print('='*90)
print('金银×四波×柱型+盈提 P≥70% 组合（样本>=1000，非必杀技子集）')
print('='*90)
for (b, yt), r in high.iterrows():
    # 判断是否必杀技子集（金龙升连+宽高）
    is_subset = (b=='金龙升连' and '宽高' in yt)
    tag = ' [必杀技]' if is_subset else ''
    print(f'  {b}+{yt}: P3={r["p3"]:.1f}%  n={r["n"]:,}{tag}')
