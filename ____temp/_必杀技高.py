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

# 必杀技 = 金银×四波×柱型 + 盈提示含"高"
# 13个 P≥70% 的金银×四波×柱型
combos = [
    ('金龙升连', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')),
    ('金龙升吞', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升吞')),
    ('银龙升连', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升连')),
    ('金龙升孕', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升孕')),
    ('金龙跌孕', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')),
    ('银龙升吞', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升吞')),
    ('银龙跌吞', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='跌吞')),
    ('银龙跌孕', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')),
    ('金武升连', (wk['金银']=='金')&(wk['四波']=='武')&(wk['柱型名']=='升连')),
    ('唏龙升连', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='升连')),
    ('唏龙升孕', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='升孕')),
    ('唏龙跌孕', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')),
    ('唏龙跌吞', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='跌吞')),
]
print('='*90)
print('必杀技 = 金银×四波×柱型 + 盈提示含"高"（不关注宽）')
print('='*90)
print(f'{"组合":<12}{"P≥3%":>8}{"期望HR":>10}{"n":>10}{"每股24年":>10}')
total_n = 0
for name, base_mask in combos:
    mask = base_mask & wk['盈提'].str.contains('高')
    sub = wk[mask]
    n = len(sub)
    if n < 1000: 
        print(f'  {name:<10} 样本不足({n})')
        continue
    p3 = (sub['下周HR']>=3).mean()*100
    avg = sub['下周HR'].mean()
    per_stock = n/n_stocks
    total_n += n
    print(f'  {name:<10}{p3:>7.1f}%{avg:>10.2f}%{n:>10,}{per_stock:>10.2f}')
print(f'  合计: n={total_n:,}')
