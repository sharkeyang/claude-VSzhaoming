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
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z = bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z, '其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

# ① 各柱型占比 + 平均周涨 + 涨幅贡献
print('='*90)
print('① 各柱型占比 + 平均周涨 + 涨幅贡献（WXZC>0）')
print('='*90)
total = len(wk)
total_涨 = wk['周涨'].sum()
print(f'{"柱型":<6}{"占比":>8}{"平均周涨":>10}{"涨幅贡献":>10}')
for t in ['升连','升吞','升孕','跌吞','跌连','跌孕']:
    sub = wk[wk['柱型']==t]
    n = len(sub)
    pct = n/total*100
    avg = sub['周涨'].mean()
    contrib = sub['周涨'].sum()/total_涨*100
    print(f'{t:<6}{pct:>7.1f}%{avg:>10.2f}%{contrib:>9.1f}%')

# ② 各柱型下周冲高率
print()
print('='*90)
print('② 各柱型下周冲高率（WXZC>0）')
print('='*90)
print(f'{"柱型":<6}{"下周涨>0":>10}{"HR≥1%":>10}{"HR≥3%":>10}')
for t in ['升连','升吞','升孕','跌吞','跌连','跌孕']:
    sub = wk[wk['柱型']==t]
    n = len(sub)
    if n < 300: continue
    yang = (sub['下周涨']>0).mean()*100
    hr1 = (sub['下周HR']>=1).mean()*100
    hr3 = (sub['下周HR']>=3).mean()*100
    print(f'{t:<6}{yang:>9.1f}%{hr1:>9.1f}%{hr3:>9.1f}%')

# ③ 升连链（升连+停顿+阴转阳）的累计收益
print()
print('='*90)
print('③ 升连链累计收益（升连→停顿→阴转阳→升连）')
print('='*90)
# 升连链: 升连后(含停顿)持有到链末
# 简化: 升连后连续阳柱(升连/升吞/升孕)的累计
wk['下周柱型'] = wk.groupby('fid')['并符串周'].shift(-1).astype(str).apply(柱型)
# 升连后下周
sub = wk[wk['柱型']=='升连']
print(f'升连后下周: n={len(sub):,}')
print(f'  下周涨>0: {(sub["下周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR≥3%: {(sub["下周HR"]>=3).mean()*100:.1f}%')
print(f'  下周均涨: {sub["下周涨"].mean():.2f}%')
