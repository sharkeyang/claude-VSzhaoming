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
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['下周并符'] = wk.groupby('fid')['并符串周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周并符'].astype(str).apply(柱型)
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk = wk[wk['WXZC']>0].copy()

# 升连末柱: 当前升连, 下周跌孕/跌吞
末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))]
# 升连非末柱: 当前升连, 下周仍升连
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')]
print(f'升连末柱(下周跌孕/跌吞): {len(末柱):,}')
print(f'升连非末柱(下周仍升连): {len(非末柱):,}')
print()

# ① 升连末柱 下周表现
print('=== ① 升连末柱 下周表现 ===')
print(f'  下周跌孕: {(末柱["下周柱型"]=="跌孕").mean()*100:.1f}%')
print(f'  下周跌吞: {(末柱["下周柱型"]=="跌吞").mean()*100:.1f}%')
print(f'  下周阴柱(涨<0): {(末柱["下周涨"]<0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(末柱["下周HR"]>=3).mean()*100:.1f}%')
print()

# ② 特征对比
print('=== ② 升连末柱 vs 非末柱 特征对比 ===')
print(f'{"特征":<12}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
def cmp(name, m, n):
    print(f'{name:<12}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
cmp('巨柱(>=5%)', (末柱['周涨']>=5).mean()*100, (非末柱['周涨']>=5).mean()*100)
cmp('中柱(2-5%)', ((末柱['周涨']>=2)&(末柱['周涨']<5)).mean()*100, ((非末柱['周涨']>=2)&(非末柱['周涨']<5)).mean()*100)
cmp('小柱(<2%)', (末柱['周涨']<2).mean()*100, (非末柱['周涨']<2).mean()*100)
cmp('十字星', (末柱['周涨'].abs()<0.5).mean()*100, (非末柱['周涨'].abs()<0.5).mean()*100)
print(f'{"平均周涨":<12}{末柱["周涨"].mean():>9.2f}%{非末柱["周涨"].mean():>9.2f}%{末柱["周涨"].mean()-非末柱["周涨"].mean():>+9.2f}pp')
print(f'{"平均HR":<12}{末柱["HR"].mean():>9.2f}%{非末柱["HR"].mean():>9.2f}%{末柱["HR"].mean()-非末柱["HR"].mean():>+9.2f}pp')
