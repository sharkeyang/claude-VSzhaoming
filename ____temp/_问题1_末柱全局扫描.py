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

# 所有升连柱
升连 = wk[wk['柱型']=='升连'].copy()
print(f'所有升连柱: {len(升连):,}')
print()

# 最优参数: HR>=15% 且 周涨>=HR*0.7
m_opt = (升连['HR']>=15) & (升连['周涨']>=升连['HR']*0.7)
opt = 升连[m_opt]
print(f'满足最优参数(HR>=15%,周涨>=HR*0.7)的升连柱: {len(opt):,} ({len(opt)/len(升连)*100:.1f}%)')
print()

# 这些升连柱中, 多少是末柱(下周跌孕/跌吞)?
末柱 = opt[opt['下周柱型'].isin(['跌孕','跌吞'])]
print(f'其中是末柱(下周跌孕/跌吞): {len(末柱):,} ({len(末柱)/len(opt)*100:.1f}%)')
print(f'其中非末柱(下周仍升连): {len(opt)-len(末柱):,} ({(len(opt)-len(末柱))/len(opt)*100:.1f}%)')
print()

# 对比: 所有升连柱中, 末柱占比
all_末柱 = 升连[升连['下周柱型'].isin(['跌孕','跌吞'])]
print(f'所有升连柱中末柱占比: {len(all_末柱)/len(升连)*100:.1f}%')
print(f'最优参数升连柱中末柱占比: {len(末柱)/len(opt)*100:.1f}%')
print(f'提升: {len(末柱)/len(opt)*100 - len(all_末柱)/len(升连)*100:.1f}pp')
print()

# 最优参数 下周表现
print('=== 最优参数升连柱 下周表现 ===')
print(f'  下周跌孕: {(opt["下周柱型"]=="跌孕").mean()*100:.1f}%')
print(f'  下周跌吞: {(opt["下周柱型"]=="跌吞").mean()*100:.1f}%')
print(f'  下周仍升连: {(opt["下周柱型"]=="升连").mean()*100:.1f}%')
print(f'  下周阴柱: {(opt["下周涨"]<0).mean()*100:.1f}%')
