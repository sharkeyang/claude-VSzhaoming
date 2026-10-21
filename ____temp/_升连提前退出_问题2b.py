# -*- coding: utf-8 -*-
"""
C7 §8.8 问题2：第二类提前退出条件验证（改进版）
升连链附近但已不是升连（仍处 WJA 之上，但可确认升连链结束）：
- 升连后跌吞 + 升孕
- 升连后跌孕 + 升吞
- 升连后跌孕 + 跌连
验证：这些是否确认升连链结束，后续转震荡？
关键：加 WXZA>0（仍处 WJA 之上）过滤 + 看后续多周表现
"""
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
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['前柱型'] = wk.groupby('fid')['并符串周'].shift(1).astype(str).apply(柱型)
wk['前前柱型'] = wk.groupby('fid')['并符串周'].shift(2).astype(str).apply(柱型)
# 后续多周表现
for k in range(1, 5):
    wk[f'后{k}周涨'] = wk.groupby('fid')['周涨'].shift(-k)
    wk[f'后{k}周HR'] = wk.groupby('fid')['HR'].shift(-k)
    wk[f'后{k}周ZA'] = wk.groupby('fid')['ZA周'].shift(-k)
    wk[f'后{k}周柱型'] = wk.groupby('fid')['并符串周'].shift(-k).astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk):,}')
print()

# 基线
base = wk
print('=== 基线（所有 WXZC>0） ===')
print(f'  下周涨>0: {(base["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(base["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {base["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {base["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0(跌破WJA): {(base["后1周ZA"]<0).mean()*100:.1f}%')
print()

def 分析序列(name, 当前柱型, 前柱型, 前前柱型, 需WJA上=True):
    mask = (wk['柱型']==当前柱型) & (wk['前柱型']==前柱型) & (wk['前前柱型']==前前柱型)
    if 需WJA上:
        mask = mask & (wk['WXZA']>0)
    sub = wk[mask]
    n = len(sub)
    print(f'=== 序列: {name} {"(WJA上)" if 需WJA上 else ""} ===')
    if n < 100:
        print(f'  n={n} 样本不足')
        print()
        return
    print(f'  n={n:,}')
    print(f'  下周涨>0: {(sub["后1周涨"]>0).mean()*100:.1f}%')
    print(f'  下周HR>=3%: {(sub["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'  下周平均高幅: {sub["后1周HR"].mean():.2f}%')
    print(f'  下周平均涨幅: {sub["后1周涨"].mean():.2f}%')
    print(f'  下周ZA<0(跌破WJA): {(sub["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'  下周回升连率: {(sub["后1周柱型"]=="升连").mean()*100:.1f}%')
    # 后续多周
    print(f'  后2周涨>0: {(sub["后2周涨"]>0).mean()*100:.1f}%  后2周ZA<0: {(sub["后2周ZA"]<0).mean()*100:.1f}%')
    print(f'  后3周涨>0: {(sub["后3周涨"]>0).mean()*100:.1f}%  后3周ZA<0: {(sub["后3周ZA"]<0).mean()*100:.1f}%')
    print(f'  后4周涨>0: {(sub["后4周涨"]>0).mean()*100:.1f}%  后4周ZA<0: {(sub["后4周ZA"]<0).mean()*100:.1f}%')
    # 累计收益（持有4周）
    sub['累计4周'] = sub[['后1周涨','后2周涨','后3周涨','后4周涨']].sum(axis=1)
    print(f'  持有4周累计均涨: {sub["累计4周"].mean():.2f}%')
    print()

分析序列('升连→跌吞→升孕', '升孕', '跌吞', '升连')
分析序列('升连→跌孕→升吞', '升吞', '跌孕', '升连')
分析序列('升连→跌孕→跌连', '跌连', '跌孕', '升连')

print()
print('='*90)
print('对照1：升连链末柱（升连→下周跌孕/跌吞）')
print('='*90)
末柱 = wk[(wk['柱型']=='升连') & (wk['后1周柱型'].isin(['跌孕','跌吞']))]
print(f'  升连末柱 n={len(末柱):,}')
print(f'  下周涨>0: {(末柱["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(末柱["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {末柱["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {末柱["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0: {(末柱["后1周ZA"]<0).mean()*100:.1f}%')
print()

print('='*90)
print('对照2：升连链延续（升连→下周仍升连）')
print('='*90)
延续 = wk[(wk['柱型']=='升连') & (wk['后1周柱型']=='升连')]
print(f'  升连延续 n={len(延续):,}')
print(f'  下周涨>0: {(延续["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(延续["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {延续["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {延续["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0: {(延续["后1周ZA"]<0).mean()*100:.1f}%')
print()

print('='*90)
print('对照3：所有升连柱（不分末柱/延续）')
print('='*90)
升连 = wk[wk['柱型']=='升连']
print(f'  升连 n={len(升连):,}')
print(f'  下周涨>0: {(升连["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(升连["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {升连["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {升连["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0: {(升连["后1周ZA"]<0).mean()*100:.1f}%')
