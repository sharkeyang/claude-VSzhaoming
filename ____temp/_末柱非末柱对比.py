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
升连 = wk[wk['柱型']=='升连'].copy()
末柱 = 升连[升连['下周柱型'].isin(['跌孕','跌吞'])]
非末柱 = 升连[升连['下周柱型']=='升连']
print(f'末柱: {len(末柱):,}  非末柱: {len(非末柱):,}')
print()

# 完整特征分布对比
print('=== 末柱 vs 非末柱 完整特征分布 ===')
print(f'{"特征":<20}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
def cmp(name, m, n):
    print(f'{name:<20}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')

# 柱体大小
cmp('巨柱(周涨>=5%)', (末柱['周涨']>=5).mean()*100, (非末柱['周涨']>=5).mean()*100)
cmp('中柱(2-5%)', ((末柱['周涨']>=2)&(末柱['周涨']<5)).mean()*100, ((非末柱['周涨']>=2)&(非末柱['周涨']<5)).mean()*100)
cmp('小柱(<2%)', (末柱['周涨']<2).mean()*100, (非末柱['周涨']<2).mean()*100)
# HR 分段
cmp('HR>=20%', (末柱['HR']>=20).mean()*100, (非末柱['HR']>=20).mean()*100)
cmp('HR>=15%', (末柱['HR']>=15).mean()*100, (非末柱['HR']>=15).mean()*100)
cmp('HR>=10%', (末柱['HR']>=10).mean()*100, (非末柱['HR']>=10).mean()*100)
cmp('HR>=5%', (末柱['HR']>=5).mean()*100, (非末柱['HR']>=5).mean()*100)
# 触哼
def 触哼(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
末柱['触哼'] = 末柱['上符串周'].astype(str).apply(触哼)
非末柱['触哼'] = 非末柱['上符串周'].astype(str).apply(触哼)
cmp('触顶', (末柱['触哼']=='A').mean()*100, (非末柱['触哼']=='A').mean()*100)
cmp('触哼', (末柱['触哼']=='B').mean()*100, (非末柱['触哼']=='B').mean()*100)
cmp('未触', (末柱['触哼']=='_').mean()*100, (非末柱['触哼']=='_').mean()*100)
# 喇叭宽度(整周含某字符)
def 含宽符(s, chars):
    if not isinstance(s,str): return False
    return any(c in s for c in chars)
cmp('含4(>=40)', 末柱['宽符串周'].astype(str).apply(含宽符, chars=['4']).mean()*100, 非末柱['宽符串周'].astype(str).apply(含宽符, chars=['4']).mean()*100)
cmp('含3(>=30)', 末柱['宽符串周'].astype(str).apply(含宽符, chars=['3']).mean()*100, 非末柱['宽符串周'].astype(str).apply(含宽符, chars=['3']).mean()*100)
cmp('含2(>=20)', 末柱['宽符串周'].astype(str).apply(含宽符, chars=['2']).mean()*100, 非末柱['宽符串周'].astype(str).apply(含宽符, chars=['2']).mean()*100)
# 平均
print(f'{"平均周涨":<20}{末柱["周涨"].mean():>9.2f}%{非末柱["周涨"].mean():>9.2f}%{末柱["周涨"].mean()-非末柱["周涨"].mean():>+9.2f}pp')
print(f'{"平均HR":<20}{末柱["HR"].mean():>9.2f}%{非末柱["HR"].mean():>9.2f}%{末柱["HR"].mean()-非末柱["HR"].mean():>+9.2f}pp')
