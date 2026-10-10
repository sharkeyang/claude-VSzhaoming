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
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周HR'])
wk['势型'] = wk['周势型(WXCD护型)'].astype(str)
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')

# 金银分类
m_gold = wk['势型'].str.contains('金', na=False)
m_silver = wk['势型'].str.contains('银', na=False)
m_xi = wk['势型'].str.contains('唏', na=False)
m_xu = wk['势型'].str.contains('嘘', na=False)
m_niao = wk['势型'].str.contains('尿', na=False)
m_shi = wk['势型'].str.contains('屎', na=False)

# 四态
m_shengzhu = (wk['WXAB']>0) & (wk['WXZB']>0)
m_jiangzhu = (wk['WXAB']<0) & (wk['WXZB']<0)
m_jiangzhuan = (wk['WXAB']<0) & (wk['WXZB']>0)
m_shengzhuan = (wk['WXAB']>0) & (wk['WXZB']<0)

def stat(mask, label):
    n = mask.sum()
    if n==0: return None
    g = wk.loc[mask]
    p3 = round((g['下周HR']>=1).mean()*100,1)
    avg = round(g['下周HR'].mean(),3)
    return (label, n, p3, avg)

print('='*70)
print('【1】金银分类作为前缀，内部再按四态细分 —— 金银内部是否还有四态信息？')
print('='*70)
for gname, gm in [('金',m_gold),('银',m_silver),('唏',m_xi),('嘘',m_xu),('尿',m_niao),('屎',m_shi)]:
    print(f'\n--- {gname} 内部按四态细分 ---')
    for sname, sm in [('升主龙',m_shengzhu),('降主虎',m_jiangzhu),('降转武',m_jiangzhuan),('升转雀',m_shengzhuan)]:
        r = stat(gm & sm, f'{gname}+{sname}')
        if r: print(f'  {r[0]}: n={r[1]}  P={r[2]}%  HR={r[3]}')

print()
print('='*70)
print('【2】四态作为前缀，内部再按金银细分 —— 四态内部是否还有金银信息？')
print('='*70)
for sname, sm in [('升主龙',m_shengzhu),('降主虎',m_jiangzhu),('降转武',m_jiangzhuan),('升转雀',m_shengzhuan)]:
    print(f'\n--- {sname} 内部按金银细分 ---')
    for gname, gm in [('金',m_gold),('银',m_silver),('唏',m_xi),('嘘',m_xu),('尿',m_niao),('屎',m_shi)]:
        r = stat(sm & gm, f'{sname}+{gname}')
        if r: print(f'  {r[0]}: n={r[1]}  P={r[2]}%  HR={r[3]}')

print()
print('='*70)
print('【3】两种分类的"纯升主"对比 —— 金 vs 升主龙 谁更纯？')
print('='*70)
r1 = stat(m_gold, '金(全部)')
r2 = stat(m_shengzhu, '升主龙(全部)')
r3 = stat(m_gold & m_shengzhu, '金∩升主龙')
r4 = stat(m_silver & m_shengzhu, '银∩升主龙')
r5 = stat(m_xi & m_shengzhu, '唏∩升主龙')
for r in [r1,r2,r3,r4,r5]:
    if r: print(f'  {r[0]}: n={r[1]}  P={r[2]}%  HR={r[3]}')
