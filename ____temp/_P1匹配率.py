# -*- coding: utf-8 -*-
import pandas as pd, glob, io, sys
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

# 加载 P1.txt 的 key
with open('_产出物/_工具/vba表周策分P1.txt', encoding='gbk') as f:
    lines = f.read().splitlines()
p1_keys = set()
for l in lines[1:]:
    if '\t' in l:
        p1_keys.add(l.split('\t')[0])
print(f'P1.txt 共 {len(p1_keys)} 个 key')

# 模拟 VBA 端构造周策略P1
def 提取地型(p3):
    if pd.isna(p3): return ''
    f0 = str(p3).split('_')[0]
    return f0[1:] if len(f0) > 1 else ''
wk['地型'] = wk['周策略P3'].apply(提取地型)
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')

# 四态判定（与VBA一致）
def 四态(row):
    a = row['WXAB']; b = row['WXZB']
    if a > 0 and b > 0: return '龙'
    elif a < 0 and b > 0: return '武'
    elif a < 0 and b < 0: return '虎'
    elif a > 0 and b < 0: return '雀'
    return ''

# 等类（与VBA一致）
def 等类(row):
    za = row['ZA周']
    mw = str(row['中符串周'])[-1] if pd.notna(row['中符串周']) else ''
    if za == 1: return '等1'
    elif za >= 2 and mw in ['C','D','E','F']: return '等2'
    elif za >= 2 and mw in ['A','B']: return '等3'
    elif za == -1: return '等5'
    elif za <= -2 and mw in ['A','B','C','D']: return '等6'
    elif za <= -2 and mw in ['E','F']: return '等7'
    return ''

# 柱排
def 柱排(row):
    zp = str(row['柱排周'])
    if zp.startswith('升'): return '升排'
    elif zp.startswith('跌'): return '跌排'
    else: return '人排'

wk['四态'] = wk.apply(四态, axis=1)
wk['等类'] = wk.apply(等类, axis=1)
wk['柱排'] = wk.apply(柱排, axis=1)
wk['key'] = wk['四态'] + '_' + wk['地型'] + '_' + wk['等类'] + '_' + wk['柱排']

# 统计匹配率
total = len(wk)
matched = wk['key'].isin(p1_keys).sum()
print(f'总行数: {total}')
print(f'匹配: {matched} ({matched/total*100:.1f}%)')
print(f'未匹配: {total-matched} ({(total-matched)/total*100:.1f}%)')
print()
# 未匹配的原因分析
unmatched = wk[~wk['key'].isin(p1_keys)]
print('=== 未匹配样本的 key ===')
for k in unmatched['key'].value_counts().head(15).items():
    print(f'  {k[0]}: {k[1]} 行')
print()
print('=== 未匹配中 四态分布 ===')
print(unmatched['四态'].value_counts())
print()
print('=== 未匹配中 等类分布 ===')
print(unmatched['等类'].value_counts())
print()
print('=== 未匹配中 地型分布 ===')
print(unmatched['地型'].value_counts())
