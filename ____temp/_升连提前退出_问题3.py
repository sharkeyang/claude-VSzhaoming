# -*- coding: utf-8 -*-
"""
C7 §8.8 问题3：第三类提前退出条件验证
一串升连后，跌破 WXZA<0 且为跌连：
- 前期已围绕 WJA 震荡
- 此次下破 WXZA<0 且为跌连
- 就是提前退出条件
验证：是否确认提前退出？后续表现？
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
# 前几周是否升连链（一串升连后）
wk['前1柱型'] = wk['前柱型']
wk['前2柱型'] = wk.groupby('fid')['并符串周'].shift(2).astype(str).apply(柱型)
wk['前3柱型'] = wk.groupby('fid')['并符串周'].shift(3).astype(str).apply(柱型)
wk['前4柱型'] = wk.groupby('fid')['并符串周'].shift(4).astype(str).apply(柱型)
# 后续多周
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

# 第三类：跌破 WXZA<0 且为跌连
print('='*90)
print('第三类：跌破 WXZA<0 且为跌连')
print('='*90)
# 当前柱：WXZA<0 且 柱型=跌连
下破跌连 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连')]
print(f'  跌破WXZA<0且跌连: n={len(下破跌连):,}')
print(f'  下周涨>0: {(下破跌连["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(下破跌连["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均高幅: {下破跌连["后1周HR"].mean():.2f}%')
print(f'  下周平均涨幅: {下破跌连["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0(仍跌破): {(下破跌连["后1周ZA"]<0).mean()*100:.1f}%')
print(f'  后2周涨>0: {(下破跌连["后2周涨"]>0).mean()*100:.1f}%  后2周ZA<0: {(下破跌连["后2周ZA"]<0).mean()*100:.1f}%')
print(f'  后3周涨>0: {(下破跌连["后3周涨"]>0).mean()*100:.1f}%  后3周ZA<0: {(下破跌连["后3周ZA"]<0).mean()*100:.1f}%')
print(f'  后4周涨>0: {(下破跌连["后4周涨"]>0).mean()*100:.1f}%  后4周ZA<0: {(下破跌连["后4周ZA"]<0).mean()*100:.1f}%')
下破跌连['累计4周'] = 下破跌连[['后1周涨','后2周涨','后3周涨','后4周涨']].sum(axis=1)
print(f'  持有4周累计均涨: {下破跌连["累计4周"].mean():.2f}%')
print()

# 细分：前几周是否升连链（一串升连后）
print('='*90)
print('细分：前几周是否升连链（一串升连后）')
print('='*90)
# 前1周是升连
前1升连 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & (wk['前1柱型']=='升连')]
print(f'  前1周升连→跌破跌连: n={len(前1升连):,}')
if len(前1升连)>100:
    print(f'    下周涨>0: {(前1升连["后1周涨"]>0).mean()*100:.1f}%')
    print(f'    下周HR>=3%: {(前1升连["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'    下周平均涨幅: {前1升连["后1周涨"].mean():.2f}%')
    print(f'    下周ZA<0: {(前1升连["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'    持有4周累计均涨: {前1升连[["后1周涨","后2周涨","后3周涨","后4周涨"]].sum(axis=1).mean():.2f}%')
print()

# 前2周内是升连链（前1或前2是升连）
前2升连 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & ((wk['前1柱型']=='升连') | (wk['前2柱型']=='升连'))]
print(f'  前2周内升连→跌破跌连: n={len(前2升连):,}')
if len(前2升连)>100:
    print(f'    下周涨>0: {(前2升连["后1周涨"]>0).mean()*100:.1f}%')
    print(f'    下周HR>=3%: {(前2升连["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'    下周平均涨幅: {前2升连["后1周涨"].mean():.2f}%')
    print(f'    下周ZA<0: {(前2升连["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'    持有4周累计均涨: {前2升连[["后1周涨","后2周涨","后3周涨","后4周涨"]].sum(axis=1).mean():.2f}%')
print()

# 前3周内是升连链
前3升连 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & ((wk['前1柱型']=='升连') | (wk['前2柱型']=='升连') | (wk['前3柱型']=='升连'))]
print(f'  前3周内升连→跌破跌连: n={len(前3升连):,}')
if len(前3升连)>100:
    print(f'    下周涨>0: {(前3升连["后1周涨"]>0).mean()*100:.1f}%')
    print(f'    下周HR>=3%: {(前3升连["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'    下周平均涨幅: {前3升连["后1周涨"].mean():.2f}%')
    print(f'    下周ZA<0: {(前3升连["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'    持有4周累计均涨: {前3升连[["后1周涨","后2周涨","后3周涨","后4周涨"]].sum(axis=1).mean():.2f}%')
print()

# 对照：跌破 WXZA<0 但非跌连（其他柱型）
print('='*90)
print('对照：跌破 WXZA<0 但非跌连（其他柱型）')
print('='*90)
下破非跌连 = wk[(wk['WXZA']<0) & (wk['柱型']!='跌连')]
print(f'  跌破WXZA<0非跌连: n={len(下破非跌连):,}')
print(f'  下周涨>0: {(下破非跌连["后1周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(下破非跌连["后1周HR"]>=3).mean()*100:.1f}%')
print(f'  下周平均涨幅: {下破非跌连["后1周涨"].mean():.2f}%')
print(f'  下周ZA<0: {(下破非跌连["后1周ZA"]<0).mean()*100:.1f}%')
print()

# 对照：跌破 WXZA<0 且为跌连，但前几周无升连（非一串升连后）
print('='*90)
print('对照：跌破WXZA<0且跌连，但前3周无升连（非一串升连后）')
print('='*90)
无前升连 = wk[(wk['WXZA']<0) & (wk['柱型']=='跌连') & ~((wk['前1柱型']=='升连') | (wk['前2柱型']=='升连') | (wk['前3柱型']=='升连'))]
print(f'  无前升连跌破跌连: n={len(无前升连):,}')
if len(无前升连)>100:
    print(f'    下周涨>0: {(无前升连["后1周涨"]>0).mean()*100:.1f}%')
    print(f'    下周HR>=3%: {(无前升连["后1周HR"]>=3).mean()*100:.1f}%')
    print(f'    下周平均涨幅: {无前升连["后1周涨"].mean():.2f}%')
    print(f'    下周ZA<0: {(无前升连["后1周ZA"]<0).mean()*100:.1f}%')
    print(f'    持有4周累计均涨: {无前升连[["后1周涨","后2周涨","后3周涨","后4周涨"]].sum(axis=1).mean():.2f}%')
