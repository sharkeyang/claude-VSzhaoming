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
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')

# 四波
def 四波(row):
    a,b = row['WXAB'], row['WXZB']
    if a>0 and b>0: return '龙'
    if a<0 and b>0: return '武'
    if a<0 and b<0: return '虎'
    if a>0 and b<0: return '雀'
    return ''
wk['四波'] = wk.apply(四波, axis=1)

# 金银（周势型[12] 第2字符）
wk['金银'] = wk['周势型(WXCD护型)'].astype(str).str[1]

# 护型（护型[4] 第1字符）
wk['护型'] = wk['护型'].astype(str).str[0]

# 波型主体（波型[7] 中文部分）
def 波型体(w):
    import re
    if not w: return ''
    base = str(w).split('.')[0]
    m = re.search(r'[\u4e00-\u9fff〇]+$', base)
    return m.group(0) if m else base
wk['波型体'] = wk['波型'].apply(波型体)

# 柱排（并符串尾字符）
wk['柱型'] = wk['并符串周'].astype(str).str[-1]

# ZA分段
wk['ZA段'] = ''
wk.loc[wk['WXZA']==1,'ZA段']='ZA1'
wk.loc[(wk['WXZA']>=2)&(wk['中符串周'].astype(str).str[-1].isin(['C','D','E','F'])),'ZA段']='ZA2'
wk.loc[(wk['WXZA']>=2)&(wk['中符串周'].astype(str).str[-1].isin(['A','B'])),'ZA段']='ZA3'
wk.loc[wk['WXZA']==-1,'ZA段']='ZA5'
wk.loc[(wk['WXZA']<=-2)&(wk['中符串周'].astype(str).str[-1].isin(['A','B','C','D'])),'ZA段']='ZA6'
wk.loc[(wk['WXZA']<=-2)&(wk['中符串周'].astype(str).str[-1].isin(['E','F'])),'ZA段']='ZA7'

# 只取 WXZC>0 非虎（周策略P3 适用域）
wk = wk[(wk['WXZC']>0) & (wk['四波']!='虎')].copy()
print(f'WXZC>0 非虎 样本: {len(wk)}')

def 区分度(col, min_n=1000):
    """计算某维度在四波内的区分度（最强组-最弱组 P≥3%）"""
    grp = wk.groupby(['四波', col])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
    grp.columns = ['n','p3']
    grp = grp[grp['n']>=min_n]
    if len(grp)<2: return 0, 0, 0
    best = grp['p3'].max()
    worst = grp['p3'].min()
    return best-worst, best, worst

print()
print('='*80)
print('各维度在四波内的预测区分度（P≥3%，最强组-最弱组）')
print('='*80)
dims = [('金银','金银'),('护型','护型'),('波型体','波型体'),('柱型','柱型'),('ZA段','ZA段')]
for name, col in dims:
    diff, best, worst = 区分度(col)
    print(f'  {name:<8} 区分度={diff:>6.2f}pp  最强={best:>6.2f}%  最弱={worst:>6.2f}%')

print()
print('='*80)
print('四波×各维度 最强/最弱组合明细')
print('='*80)
for name, col in dims:
    grp = wk.groupby(['四波', col])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
    grp.columns = ['n','p3']
    grp = grp[grp['n']>=1000]
    if len(grp)==0: continue
    best = grp['p3'].idxmax()
    worst = grp['p3'].idxmin()
    print(f'  {name}: 最强={best[0]}×{best[1]}={grp.loc[best,"p3"]:.1f}%(n{grp.loc[best,"n"]:,})  最弱={worst[0]}×{worst[1]}={grp.loc[worst,"p3"]:.1f}%(n{grp.loc[worst,"n"]:,})')
