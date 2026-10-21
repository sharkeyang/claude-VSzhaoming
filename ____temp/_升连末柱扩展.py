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
wk['下周柱排'] = wk.groupby('fid')['柱排周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周柱排'].astype(str).apply(柱型)
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk = wk[wk['WXZC']>0].copy()

# 升连末柱: 当前是升连(Q), 下周是跌孕(v)或跌吞(V)
# 升连非末柱: 当前是升连(Q), 下周还是升连(Q)
末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))]
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')]
print(f'升连末柱(下周跌孕/跌吞): {len(末柱):,}')
print(f'升连非末柱(下周仍升连): {len(非末柱):,}')
print()

# ① 升连末柱 下周表现(转为跌孕/跌吞的概率)
print('=== ① 升连末柱 下周表现 ===')
print(f'  下周跌孕: {(末柱["下周柱型"]=="跌孕").mean()*100:.1f}%')
print(f'  下周跌吞: {(末柱["下周柱型"]=="跌吞").mean()*100:.1f}%')
print(f'  下周阴柱(涨<0): {(末柱["下周涨"]<0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(末柱["下周HR"]>=3).mean()*100:.1f}%')
print()

# ② 升连末柱 vs 非末柱 特征对比
print('=== ② 升连末柱 vs 非末柱 特征对比 ===')
print(f'{"特征":<12}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
def feat(name, cond):
    m = cond.mean()*100
    nm = cond[非末柱.index].mean()*100 if len(cond)==len(末柱) else 0
    return m, nm
# 巨柱
m1 = (末柱['周涨']>=5).mean()*100
n1 = (非末柱['周涨']>=5).mean()*100
print(f'{"巨柱(>=5%)":<12}{m1:>9.1f}%{n1:>9.1f}%{m1-n1:>+9.1f}pp')
# 中柱
m2 = ((末柱['周涨']>=2)&(末柱['周涨']<5)).mean()*100
n2 = ((非末柱['周涨']>=2)&(非末柱['周涨']<5)).mean()*100
print(f'{"中柱(2-5%)":<12}{m2:>9.1f}%{n2:>9.1f}%{m2-n2:>+9.1f}pp')
# 小柱
m3 = (末柱['周涨']<2).mean()*100
n3 = (非末柱['周涨']<2).mean()*100
print(f'{"小柱(<2%)":<12}{m3:>9.1f}%{n3:>9.1f}%{m3-n3:>+9.1f}pp')
# 十字星
m4 = (末柱['周涨'].abs()<0.5).mean()*100
n4 = (非末柱['周涨'].abs()<0.5).mean()*100
print(f'{"十字星":<12}{m4:>9.1f}%{n4:>9.1f}%{m4-n4:>+9.1f}pp')
# 平均周涨
m5 = 末柱['周涨'].mean()
n5 = 非末柱['周涨'].mean()
print(f'{"平均周涨":<12}{m5:>9.2f}%{n5:>9.2f}%{m5-n5:>+9.2f}pp')
# 平均HR
m6 = 末柱['HR'].mean()
n6 = 非末柱['HR'].mean()
print(f'{"平均HR":<12}{m6:>9.2f}%{n6:>9.2f}%{m6-n6:>+9.2f}pp')
