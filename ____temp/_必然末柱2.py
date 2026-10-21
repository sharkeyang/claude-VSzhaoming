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
print(f'所有升连柱: {len(升连):,}  末柱率基线: {(升连["下周柱型"].isin(["跌孕","跌吞"])).mean()*100:.1f}%')
print()

# 宽符串周: 5字符, 每字符=某日喇叭宽度(X>=50/4>=40/3>=30/2>=20/K>=15/I>=10/s>=5/o>=0/_负)
# 用整周: 是否有字符达到某阈值
def 含宽符(s, chars):
    if not isinstance(s,str): return False
    return any(c in s for c in chars)

def 末柱率(mask, name):
    sub = 升连[mask]
    n = len(sub)
    if n < 100: return
    mz = (sub['下周柱型'].isin(['跌孕','跌吞'])).mean()*100
    print(f'  {name}: n={n:,}  末柱率={mz:.1f}%')

print('=== 宽符串周(整周,含某字符) 末柱率 ===')
# 含 X(>=50)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['X']), '含X(>=50)')
# 含 4(>=40)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['4']), '含4(>=40)')
# 含 3(>=30)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['3']), '含3(>=30)')
# 含 2(>=20)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['2']), '含2(>=20)')
# 含 K(>=15)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['K']), '含K(>=15)')
# 含 I(>=10)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['I']), '含I(>=10)')
# 含 s(>=5)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['s']), '含s(>=5)')
# 含 o(>=0)
末柱率(升连['宽符串周'].astype(str).apply(含宽符, chars=['o']), '含o(>=0)')
print()

# 组合: HR>=15 且 含3(>=30)
末柱率((升连['HR']>=15)&(升连['宽符串周'].astype(str).apply(含宽符, chars=['3'])), 'HR>=15%且含3(>=30)')
末柱率((升连['HR']>=20)&(升连['宽符串周'].astype(str).apply(含宽符, chars=['3'])), 'HR>=20%且含3(>=30)')
末柱率((升连['HR']>=25)&(升连['宽符串周'].astype(str).apply(含宽符, chars=['3'])), 'HR>=25%且含3(>=30)')
