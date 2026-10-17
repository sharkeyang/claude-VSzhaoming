# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 加载 P1.txt keys
with open('_产出物/_工具/vba表周策分P1.txt', encoding='gbk') as f:
    p1_keys = set(l.split('\t')[0] for l in f.read().splitlines()[1:] if '\t' in l)
print(f'P1.txt 共 {len(p1_keys)} 个 key')

# 模拟修复后的 P1 策略名（用等周[6]列）
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))[:200]
dfs=[]
for f in files:
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2: dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
def 四波(row):
    a,b = row['WXAB'], row['WXZB']
    if a>0 and b>0: return '龙'
    if a<0 and b>0: return '武'
    if a<0 and b<0: return '虎'
    if a>0 and b<0: return '雀'
    return ''
def 柱排向(z):
    if z.startswith('升'): return '升排'
    if z.startswith('跌'): return '跌排'
    return '人排'
wk['四波'] = wk.apply(四波, axis=1)
wk['柱排向'] = wk['柱排周'].astype(str).apply(柱排向)
# 修复后：用等周[6]列
wk['P1修复'] = wk['四波'] + '_' + wk['地型周'].astype(str) + '_' + wk['等周'].astype(str) + '_' + wk['柱排向']
# 修复前：等类为空
wk['P1旧'] = wk['四波'] + '_' + wk['地型周'].astype(str) + '_' + '_' + wk['柱排向']

total = len(wk)
match_new = wk['P1修复'].isin(p1_keys).sum()
match_old = wk['P1旧'].isin(p1_keys).sum()
print(f'总行数: {total}')
print(f'修复后匹配率: {match_new/total*100:.1f}%')
print(f'修复前匹配率: {match_old/total*100:.1f}%')
print()
print('修复后 P1 样例:', wk['P1修复'].head(5).tolist())
