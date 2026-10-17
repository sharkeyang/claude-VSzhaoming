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
# 下周HR（按fid分组shift）
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周HR'])
# WXZC>0
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

# 护型分类（第1字符）
hx = wk['护型'].astype(str).str[0]
za = wk['WXZA']
def 护型类(row):
    c = row['护型'][0]
    if c=='a': return '甲'
    if c=='b': return '乙ZA>0' if row['WXZA']>0 else '乙ZA<0'
    if c=='c': return '丙'
    if c=='r': return '己'
    if c=='z': return '丁'
    if c=='y': return '戊ZA>0' if row['WXZA']>0 else '戊ZA<0'
    return '其他'
wk['护型类'] = wk.apply(护型类, axis=1)

# 柱排六种分类
s = wk['柱排周'].astype(str)
def 柱型(row):
    z = row['柱排周']
    if z.startswith('升.尾吞'): return '升吞O'
    if z.startswith('升.尾连'): return '升连Q'
    if z.startswith('升.尾反孕'): return '升孕o'
    if z.startswith('跌.尾吞'): return '跌吞V'
    if z.startswith('跌.尾连'): return '跌连W'
    if z.startswith('跌.尾反孕'): return '跌孕v'
    return '其他'
wk['柱型'] = wk.apply(柱型, axis=1)

# 交叉表：护型类 × 柱型 → 下周冲高率(HR>=3)
hx_order = ['甲','乙ZA>0','乙ZA<0','丙','己','丁','戊ZA>0','戊ZA<0']
zx_order = ['升吞O','升连Q','升孕o','跌吞V','跌连W','跌孕v']
print()
print('='*90)
print('WXZC>0 护型×柱型 下周冲高率(HR>=3%) 交叉表')
print('='*90)
# 表头
print(f'{"护型":<10}' + ''.join(f'{z:>12}' for z in zx_order) + f'{"合计":>12}')
for h in hx_order:
    row = wk[wk['护型类']==h]
    cells = []
    for z in zx_order:
        sub = row[row['柱型']==z]
        n = len(sub)
        if n>=100:
            rate = (sub['下周HR']>=3).mean()*100
            cells.append(f'{rate:>10.1f}%({n})')
        else:
            cells.append(f'{"--":>10}({n})')
    tot = len(row)
    trate = (row['下周HR']>=3).mean()*100 if tot>0 else 0
    print(f'{h:<10}' + ''.join(cells) + f'{trate:>10.1f}%({tot})')

# 样本数表
print()
print('='*90)
print('样本数表')
print('='*90)
print(f'{"护型":<10}' + ''.join(f'{z:>12}' for z in zx_order) + f'{"合计":>12}')
for h in hx_order:
    row = wk[wk['护型类']==h]
    cells = []
    for z in zx_order:
        cells.append(f'{len(row[row["柱型"]==z]):>12}')
    print(f'{h:<10}' + ''.join(cells) + f'{len(row):>12}')
