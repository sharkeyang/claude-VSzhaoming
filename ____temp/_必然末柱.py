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
print(f'所有升连柱: {len(升连):,}')
print()

# 扫描各种特征, 看是否有"必然末柱"(下周跌孕/跌吞=100%)
# 特征: HR/周涨/触哼/喇叭宽度 等
def 末柱率(mask, name):
    sub = 升连[mask]
    n = len(sub)
    if n < 100: return
    mz = (sub['下周柱型'].isin(['跌孕','跌吞'])).mean()*100
    print(f'  {name}: n={n:,}  末柱率={mz:.1f}%')

print('=== 扫描: 是否有必然末柱特征 ===')
# HR 极高
for hr in [20,25,30,35,40]:
    末柱率(升连['HR']>=hr, f'HR>={hr}%')
# 周涨极高
for zf in [10,15,20,25]:
    末柱率(升连['周涨']>=zf, f'周涨>={zf}%')
# HR>=15 且 周涨>=HR*0.7 (最优参数)
末柱率((升连['HR']>=15)&(升连['周涨']>=升连['HR']*0.7), 'HR>=15%且周涨>=HR*0.7')
# HR>=15 且 周涨>=HR*0.8
末柱率((升连['HR']>=15)&(升连['周涨']>=升连['HR']*0.8), 'HR>=15%且周涨>=HR*0.8')
# HR>=20 且 周涨>=HR*0.7
末柱率((升连['HR']>=20)&(升连['周涨']>=升连['HR']*0.7), 'HR>=20%且周涨>=HR*0.7')
# HR>=25 且 周涨>=HR*0.7
末柱率((升连['HR']>=25)&(升连['周涨']>=升连['HR']*0.7), 'HR>=25%且周涨>=HR*0.7')
# 触哼状态
def 触哼(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
升连['触哼'] = 升连['上符串周'].astype(str).apply(触哼)
末柱率(升连['触哼']=='A', '触顶')
末柱率(升连['触哼']=='B', '触哼')
末柱率(升连['触哼']=='_', '未触')
# 喇叭宽度
def 宽符(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
升连['宽符'] = 升连['宽符串周'].astype(str).apply(宽符)
for v in ['X','4','3','2','K','I','s','o']:
    末柱率(升连['宽符']==v, f'宽符={v}')
