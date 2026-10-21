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
wk = wk[wk['WXZC']>0].copy()

末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))].copy()
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')].copy()

def 形态(sx, kf):
    sx = str(sx); kf = str(kf)
    last = sx[-1] if len(sx)>0 else '_'
    klast = kf[-1] if len(kf)>0 else 's'
    if klast=='o': return '十字星'
    if last=='B': return '长上影'
    if last=='A': return '上影'
    if last=='v': return '长下影'
    if last=='w': return '下影'
    if last=='_':
        if klast=='I': return '光头光脚长实体'
        return '光头光脚'
    return '其他'

末柱['形态'] = 末柱.apply(lambda r: 形态(r['上符串周'], r['宽符串周']), axis=1)
非末柱['形态'] = 非末柱.apply(lambda r: 形态(r['上符串周'], r['宽符串周']), axis=1)

print('=== 升连末柱 vs 非末柱 柱体形态(全部7种) ===')
print(f'{"形态":<16}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
order = ['十字星','上影','长上影','下影','长下影','光头光脚','光头光脚长实体','其他']
for fm in order:
    m = (末柱['形态']==fm).mean()*100
    n = (非末柱['形态']==fm).mean()*100
    print(f'{fm:<16}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
print()
# 合计
print(f'合计: 末柱={len(末柱):,}  非末柱={len(非末柱):,}')
