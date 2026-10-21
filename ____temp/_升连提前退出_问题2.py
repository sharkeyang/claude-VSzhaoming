# -*- coding: utf-8 -*-
"""
C7 §8.8 问题2：第二类提前退出条件验证
升连链附近但已不是升连（仍处 WJA 之上，但可确认升连链结束）：
- 升连后跌吞 + 升孕
- 升连后跌孕 + 升吞
- 升连后跌孕 + 跌连
验证：这些是否确认升连链结束，后续转震荡？
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
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['下周并符'] = wk.groupby('fid')['并符串周'].shift(-1)
wk['前并符'] = wk.groupby('fid')['并符串周'].shift(1)
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
wk['下周柱型'] = wk['下周并符'].astype(str).apply(柱型)
wk['前柱型'] = wk['前并符'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk):,}')
print()

# 基线：所有 WXZC>0 样本的下周表现
base = wk
print('=== 基线（所有 WXZC>0） ===')
print(f'  下周涨>0: {(base["下周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(base["下周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {base["下周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {base["下周涨"].mean():.2f}%')
print()

# 第二类三种序列：锚定序列最后一柱（升孕/升吞/跌连），看其下周表现
# 序列1: 升连→跌吞→升孕  (当前=升孕, 前柱=跌吞, 前前柱=升连)
# 序列2: 升连→跌孕→升吞  (当前=升吞, 前柱=跌孕, 前前柱=升连)
# 序列3: 升连→跌孕→跌连  (当前=跌连, 前柱=跌孕, 前前柱=升连)
wk['前前并符'] = wk.groupby('fid')['并符串周'].shift(2)
wk['前前柱型'] = wk['前前并符'].astype(str).apply(柱型)

def 分析序列(name, 当前柱型, 前柱型, 前前柱型):
    mask = (wk['柱型']==当前柱型) & (wk['前柱型']==前柱型) & (wk['前前柱型']==前前柱型)
    sub = wk[mask]
    n = len(sub)
    print(f'=== 序列: {name} ===')
    if n < 100:
        print(f'  n={n} 样本不足')
        print()
        return
    print(f'  n={n:,}')
    print(f'  下周涨>0: {(sub["下周涨"]>0).mean()*100:.1f}%')
    print(f'  下周HR>=3%: {(sub["下周HR"]>=3).mean()*100:.1f}%')
    print(f'  下周平均高幅: {sub["下周HR"].mean():.2f}%')
    print(f'  下周平均涨幅: {sub["下周涨"].mean():.2f}%')
    print(f'  下周柱型分布:')
    for t, c in sub['下周柱型'].value_counts().items():
        print(f'    → {t}: {c:,} ({c/n*100:.1f}%)')
    print()

分析序列('升连→跌吞→升孕', '升孕', '跌吞', '升连')
分析序列('升连→跌孕→升吞', '升吞', '跌孕', '升连')
分析序列('升连→跌孕→跌连', '跌连', '跌孕', '升连')

print()
print('='*90)
print('对照：升连链末柱（升连→下周跌孕/跌吞）的下周表现')
print('='*90)
末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))]
print(f'  升连末柱 n={len(末柱):,}')
print(f'  下周涨>0: {(末柱["下周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(末柱["下周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {末柱["下周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {末柱["下周涨"].mean():.2f}%')
print()

# 关键问题：第二类序列是否确认升连链结束（后续转震荡）？
# 判断标准：序列完成后，后续是否不再回到升连（转震荡）
print('='*90)
print('关键验证：第二类序列完成后，后续是否转震荡（不再回升连）？')
print('='*90)
# 对每个序列，看锚定柱的"下周柱型"是否还是升连
for name, 当前柱型, 前柱型, 前前柱型 in [
    ('升连→跌吞→升孕', '升孕', '跌吞', '升连'),
    ('升连→跌孕→升吞', '升吞', '跌孕', '升连'),
    ('升连→跌孕→跌连', '跌连', '跌孕', '升连'),
]:
    mask = (wk['柱型']==当前柱型) & (wk['前柱型']==前柱型) & (wk['前前柱型']==前前柱型)
    sub = wk[mask]
    n = len(sub)
    if n < 100:
        continue
    回升连 = (sub['下周柱型']=='升连').mean()*100
    print(f'  {name}: 下周回升连率 {回升连:.1f}%')
