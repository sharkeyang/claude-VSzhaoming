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
jy = [('金',m_gold),('银',m_silver),('唏',m_xi),('嘘',m_xu),('尿',m_niao),('屎',m_shi)]

# 四态
m_shengzhu = (wk['WXAB']>0) & (wk['WXZB']>0)
m_jiangzhu = (wk['WXAB']<0) & (wk['WXZB']<0)
m_jiangzhuan = (wk['WXAB']<0) & (wk['WXZB']>0)
m_shengzhuan = (wk['WXAB']>0) & (wk['WXZB']<0)
st = [('升主龙',m_shengzhu),('降主虎',m_jiangzhu),('降转武',m_jiangzhuan),('升转雀',m_shengzhuan)]

# 下游条件：等类+柱排（控制变量）
def 等类(mask):
    return mask
# 用 ZA 分段作为等类近似（与P1脚本一致）
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & wk['末位'].isin(['C','D','E','F'])
m3 = (wk['ZA周'] >= 2) & wk['末位'].isin(['A','B'])
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & wk['末位'].isin(['A','B','C','D'])
m7 = (wk['ZA周'] <= -2) & wk['末位'].isin(['E','F'])
eqs = [('等1',m1),('等2',m2),('等3',m3),('等5',m5),('等6',m6),('等7',m7)]

def p3(mask):
    n = mask.sum()
    if n < 1000: return None
    g = wk.loc[mask]
    return round((g['下周HR']>=1).mean()*100,1)

def 报告(prefix_name, prefix_masks, title):
    print(f'\n{"="*60}')
    print(f'【{title}】')
    print(f'{"="*60}')
    # 每个前缀 × 每个等类
    all_p = []
    for pname, pm in prefix_masks:
        for ename, em in eqs:
            p = p3(pm & em)
            if p is not None:
                all_p.append((p, f'{pname}+{ename}'))
    if not all_p:
        print('  无有效组合')
        return
    all_p.sort(reverse=True)
    top = all_p[0][0]
    bot = all_p[-1][0]
    print(f'  组合数: {len(all_p)}')
    print(f'  最高P: {top}%  ({all_p[0][1]})')
    print(f'  最低P: {bot}%  ({all_p[-1][1]})')
    print(f'  极差: {top-bot:.1f}pp')
    print(f'  前5: {[f"{p}%({n})" for p,n in all_p[:5]]}')
    print(f'  后5: {[f"{p}%({n})" for p,n in all_p[-5:]]}')
    return top, bot

print('总行数:', len(wk))
报告('金银', jy, '方案A：仅金银分类（6前缀）')
报告('四态', st, '方案B：仅四态分类（4前缀）')
# 叠加：金银×四态
叠加 = [(f'{jn}+{sn}', jm & sm) for jn, jm in jy for sn, sm in st]
报告('叠加', 叠加, '方案C：金银×四态叠加（24组合）')
