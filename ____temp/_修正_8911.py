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
wk = wk.dropna(subset=['下周涨','下周HR'])
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['四波'] = ''
wk.loc[(wk['WXAB']>0)&(wk['WXZB']>0),'四波']='龙'
wk.loc[(wk['WXAB']<0)&(wk['WXZB']<0),'四波']='虎'
wk.loc[(wk['WXAB']<0)&(wk['WXZB']>0),'四波']='武'
wk.loc[(wk['WXAB']>0)&(wk['WXZB']<0),'四波']='雀'
wk['柱型'] = wk['并符串周'].astype(str).str[-1]
# 护级
wk['护级'] = wk['护型'].astype(str).str[3]
# 等类
wk['ZA'] = wk['WXZA']
wk['末位'] = wk['中符串周'].astype(str).str[-1]
def 等类(row):
    za = row['ZA']
    mw = row['末位']
    if za == 1: return '等1'
    if za >= 2 and mw in ['C','D','E','F']: return '等2'
    if za >= 2 and mw in ['A','B']: return '等3'
    if za == -1: return '等5'
    if za <= -2 and mw in ['A','B','C','D']: return '等6'
    if za <= -2 and mw in ['E','F']: return '等7'
    return ''
wk['等类'] = wk.apply(等类, axis=1)

# 只取 WXZC>0 非虎
wk = wk[(wk['WXZC']>0) & (wk['四波']!='虎')].copy()
print(f'WXZC>0 非虎 样本: {len(wk)}')

def 冲高率(sub):
    return (sub['下周HR']>=3).mean()*100 if len(sub)>0 else 0

print()
print('='*80)
print('① WXZC>0 非虎整体下柱冲高率（下周HR>=3%）')
print('='*80)
for bo in ['龙','武','雀']:
    sub = wk[wk['四波']==bo]
    print(f'  {bo}: n={len(sub):,}  下柱冲高率={冲高率(sub):.2f}%')

print()
print('='*80)
print('② 按柱排细分（下周HR>=3%）')
print('='*80)
zx_map = {'O':'升吞O','Q':'升连Q','o':'升孕o','V':'跌吞V','W':'跌连W','v':'跌孕v'}
print(f'{"柱排":<8}' + ''.join(f'{bo:>12}' for bo in ['龙','武','雀']))
for z in ['O','Q','o','V','W','v']:
    cells=[]
    for bo in ['龙','武','雀']:
        sub = wk[(wk['四波']==bo)&(wk['柱型']==z)]
        cells.append(f'{冲高率(sub):>10.2f}%({len(sub)})')
    print(f'{zx_map[z]:<8}' + ''.join(cells))

print()
print('='*80)
print('③ 按护级细分（下周HR>=3%）')
print('='*80)
for bo, hx in [('龙','上'),('龙','中'),('武','忐'),('雀','下')]:
    sub = wk[(wk['四波']==bo)&(wk['护级']==hx)]
    print(f'  {bo}×护级{hx}: n={len(sub):,}  下柱冲高率={冲高率(sub):.2f}%')

print()
print('='*80)
print('④ 按等细分（下周HR>=3%）')
print('='*80)
print(f'{"等":<6}' + ''.join(f'{bo:>12}' for bo in ['龙','武','雀']))
for eq in ['等1','等2','等3','等5','等6']:
    cells=[]
    for bo in ['龙','武','雀']:
        sub = wk[(wk['四波']==bo)&(wk['等类']==eq)]
        cells.append(f'{冲高率(sub):>10.2f}%({len(sub)})')
    print(f'{eq:<6}' + ''.join(cells))

print()
print('='*80)
print('跌排后完整表现（下周口径，修正）')
print('='*80)
print(f'{"状态":<12}{"n":>10}{"下周均涨":>10}{"下周上涨率":>12}{"下周冲高率":>12}{"下周均高幅":>12}')
for bo in ['龙','武','雀']:
    for z,zn in [('V','跌吞'),('W','跌连'),('v','跌孕')]:
        sub = wk[(wk['四波']==bo)&(wk['柱型']==z)]
        n=len(sub)
        if n==0: continue
        avg=sub['下周涨'].mean()
        up=(sub['下周涨']>0).mean()*100
        hr=冲高率(sub)
        hravg=sub['下周HR'].mean()
        print(f'{bo}×{zn:<8}{n:>10,}{avg:>10.3f}%{up:>11.2f}%{hr:>11.2f}%{hravg:>11.3f}%')
