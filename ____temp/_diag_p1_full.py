# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
dfs=[]
for i,f in enumerate(files):
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2: dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
print(f'总行数: {len(wk)}')
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
mask = m_za_neg & m5 & (wk['地型']=='6娝') & m_ren & m_jiangzhu
print(f'P1生成逻辑: 虎_6娝_等5_人排 = {mask.sum()} 行')
# 检查各条件
print(f'  m_za_neg(ZA<0): {m_za_neg.sum()}')
print(f'  m5(ZA==-1): {m5.sum()}')
print(f'  地型6娝: {(wk["地型"]=="6娝").sum()}')
print(f'  m_ren(人排): {m_ren.sum()}')
print(f'  m_jiangzhu(虎): {m_jiangzhu.sum()}')
# 两两组合
print(f'  ZA<0 & ZA==-1: {(m_za_neg & m5).sum()}')
print(f'  ZA<0 & 地型6娝: {(m_za_neg & (wk["地型"]=="6娝")).sum()}')
print(f'  ZA==-1 & 地型6娝: {(m5 & (wk["地型"]=="6娝")).sum()}')
print(f'  ZA==-1 & 地型6娝 & 人排: {(m5 & (wk["地型"]=="6娝") & m_ren).sum()}')
print(f'  ZA==-1 & 地型6娝 & 人排 & 虎: {(m5 & (wk["地型"]=="6娝") & m_ren & m_jiangzhu).sum()}')
