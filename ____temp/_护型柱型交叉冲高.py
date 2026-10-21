# -*- coding: utf-8 -*-
"""
C7 交叉分析：WXZC>0 护型(8类) × 六种柱型 → 下周冲高概率
护型编码[4]首字符: a甲/b乙/c丙/z丁/y戊/r己
柱型用并符串周[51]尾字符: O升吞/Q升连/o升孕/V跌吞/W跌连/v跌孕
下周冲高 = 下周HR≥3%
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
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
# 护型首字符
wk['护型'] = wk['护型'].astype(str).str[0]
# 柱型
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk):,}')
print()

# 护型8类
def 护型8(护型, WXZA):
    if 护型=='a': return '甲'
    if 护型=='b': return '乙(WXZA>0)' if WXZA>0 else '乙(WXZA<0)'
    if 护型=='c': return '丙'
    if 护型=='r': return '己'
    if 护型=='z': return '丁'
    if 护型=='y': return '戊(WXZA>0)' if WXZA>0 else '戊(WXZA<0)'
    return '其他'
wk['护型8'] = [护型8(h, z) for h, z in zip(wk['护型'], wk['WXZA'])]

# 基线
print('=== 基线（WXZC>0 全量） ===')
print(f'  下周HR>=3%(冲高): {(wk["下周HR"]>=3).mean()*100:.1f}%')
print(f'  下周涨>0: {(wk["下周涨"]>0).mean()*100:.1f}%')
print()

# 交叉表：护型8 × 柱型 → 下周冲高率
柱型序 = ['升吞','升连','升孕','跌吞','跌连','跌孕']
护型序 = ['甲','乙(WXZA>0)','乙(WXZA<0)','丙','己','丁','戊(WXZA>0)','戊(WXZA<0)']
print('=== 交叉表：护型8 × 柱型 → 下周冲高率(下周HR>=3%) ===')
print(f'{"护型":<12}{"升吞":>8}{"升连":>8}{"升孕":>8}{"跌吞":>8}{"跌连":>8}{"跌孕":>8}')
for h in 护型序:
    row = []
    for c in 柱型序:
        sub = wk[(wk['护型8']==h)&(wk['柱型']==c)]
        n = len(sub)
        if n < 100:
            row.append('  -')
        else:
            row.append(f'{(sub["下周HR"]>=3).mean()*100:6.1f}')
    print(f'{h:<12}' + ''.join(f'{x:>8}' for x in row))
print()

# 每行护型的整体冲高率
print('=== 各护型整体下周冲高率 ===')
for h in 护型序:
    sub = wk[wk['护型8']==h]
    n = len(sub)
    if n < 100:
        print(f'  {h:<12}: n={n} 样本不足')
    else:
        print(f'  {h:<12}: n={n:,}  冲高率={(sub["下周HR"]>=3).mean()*100:.1f}%')
print()

# 每列柱型的整体冲高率
print('=== 各柱型整体下周冲高率 ===')
for c in 柱型序:
    sub = wk[wk['柱型']==c]
    n = len(sub)
    print(f'  {c:<6}: n={n:,}  冲高率={(sub["下周HR"]>=3).mean()*100:.1f}%')
print()

# 关键问题：是否"只要不是跌排就有下周冲高"？
# 跌排 = 跌吞/跌连/跌孕；升排 = 升吞/升连/升孕
print('=== 升排 vs 跌排 下周冲高率 ===')
for 排, 柱 in [('升排',['升吞','升连','升孕']), ('跌排',['跌吞','跌连','跌孕'])]:
    sub = wk[wk['柱型'].isin(柱)]
    print(f'  {排}: n={len(sub):,}  冲高率={(sub["下周HR"]>=3).mean()*100:.1f}%')
