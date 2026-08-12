# -*- coding: utf-8 -*-
"""MC3.1_研究周趋势微观指标 全量(2644只)统计重跑"""
import pandas as pd, os, glob, random, warnings
warnings.simplefilter('ignore')
random.seed(42)

WK_DIR = 'D:\\@VSwork\\VS昭明计划VBA优化\\昭明算展\\谕组周'
wfiles = sorted(glob.glob(os.path.join(WK_DIR, '谕组周_*.csv')))
print(f'文件数: {len(wfiles)}', flush=True)

dfs = []
for i, f in enumerate(wfiles):
    if i % 500 == 0: print(f' 读入: {i}/{len(wfiles)}', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) >= 10:
            df['fid'] = i
            dfs.append(df)
    except: continue
wk = pd.concat(dfs, ignore_index=True)
print(f'总行: {len(wk)}', flush=True)

# 列重命名（按位置）
wk = wk.rename(columns={
    wk.columns[1]: '周涨', wk.columns[2]: 'PR', wk.columns[3]: 'HR',
    wk.columns[5]: '波型', wk.columns[6]: '柱排周', wk.columns[13]: 'WXCD',
    wk.columns[14]: 'ZA周', wk.columns[15]: 'ZB周', wk.columns[16]: 'ZC周',
    wk.columns[4]: 'WXAB'
})
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)

out = open('D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\周全量统计_2644.txt', 'w', encoding='utf-8')
def rep(name, mask, n_min=500):
    g = wk[mask]
    n = len(g)
    if n < n_min: return
    p3 = (g['下周HR'] >= 3).mean() * 100
    p2 = (g['下周HR'] >= 2).mean() * 100
    avg = g['下周HR'].mean()
    out.write(name.ljust(35) + ' n=' + str(n).rjust(6) + ' 下周P2=' + format(p2, '.1f') + '% 下周P3=' + format(p3, '.1f') + '% 均幅=' + format(avg, '.2f') + '%\n')
    return p3

# ============ 1.1 框架数据验证 ============
out.write('='*65+'\n')
out.write('一、框架数据验证（各层级区分度）\n')
out.write('='*65+'\n\n')
out.write('基线：')
rep('全部样本', slice(None), 1000)

out.write('\n【宏观WXCD】\n')
for wx in ['金升','银升','唏待','嘘降','屎降','尿降']:
    rep('WXCD-' + wx, wk['WXCD'].str.contains(wx, na=False, regex=False))

out.write('\n【中观WXAB】\n')
def q(wx):
    if pd.isna(wx): return 'X'
    s = str(wx)
    if len(s) >= 2: return s[1]
    return 'X'
wk['护型'] = wk['WXAB'].apply(q)
wk = wk[wk['护型'] != 'X']
for c in '甲乙丙丁戊己':
    rep('WXAB-' + c, wk['护型'] == c)

out.write('\n【微观波型】\n')
for pat in ['Aa龙猪','Be龙管根','Fe震正根','De头正根','Dd头正芽','Df头负','Fa震正〇','Ff震负','Fd震正芽']:
    m = wk['波型'].str.contains(pat, na=False, regex=False)
    if m.sum() >= 500:
        rep('波型-' + pat, m)

out.write('\n【微观柱排】\n')
for pat in ['升.尾连','升.尾吞','升.尾反孕','跌.尾连','跌.尾吞','(升)人.连后吞','(跌)人.连后吞','(人)人.吞吞','(人)人.孕孕']:
    m = wk['柱排周'].str.contains(pat, na=False, regex=False)
    if m.sum() >= 500:
        rep('柱排-' + pat, m)

# ============ 3.1 周等型 ============
out.write('\n' + '='*65 + '\n')
out.write('二、周等型（ZA周分级）\n')
out.write('='*65 + '\n\n')
rep('ZA周>0(站上WJA)', wk['ZA周'] > 0)
rep('ZA周<=0(跌破WJA)', wk['ZA周'] <= 0)
rep('ZA周=1(刚站上)', wk['ZA周'] == 1)
rep('ZA周=2~3', (wk['ZA周'] >= 2) & (wk['ZA周'] <= 3))
rep('ZA周>3', wk['ZA周'] > 3)
rep('ZA周=-1(刚跌破)', wk['ZA周'] == -1)
rep('ZA周=-2~-3', (wk['ZA周'] >= -3) & (wk['ZA周'] <= -2))
rep('ZA周<-3', wk['ZA周'] < -3)

# ============ CC WXCD+波型 ============
out.write('\n' + '='*65 + '\n')
out.write('三、WXCD+周波型\n')
out.write('='*65 + '\n\n')
for wx in ['金升','银升','唏待','嘘降','屎降','尿降']:
    m1 = wk['WXCD'].str.contains(wx, na=False, regex=False)
    if m1.sum() < 1000: continue
    for bx in ['Aa龙猪','Be龙管根','Fe震正根']:
        m2 = m1 & wk['波型'].str.contains(bx, na=False, regex=False)
        if m2.sum() >= 500:
            rep(wx + '+' + bx, m2)

out.close()
print('完成')