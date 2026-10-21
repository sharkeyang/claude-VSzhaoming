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
wk['前并符'] = wk.groupby('fid')['并符串周'].shift(1)
wk['下周并符'] = wk.groupby('fid')['并符串周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['前柱型'] = wk['前并符'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周并符'].astype(str).apply(柱型)
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
wk = wk[wk['WXZC']>0].copy()

# 升连首柱: 当前升连, 前柱不是升连(链开始)
首柱 = wk[(wk['柱型']=='升连') & (wk['前柱型']!='升连')].copy()
# 升连末柱: 当前升连, 下周跌孕/跌吞
末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))].copy()
# 升连中柱: 当前升连, 前柱升连, 下周升连
中柱 = wk[(wk['柱型']=='升连') & (wk['前柱型']=='升连') & (wk['下周柱型']=='升连')].copy()
print(f'升连首柱: {len(首柱):,}')
print(f'升连末柱: {len(末柱):,}')
print(f'升连中柱: {len(中柱):,}')
print()

# ① 升连首柱 前柱分布(确认首柱前是升吞/升孕)
print('=== ① 升连首柱 前柱分布 ===')
print(首柱['前柱型'].value_counts().head(6))
print()

# ② 升连首柱 vs 中柱 vs 末柱 特征对比
print('=== ② 升连首柱 vs 中柱 vs 末柱 特征 ===')
print(f'{"特征":<14}{"首柱":>10}{"中柱":>10}{"末柱":>10}')
def feat(name, m1, m2, m3):
    print(f'{name:<14}{m1:>9.1f}%{m2:>9.1f}%{m3:>9.1f}%')
feat('平均周涨', 首柱['周涨'].mean(), 中柱['周涨'].mean(), 末柱['周涨'].mean())
feat('平均HR', 首柱['HR'].mean(), 中柱['HR'].mean(), 末柱['HR'].mean())
feat('巨柱(>=5%)', (首柱['周涨']>=5).mean()*100, (中柱['周涨']>=5).mean()*100, (末柱['周涨']>=5).mean()*100)
feat('中柱(2-5%)', ((首柱['周涨']>=2)&(首柱['周涨']<5)).mean()*100, ((中柱['周涨']>=2)&(中柱['周涨']<5)).mean()*100, ((末柱['周涨']>=2)&(末柱['周涨']<5)).mean()*100)
feat('小柱(<2%)', (首柱['周涨']<2).mean()*100, (中柱['周涨']<2).mean()*100, (末柱['周涨']<2).mean()*100)
print()

# ③ 触哼状态对比
def 触哼(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
首柱['触哼'] = 首柱['上符串周'].astype(str).apply(触哼)
中柱['触哼'] = 中柱['上符串周'].astype(str).apply(触哼)
末柱['触哼'] = 末柱['上符串周'].astype(str).apply(触哼)
print('=== ③ 触哼状态对比 ===')
print(f'{"触哼":<10}{"首柱":>10}{"中柱":>10}{"末柱":>10}')
for v, name in [('A','触顶'),('B','触哼'),('_','未触')]:
    m1 = (首柱['触哼']==v).mean()*100
    m2 = (中柱['触哼']==v).mean()*100
    m3 = (末柱['触哼']==v).mean()*100
    print(f'{name:<10}{m1:>9.1f}%{m2:>9.1f}%{m3:>9.1f}%')
