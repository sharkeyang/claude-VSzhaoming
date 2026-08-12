# -*- coding: utf-8 -*-
"""
周波型 + 周级别等高线 = 下周冲高预测
"""
import pandas as pd, os, glob, random, warnings
warnings.simplefilter('ignore')
random.seed(42)

WK_DIR = 'D:\\@VSwork\\VS昭明计划VBA优化\\昭明算展\\谕组周'
wfiles = sorted(glob.glob(os.path.join(WK_DIR, '谕组周_*.csv')))
sampled = random.sample(wfiles, 3000)

out = open('D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\周波型分析.txt','w',encoding='utf-8')

def rep(name, g, n_min=200):
    n=len(g)
    if n<n_min: return
    hr=g['HR'].mean()
    p2=(g['HR']>=2).mean()*100
    p3=(g['HR']>=3).mean()*100
    nh2=(g['下周HR']>=2).mean()*100
    nh3=(g['下周HR']>=3).mean()*100
    nhr=g['下周HR'].mean()
    out.write(f'{name:<50} n={n:>5} 当周均幅={hr:>5.2f}% 下周均幅={nhr:>5.2f}% 下周P2={nh2:>5.1f}% 下周P3={nh3:>5.1f}%\n')

dfs = []
for idx, f in enumerate(sampled):
    try:
        df = pd.read_csv(f, encoding='gbk')
        df.columns = ['日期','收','PR','HR','WXAB','波型','柱型','盈提示','WXCD','ZA级','ZB级','ZC级','涨幅','周级']
        if len(df) >= 20:
            df['fid'] = idx  # 每文件独立ID，用于shift
            dfs.append(df)
    except: continue
wk = pd.concat(dfs, ignore_index=True)

# 下周HR（每文件内shift）
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
# 分组
wk['ZC+'] = wk['ZC级'] > 0
wk['ZB+'] = wk['ZB级'] > 0
wk['ZA+'] = wk['ZA级'] > 0

out.write(f'周线样本: {len(wk)}行\n')
out.write('='*70+'\n')
out.write('一、周波型 整体 下周冲高率\n')
out.write('='*70+'\n')
out.write(f'{"波型":<50} {"样本":>6} {"下周P2":>8} {"下周P3":>8} {"下周均幅":>8} {"当周均幅":>8}\n{"-"*80}\n')

# 提取主要波型类型
for pat in ['Aa龙猪','Be龙管根','Fe震正根','De头正根','Ff震负','Fa震正〇','Dd头正芽','Df头负']:
    m = wk['波型'].str.contains(pat, na=False, regex=False)
    if m.sum() >= 200:
        rep(f'周波型={pat}', wk[m])

out.write('\n'+'='*70+'\n')
out.write('二、周波型 × 站上WJC 下周冲高率\n')
out.write('='*70+'\n')
out.write(f'{"条件":<50} {"样本":>6} {"下周P2":>8} {"下周P3":>8} {"下周均幅":>8}\n{"-"*80}\n')
for pat in ['Aa龙猪','Be龙管根','Fe震正根']:
    for label, cond in [('站上WJC', wk['ZC+']), ('WJC之下', ~wk['ZC+'])]:
        m = wk['波型'].str.contains(pat, na=False, regex=False) & cond
        if m.sum() >= 200:
            g = wk[m]
            n=len(g); nh2=(g['下周HR']>=2).mean()*100; nh3=(g['下周HR']>=3).mean()*100
            out.write(f'周{pat}+{label:<12} n={n:>5} 下周P2={nh2:>5.1f}% 下周P3={nh3:>5.1f}% 下周均幅={g["下周HR"].mean():.2f}%\n')

out.write('\n'+'='*70+'\n')
out.write('三、周波型 + 等高线(周级别ZC级作为代理) 下周冲高率\n')
out.write('='*70+'\n')
out.write(f'{"条件":<50} {"样本":>6} {"下周P2":>8} {"下周P3":>8} {"下周均幅":>8}\n{"-"*80}\n')
# ZC级分档模拟等高线
def zc_level(v):
    if v > 0: return 'ZC>0(站上WJC)'
    elif v == -1: return 'ZC=-1(刚跌破)'
    else: return 'ZC<=-2(深跌)'
wk['ZC档'] = wk['ZC级'].apply(zc_level)
for pat in ['Aa龙猪','Be龙管根','Fe震正根']:
    for zc_label in ['ZC>0(站上WJC)', 'ZC=-1(刚跌破)', 'ZC<=-2(深跌)']:
        m = wk['波型'].str.contains(pat, na=False, regex=False) & (wk['ZC档']==zc_label)
        if m.sum() >= 200:
            g = wk[m]
            n=len(g); nh2=(g['下周HR']>=2).mean()*100; nh3=(g['下周HR']>=3).mean()*100
            out.write(f'周{pat}+{zc_label:<20} n={n:>5} 下周P2={nh2:>5.1f}% 下周P3={nh3:>5.1f}% 下周均幅={g["下周HR"].mean():.2f}%\n')

out.write('\n'+'='*70+'\n')
out.write('四、周波型 × 柱型 组合\n')
out.write('='*70+'\n')
out.write(f'{"条件":<50} {"样本":>6} {"下周P2":>8} {"下周P3":>8} {"下周均幅":>8}\n{"-"*80}\n')
for bx in ['Aa龙猪','Be龙管根']:
    m1 = wk['波型'].str.contains(bx, na=False, regex=False)
    sub = wk[m1]
    for zx in ['梯','栅','枝','根']:
        m2 = sub['柱型'].str.contains(zx, na=False, regex=False)
        if m2.sum() >= 200:
            g = sub[m2]
            n=len(g); nh2=(g['下周HR']>=2).mean()*100; nh3=(g['下周HR']>=3).mean()*100
            out.write(f'周{bx}+柱{zx:<6} n={n:>5} 下周P2={nh2:>5.1f}% 下周P3={nh3:>5.1f}% 下周均幅={g["下周HR"]:.2f}%\n')

out.write('\n'+'='*70+'\n')
out.write('五、最佳组合排序\n')
out.write('='*70+'\n')
# 收集所有组合
cands = []
for v in ['波型','WXCD','ZA级','ZB级','ZC级']:
    if v not in wk.columns: continue
    g = wk.groupby(v, dropna=True).agg(n=('下周HR','count'), p3=('下周HR', lambda x:(x>=3).mean()), p2=('下周HR', lambda x:(x>=2).mean()))
    for idx, r in g.iterrows():
        if r['n']>=500:
            cands.append((v, str(idx), r['n'], r['p2']*100, r['p3']*100))
cands.sort(key=lambda x: -x[3])
out.write('下周P2最高TOP 15：\n')
for v, val, n, p2, p3 in cands[:15]:
    out.write(f'  {v}={val:<20} n={n:>5} 下周P2={p2:>5.1f}% 下周P3={p3:>5.1f}%\n')
out.write('\n下周P2最低TOP 12：\n')
cands.sort(key=lambda x: x[3])
for v, val, n, p2, p3 in cands[:12]:
    out.write(f'  {v}={val:<20} n={n:>5} 下周P2={p2:>5.1f}% 下周P3={p3:>5.1f}%\n')

out.close()
print('完成')