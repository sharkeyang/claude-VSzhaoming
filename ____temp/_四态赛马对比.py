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

# 地型（从地型周列[5]读取，格式 0橅，2026-10-15 重导后周策略P3不再含地型）
wk['地型'] = wk['地型周'].astype(str)

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

# 等类（ZA分段，与P1一致）
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & wk['末位'].isin(['C','D','E','F'])
m3 = (wk['ZA周'] >= 2) & wk['末位'].isin(['A','B'])
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & wk['末位'].isin(['A','B','C','D'])
m7 = (wk['ZA周'] <= -2) & wk['末位'].isin(['E','F'])
eqs = [('等1',m1),('等2',m2),('等3',m3),('等5',m5),('等6',m6),('等7',m7)]

# 柱排（用startswith，contains会把(升)人误判为升排，2026-10-16修正）
m_up = wk['柱排周'].str.startswith('升')
m_dn = wk['柱排周'].str.startswith('跌')
m_ren = ~(m_up | m_dn)
zp = [('升排',m_up),('人排',m_ren),('跌排',m_dn)]

# 地型列表
dx_pos = ['0橅','1柜','2栅','3桮']
dx_neg = ['6娝','7姗','8姖','9妩']

def 赛马(prefix_masks, title, min_n=1000):
    """跑赛马：前缀×等类×柱排×地型，生成策略编码，按平均周涨排序"""
    results = []
    for pname, pm in prefix_masks:
        for ename, em in eqs:
            for zpname, zpm in zp:
                # 地型按ZA正负分
                if '等1' in ename or '等2' in ename or '等3' in ename:
                    dx_list = dx_pos
                else:
                    dx_list = dx_neg
                for d in dx_list:
                    mask = pm & em & zpm & (wk['地型']==d)
                    n = mask.sum()
                    if n < min_n: continue
                    g = wk.loc[mask]
                    avg = g['周涨'].mean()
                    p3 = (g['下周HR']>=1).mean()*100
                    results.append((avg, p3, f'{pname}+{ename}+{zpname}+{d}', n))
    results.sort(reverse=True)
    print(f'\n{"="*60}')
    print(f'【{title}】')
    print(f'{"="*60}')
    print(f'  组合数: {len(results)}')
    if not results: return
    print(f'  最优5(按平均周涨):')
    for avg, p3, name, n in results[:5]:
        print(f'    {name}: 周涨={avg:.3f}%  P3={p3:.1f}%  n={n}')
    print(f'  最差5:')
    for avg, p3, name, n in results[-5:]:
        print(f'    {name}: 周涨={avg:.3f}%  P3={p3:.1f}%  n={n}')
    avgs = [r[0] for r in results]
    print(f'  极差(周涨): {max(avgs)-min(avgs):.3f}pp')
    return results

print('总行数:', len(wk))
赛马(jy, '方案A：金银前缀（现状）')
赛马(st, '方案B：四态前缀（改写）')
叠加 = [(f'{jn}+{sn}', jm & sm) for jn, jm in jy for sn, sm in st]
赛马(叠加, '方案C：四态×金银叠加')
