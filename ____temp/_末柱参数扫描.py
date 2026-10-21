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
末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))].copy()

# 参数扫描: HR阈值 × 周涨/HR比例
print('=== 参数扫描: 冲高巨阳(下周跌孕率) vs 冲高上影(下周跌吞率) ===')
print(f'{"HR阈值":<8}{"比例":<6}{"巨阳n":>8}{"巨阳跌孕":>10}{"上影n":>8}{"上影跌吞":>10}{"区分度":>8}')
best = (0,0,0)
for hr_th in [8,10,12,15]:
    for ratio in [0.3,0.4,0.5,0.6,0.7]:
        m_jy = (末柱['HR']>=hr_th) & (末柱['周涨']>=末柱['HR']*ratio)
        m_sy = (末柱['HR']>=hr_th) & (末柱['周涨']<末柱['HR']*ratio)
        jy = 末柱[m_jy]; sy = 末柱[m_sy]
        if len(jy)<500 or len(sy)<500: continue
        jy_dy = (jy['下周柱型']=='跌孕').mean()*100
        sy_dt = (sy['下周柱型']=='跌吞').mean()*100
        diff = jy_dy - sy_dt
        print(f'{hr_th:<8}{ratio:<6}{len(jy):>8,}{jy_dy:>9.1f}%{len(sy):>8,}{sy_dt:>9.1f}%{diff:>+7.1f}pp')
        if diff > best[0]:
            best = (diff, hr_th, ratio)
print()
print(f'最优: 区分度={best[0]:.1f}pp  HR阈值={best[1]}%  比例={best[2]}')
