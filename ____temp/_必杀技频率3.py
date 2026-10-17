# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
n_stocks = len(files)
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

total = len(wk)
print(f'WXZC>0 总样本: {total:,}  股票数: {n_stocks}  数据年数: 24 (2003-2026)')
print()

combos = [
    ('金龙升连+宽高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高'))),
    ('金龙升吞+宽高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升吞')&(wk['盈提'].str.contains('宽高'))),
    ('银龙升连+宽高', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高'))),
    ('银龙升吞+宽高', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升吞')&(wk['盈提'].str.contains('宽高'))),
    ('金龙升孕+宽高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升孕')&(wk['盈提'].str.contains('宽高'))),
    ('金龙跌孕+宽高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')&(wk['盈提'].str.contains('宽高'))),
    ('金龙升连+高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高'))),
    ('银龙升连+高', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高'))),
    ('金龙升吞+高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升吞')&(wk['盈提'].str.contains('高'))),
    ('金武升连+高', (wk['金银']=='金')&(wk['四波']=='武')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高'))),
    ('金龙升孕+高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升孕')&(wk['盈提'].str.contains('高'))),
    ('唏龙升连+高', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高'))),
    ('唏龙升孕+宽', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='升孕')&(wk['盈提'].str.contains('宽'))),
    ('唏龙跌孕+宽', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')&(wk['盈提'].str.contains('宽'))),
    ('唏龙跌吞+宽', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='跌吞')&(wk['盈提'].str.contains('宽'))),
    ('银龙跌吞+宽', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='跌吞')&(wk['盈提'].str.contains('宽'))),
    ('银龙跌孕+宽', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')&(wk['盈提'].str.contains('宽'))),
    ('金龙升连+宽', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽'))),
    ('金龙跌孕+宽', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')&(wk['盈提'].str.contains('宽'))),
]
print('='*90)
print('19个独立组合 频率（单只股票 24 年出现次数）')
print('='*90)
print(f'{"组合":<16}{"n":>10}{"占比":>10}{"每股24年":>10}{"每股每年":>10}')
for name, mask in combos:
    n = mask.sum()
    pct = n/total*100
    per_stock_24y = n/n_stocks
    per_stock_year = n/n_stocks/24
    print(f'{name:<16}{n:>10,}{pct:>9.2f}%{per_stock_24y:>10.2f}{per_stock_year:>10.4f}')
