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

def show(name, mask):
    sub = wk[mask]
    n = len(sub)
    p3 = (sub['下周HR']>=3).mean()*100
    avg = sub['下周HR'].mean()
    print(f'  {name}: P3={p3:.1f}%  期望HR={avg:.2f}%  n={n:,}')

print('=== 银龙升连 合并 ===')
show('银龙升连+高(单独)', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高'))&(~wk['盈提'].str.contains('宽')))
show('银龙升连+宽高', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高')))
show('银龙升连+高(含宽高)', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高')))
print()
print('=== 金龙升连 合并 ===')
show('金龙升连+宽(单独)', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽'))&(~wk['盈提'].str.contains('高')))
show('金龙升连+高(单独)', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('高'))&(~wk['盈提'].str.contains('宽')))
show('金龙升连+宽高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高')))
show('金龙升连+宽或高(合并)', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽')|wk['盈提'].str.contains('高')))
print()
print('=== 金龙升连 全盈提(含宽/高/宽高/连N) ===')
show('金龙升连+任意盈提', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连'))
