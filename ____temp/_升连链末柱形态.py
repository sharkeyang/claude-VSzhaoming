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

# 升连链末柱: 当前升连, 下周跌孕/跌吞
末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))].copy()
# 升连链非末柱: 当前升连, 下周仍升连
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')].copy()
print(f'升连链末柱: {len(末柱):,}  非末柱: {len(非末柱):,}')
print()

# 形态定义(用 HR 高幅 和 周涨 涨幅)
def 形态(row):
    hr = row['HR']; zf = row['周涨']
    if pd.isna(hr) or pd.isna(zf): return '空'
    if hr >= 10:
        if zf >= hr * 0.5:
            return '冲高巨阳'   # 高幅大, 收盘接近高点
        else:
            return '冲高上影'   # 高幅大, 收盘远离高点
    elif hr >= 5:
        if zf >= hr * 0.5:
            return '中阳'       # 中高幅, 收盘接近高点
        else:
            return '中上影'     # 中高幅, 收盘远离高点
    else:
        return '小阳'           # 低高幅

末柱['形态'] = 末柱.apply(形态, axis=1)
非末柱['形态'] = 非末柱.apply(形态, axis=1)

print('=== 升连链末柱 vs 非末柱 形态(用HR高幅+周涨涨幅) ===')
print(f'{"形态":<12}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
for fm in ['冲高巨阳','冲高上影','中阳','中上影','小阳','空']:
    m = (末柱['形态']==fm).mean()*100
    n = (非末柱['形态']==fm).mean()*100
    if m>0.5 or n>0.5:
        print(f'{fm:<12}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
print()

# 补充: 末柱 下周表现(按形态)
print('=== 升连链末柱 各形态 下周表现 ===')
for fm in ['冲高巨阳','冲高上影','中阳','中上影','小阳']:
    sub = 末柱[末柱['形态']==fm]
    if len(sub)<500: continue
    print(f'  {fm}: n={len(sub):,}  下周跌孕={(sub["下周柱型"]=="跌孕").mean()*100:.1f}%  下周跌吞={(sub["下周柱型"]=="跌吞").mean()*100:.1f}%')
