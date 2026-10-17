# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys, re
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
wk['前柱排'] = wk.groupby('fid')['柱排周'].shift(1)
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['再下周涨'] = wk.groupby('fid')['周涨'].shift(-2)
wk['再下周HR'] = wk.groupby('fid')['HR'].shift(-2)
wk = wk.dropna(subset=['下周涨','下周HR','再下周涨','再下周HR'])
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(z):
    if not isinstance(z,str): return ''
    if z.startswith('升.尾连'): return '升连'
    if z.startswith('升.尾吞'): return '升吞'
    if z.startswith('升.尾反孕'): return '升孕'
    if z.startswith('跌.尾吞'): return '跌吞'
    if z.startswith('跌.尾连'): return '跌连'
    if z.startswith('跌.尾反孕'): return '跌孕'
    return '其他'
wk['柱型'] = wk['柱排周'].astype(str).apply(柱型)
wk['前柱型'] = wk['前柱排'].astype(str).apply(柱型)
wk['阴阳'] = wk['周涨'].apply(lambda x: '阳' if x>0 else ('阴' if x<0 else '平'))
wk['下周阴阳'] = wk['下周涨'].apply(lambda x: '阳' if x>0 else ('阴' if x<0 else '平'))
wk['再下周阴阳'] = wk['再下周涨'].apply(lambda x: '阳' if x>0 else ('阴' if x<0 else '平'))
def 波型体(w):
    if not isinstance(w,str): return ''
    base = w.split('.')[0]
    m = re.search(r'[\u4e00-\u9fff〇]+$', base)
    return m.group(0) if m else base
wk['波型体'] = wk['波型'].astype(str).apply(波型体)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

def show(name, mask, col='下周', min_n=500):
    sub = wk[mask]
    n = len(sub)
    if n < min_n:
        print(f'  {name}: n={n} 样本不足')
        return
    if col=='下周':
        yang = (sub['下周阴阳']=='阳').mean()*100
        chonggao = (sub['下周HR']>=3).mean()*100
    else:
        yang = (sub['再下周阴阳']=='阳').mean()*100
        chonggao = (sub['再下周HR']>=3).mean()*100
    print(f'  {name}: n={n:,}  {col}阳={yang:.1f}%  {col}冲高≥3%={chonggao:.1f}%')

print()
print('='*90)
print('假设3: 前柱升连+阴柱+阳柱 → 已拉升则后续阴柱(看再下周)')
print('='*90)
show('升连→阴→阳→再下周', (wk['前柱型']=='升连')&(wk['阴阳']=='阴')&(wk['下周阴阳']=='阳'), col='再下周')

print()
print('='*90)
print('假设2补充: 前柱升连+当前阴柱 → 后续单阳或冲高(看下周)')
print('='*90)
show('前柱升连+当前阴柱', (wk['前柱型']=='升连')&(wk['阴阳']=='阴'), col='下周')

print()
print('='*90)
print('假设5: 龙震芽后升连 → 可能诱多(看升连之后)')
print('='*90)
show('龙震芽→升连→下周', (wk['前柱型']=='升连')&(wk['波型体']=='龙震芽'), col='下周')
