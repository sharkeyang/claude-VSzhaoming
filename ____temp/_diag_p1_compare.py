# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
dfs=[]
for f in files:
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2: dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
print(f'总行数: {len(wk)}')

# === P1生成逻辑 ===
wk['地型'] = wk['地型周'].astype(str)
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
m_up = wk['柱排周'].str.contains('升', na=False)
m_dn = wk['柱排周'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)
m5 = wk['ZA周'] == -1
m_za_neg = wk['ZA周'] < 0
m_jiangzhu = (wk['WXAB'] < 0) & (wk['WXZB'] < 0)
mask_p1gen = m_za_neg & m5 & (wk['地型']=='6娝') & m_ren & m_jiangzhu
print(f'P1生成逻辑: 虎_6娝_等5_人排 = {mask_p1gen.sum()}')

# === _P1匹配率.py 逻辑 ===
def 四态(row):
    a = row['WXAB']; b = row['WXZB']
    if a > 0 and b > 0: return '龙'
    elif a < 0 and b > 0: return '武'
    elif a < 0 and b < 0: return '虎'
    elif a > 0 and b < 0: return '雀'
    return ''
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
def 柱排(row):
    zp = str(row['柱排周'])
    if zp.startswith('升'): return '升排'
    elif zp.startswith('跌'): return '跌排'
    else: return '人排'
wk['四态'] = wk.apply(四态, axis=1)
wk['等类'] = wk.apply(等类, axis=1)
wk['柱排'] = wk.apply(柱排, axis=1)
wk['key'] = wk['四态'] + '_' + wk['地型'] + '_' + wk['等类'] + '_' + wk['柱排']
print(f'_P1匹配率逻辑: 虎_6娝_等5_人排 = {(wk["key"]=="虎_6娝_等5_人排").sum()}')

# 找出差异行
diff = mask_p1gen != (wk['key']=='虎_6娝_等5_人排')
print(f'差异行数: {diff.sum()}')
# 检查差异行的各字段
d = wk[diff]
print('差异行 四态分布:', d['四态'].value_counts().to_dict())
print('差异行 等类分布:', d['等类'].value_counts().to_dict())
print('差异行 柱排分布:', d['柱排'].value_counts().to_dict())
print('差异行 地型分布:', d['地型'].value_counts().to_dict())
print('差异行 ZA周 样例:', d['ZA周'].head(10).tolist())
print('差异行 中符串周 样例:', d['中符串周'].head(10).tolist())
print('差异行 柱排周 样例:', d['柱排周'].head(10).tolist())
