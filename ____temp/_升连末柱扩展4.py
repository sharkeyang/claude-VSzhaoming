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
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
wk = wk[wk['WXZC']>0].copy()

末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))]
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')]
print(f'升连末柱: {len(末柱):,}  非末柱: {len(非末柱):,}')
print()

# ① 升连末柱 下周表现(补充平均高幅/涨幅)
print('=== ① 升连末柱 下周表现 ===')
print(f'  下周跌孕: {(末柱["下周柱型"]=="跌孕").mean()*100:.1f}%')
print(f'  下周跌吞: {(末柱["下周柱型"]=="跌吞").mean()*100:.1f}%')
print(f'  下周阴柱(涨<0): {(末柱["下周涨"]<0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(末柱["下周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {末柱["下周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {末柱["下周涨"].mean():.2f}%')
print()

# ② 维度1: 柱体大小(按周涨幅度)
print('=== ② 维度1: 柱体大小(按周涨幅度) ===')
print(f'{"柱体":<12}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
def cmp(name, m, n):
    print(f'{name:<12}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
cmp('巨柱(>=5%)', (末柱['周涨']>=5).mean()*100, (非末柱['周涨']>=5).mean()*100)
cmp('中柱(2-5%)', ((末柱['周涨']>=2)&(末柱['周涨']<5)).mean()*100, ((非末柱['周涨']>=2)&(非末柱['周涨']<5)).mean()*100)
cmp('小柱(<2%)', (末柱['周涨']<2).mean()*100, (非末柱['周涨']<2).mean()*100)
print()

# ③ 维度2: 柱体形态(影线)
# 用上符串周 判断影线: 上符串含'上影'/'长上影'等
# 先看上符串周 的取值
print('=== ③ 维度2: 柱体形态(影线) ===')
# 上符串周 列
if '上符串周' in wk.columns:
    print('上符串周 取值分布(末柱):')
    print(末柱['上符串周'].astype(str).value_counts().head(10))
else:
    print('无上符串周列')
