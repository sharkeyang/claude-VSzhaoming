# -*- coding: utf-8 -*-
"""镜面映射：在WXZB前提下，WXAB正负的增量效果（用户澄清）"""
import glob, pandas as pd, io, sys, math
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
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['后1周ZC'] = wk.groupby('fid')['ZC周'].shift(-1)
print(f'总样本: {len(wk):,}')
print()

def 报告(name, sub, 目标布尔):
    n = len(sub)
    if n < 100:
        print(f'  {name}: n={n} 样本不足')
        return
    p = 目标布尔.mean()*100
    se = math.sqrt(p/100*(1-p/100)/n)*100
    ci = 1.96*se
    print(f'  {name}: n={n:,}  概率={p:.1f}%  (±{ci:.1f}%)')
    return p

print('='*90)
print('猜想1：WXZC<0 + WXZB>0 前提下，WXAB>0 是否提高转正率？')
print('='*90)
s1 = wk[(wk['WXZC']<0)&(wk['WXZB']>0)&(wk['WXAB']>0)]
s2 = wk[(wk['WXZC']<0)&(wk['WXZB']>0)&(wk['WXAB']<0)]
p_ab_pos = 报告('WXZC<0+WXZB>0+WXAB>0', s1, s1['后1周ZC']>0)
p_ab_neg = 报告('WXZC<0+WXZB>0+WXAB<0', s2, s2['后1周ZC']>0)
if p_ab_pos and p_ab_neg:
    print(f'  → 差: {p_ab_pos-p_ab_neg:+.1f}pp')
print()

print('='*90)
print('猜想2：WXZC>0 + WXZB<0 前提下，WXAB<0 是否提高转负率？')
print('='*90)
s3 = wk[(wk['WXZC']>0)&(wk['WXZB']<0)&(wk['WXAB']<0)]
s4 = wk[(wk['WXZC']>0)&(wk['WXZB']<0)&(wk['WXAB']>0)]
p_ab_neg2 = 报告('WXZC>0+WXZB<0+WXAB<0', s3, s3['后1周ZC']<0)
p_ab_pos2 = 报告('WXZC>0+WXZB<0+WXAB>0', s4, s4['后1周ZC']<0)
if p_ab_neg2 and p_ab_pos2:
    print(f'  → 差: {p_ab_neg2-p_ab_pos2:+.1f}pp')
print()

print('='*90)
print('对照：WXZB 前提下的基线（不区分WXAB）')
print('='*90)
s5 = wk[(wk['WXZC']<0)&(wk['WXZB']>0)]
s6 = wk[(wk['WXZC']>0)&(wk['WXZB']<0)]
报告('WXZC<0+WXZB>0(全)', s5, s5['后1周ZC']>0)
报告('WXZC>0+WXZB<0(全)', s6, s6['后1周ZC']<0)
print()

print('='*90)
print('补充：WXZA 前提下，WXAB 正负的增量效果（对照）')
print('='*90)
s7 = wk[(wk['WXZC']<0)&(wk['WXZA']>0)&(wk['WXAB']>0)]
s8 = wk[(wk['WXZC']<0)&(wk['WXZA']>0)&(wk['WXAB']<0)]
s9 = wk[(wk['WXZC']>0)&(wk['WXZA']<0)&(wk['WXAB']<0)]
s10 = wk[(wk['WXZC']>0)&(wk['WXZA']<0)&(wk['WXAB']>0)]
报告('WXZC<0+WXZA>0+WXAB>0', s7, s7['后1周ZC']>0)
报告('WXZC<0+WXZA>0+WXAB<0', s8, s8['后1周ZC']>0)
报告('WXZC>0+WXZA<0+WXAB<0', s9, s9['后1周ZC']<0)
报告('WXZC>0+WXZA<0+WXAB>0', s10, s10['后1周ZC']<0)
