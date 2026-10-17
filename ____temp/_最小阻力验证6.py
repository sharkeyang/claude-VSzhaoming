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
wk['前前柱排'] = wk.groupby('fid')['柱排周'].shift(2)
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['下周柱排'] = wk.groupby('fid')['柱排周'].shift(-1)
wk['再下周涨'] = wk.groupby('fid')['周涨'].shift(-2)
wk['再下周HR'] = wk.groupby('fid')['HR'].shift(-2)
wk = wk.dropna(subset=['下周涨','下周HR'])
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
wk['前前柱型'] = wk['前前柱排'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周柱排'].astype(str).apply(柱型)
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

# 基线
base = wk
base_yang = (base['下周涨']>0).mean()*100
base_hr0 = (base['下周HR']>0).mean()*100
base_hr1 = (base['下周HR']>=1).mean()*100
base_hr3 = (base['下周HR']>=3).mean()*100
print(f'基线(WXZC>0全量): 下周涨>0={base_yang:.1f}%  下周HR>0={base_hr0:.1f}%  HR≥1%={base_hr1:.1f}%  HR≥3%={base_hr3:.1f}%')
print()

def show(name, mask, col='下周', min_n=500):
    sub = wk[mask]
    n = len(sub)
    if n < min_n:
        print(f'  {name}: n={n} 样本不足')
        return
    if col=='下周':
        yang = (sub['下周涨']>0).mean()*100
        hr0 = (sub['下周HR']>0).mean()*100
        hr1 = (sub['下周HR']>=1).mean()*100
        hr3 = (sub['下周HR']>=3).mean()*100
    else:
        yang = (sub['再下周涨']>0).mean()*100
        hr0 = (sub['再下周HR']>0).mean()*100
        hr1 = (sub['再下周HR']>=1).mean()*100
        hr3 = (sub['再下周HR']>=3).mean()*100
    print(f'  {name}: n={n:,}  涨>0={yang:.1f}%  HR>0={hr0:.1f}%  HR≥1%={hr1:.1f}%  HR≥3%={hr3:.1f}%')

print('='*90)
print('假设1: 前柱升连 → 后续表现(多档)')
print('='*90)
show('前柱升连', wk['前柱型']=='升连')

print()
print('='*90)
print('假设2: 前柱升连+当前阴柱 → 后续表现(多档)')
print('='*90)
show('前柱升连+当前阴柱', (wk['前柱型']=='升连')&(wk['阴阳']=='阴'))

print()
print('='*90)
print('假设3: 升连→阴→阳 → 后续表现(看再下周)')
print('='*90)
show('升连→阴→阳→再下周', (wk['前柱型']=='升连')&(wk['阴阳']=='阴')&(wk['下周阴阳']=='阳'), col='再下周')

print()
print('='*90)
print('假设4: 升连→(跌孕/跌吞)→跌连 → 后续表现')
print('='*90)
# 前柱升连，当前跌孕/跌吞，下周跌连
show('升连→跌孕/跌吞→跌连→再下周', (wk['前柱型']=='升连')&(wk['柱型'].isin(['跌孕','跌吞']))&(wk['下周柱型']=='跌连'), col='再下周')

print()
print('='*90)
print('假设5: 龙震芽后升连 → 后续表现(多档)')
print('='*90)
show('龙震芽→升连→下周', (wk['前柱型']=='升连')&(wk['波型体']=='龙震芽'))

print()
print('='*90)
print('假设6: 符合最小阻力动向 vs 不符合(多档)')
print('='*90)
符合 = (wk['WXAB']>0)&(wk['WXZA']>0)&(wk['柱型'].isin(['升连','跌孕','升吞','升孕']))
show('符合最小阻力动向', 符合)
不符合 = (wk['WXAB']>0)&(wk['WXZA']>0)&(wk['柱型'].isin(['跌吞','跌连']))
show('不符合(跌吞/跌连)', 不符合)
