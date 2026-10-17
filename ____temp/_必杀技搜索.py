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
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周HR'])
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
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
# 等类
wk['末位'] = wk['中符串周'].astype(str).str[-1]
def 等类(row):
    za = row['WXZA']
    mw = row['末位']
    if za == 1: return '等1'
    if za >= 2 and mw in ['C','D','E','F']: return '等2'
    if za >= 2 and mw in ['A','B']: return '等3'
    if za == -1: return '等5'
    if za <= -2 and mw in ['A','B','C','D']: return '等6'
    if za <= -2 and mw in ['E','F']: return '等7'
    return ''
wk['等类'] = wk.apply(等类, axis=1)
# 护级
wk['护级'] = wk['护型'].astype(str).str[3]
# 盈提示
wk['盈提'] = wk['盈提示'].astype(str)
# 顶触
wk['顶触'] = wk['顶触周'].astype(str)
# 波型体
def 波型体(w):
    if not w: return ''
    base = str(w).split('.')[0]
    m = re.search(r'[\u4e00-\u9fff〇]+$', base)
    return m.group(0) if m else base
wk['波型体'] = wk['波型'].apply(波型体)
# 只取 WXZC>0
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

# 基线：金银×四波×柱型
base = wk['金银']+wk['四波']+wk['柱型名']
base_valid = base[base!='']
print(f'基线(金银×四波×柱型) P≥3%: {(wk.loc[base_valid.index,"下周HR"]>=3).mean()*100:.1f}%')

# 搜索：金银×四波×柱型 + 各维度
dims = {
    '等类': wk['等类'],
    '护级': wk['护级'],
    '盈提': wk['盈提'],
    '顶触': wk['顶触'],
    '波型体': wk['波型体'],
}
print()
print('='*90)
print('金银×四波×柱型 + 各维度 搜索 P≥3% 超高组合（样本>=500）')
print('='*90)
results = []
for dim_name, dim_vals in dims.items():
    grp = wk.groupby([base, dim_vals])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
    grp.columns = ['n','p3']
    grp = grp[grp['n']>=500]
    for (b, d), r in grp.iterrows():
        results.append((r['p3'], r['n'], f'{b}+{dim_name}={d}'))

results.sort(key=lambda x: -x[0])
print('P≥3% 最高的 30 个组合:')
for p3, n, name in results[:30]:
    print(f'  {name}: P3={p3:.1f}%  n={n:,}')
