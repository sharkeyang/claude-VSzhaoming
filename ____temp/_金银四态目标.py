# -*- coding: utf-8 -*-
import pandas as pd, glob, io, sys, numpy as np
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
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周HR'])
wk['势型'] = wk['周势型(WXCD护型)'].astype(str)
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')

# 金银
m_gold = wk['势型'].str.contains('金', na=False)
m_silver = wk['势型'].str.contains('银', na=False)
m_xi = wk['势型'].str.contains('唏', na=False)
m_xu = wk['势型'].str.contains('嘘', na=False)
m_niao = wk['势型'].str.contains('尿', na=False)
m_shi = wk['势型'].str.contains('屎', na=False)
jy = [('金',m_gold),('银',m_silver),('唏',m_xi),('嘘',m_xu),('尿',m_niao),('屎',m_shi)]

# 四态
m_shengzhu = (wk['WXAB']>0) & (wk['WXZB']>0)
m_jiangzhu = (wk['WXAB']<0) & (wk['WXZB']<0)
m_jiangzhuan = (wk['WXAB']<0) & (wk['WXZB']>0)
m_shengzhuan = (wk['WXAB']>0) & (wk['WXZB']<0)
st = [('升主龙',m_shengzhu),('降主虎',m_jiangzhu),('降转武',m_jiangzhuan),('升转雀',m_shengzhuan)]

print('=== 金银分类：对多个目标的预测力 ===')
print(f'{"前缀":<6}{"n":<10}{"P(HR>=1)":<10}{"平均HR":<10}{"平均周涨":<10}')
for name, m in jy:
    n = m.sum()
    g = wk.loc[m]
    print(f'{name:<6}{n:<10}{round((g["下周HR"]>=1).mean()*100,1):<10}{round(g["下周HR"].mean(),2):<10}{round(g["周涨"].mean(),3):<10}')

print()
print('=== 四态分类：对多个目标的预测力 ===')
print(f'{"前缀":<8}{"n":<10}{"P(HR>=1)":<10}{"平均HR":<10}{"平均周涨":<10}')
for name, m in st:
    n = m.sum()
    g = wk.loc[m]
    print(f'{name:<8}{n:<10}{round((g["下周HR"]>=1).mean()*100,1):<10}{round(g["下周HR"].mean(),2):<10}{round(g["周涨"].mean(),3):<10}')
