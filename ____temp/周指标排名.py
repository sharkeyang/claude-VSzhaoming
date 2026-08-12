# -*- coding: utf-8 -*-
"""周类指标 下周冲高预测力 综合排名"""
import pandas as pd, os, glob, random, warnings
warnings.simplefilter('ignore')
random.seed(42)

WK_DIR = 'D:\\@VSwork\\VS昭明计划VBA优化\\昭明算展\\谕组周'
wfiles = sorted(glob.glob(os.path.join(WK_DIR, '谕组周_*.csv')))
print(f'文件: {len(wfiles)}', flush=True)

dfs = []
for i, f in enumerate(wfiles):
    if i % 800 == 0: print(f' 读入: {i}/{len(wfiles)}', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) >= 10:
            df['fid'] = i
            dfs.append(df)
    except: continue
wk = pd.concat(dfs, ignore_index=True)
print(f'总行: {len(wk)}', flush=True)

wk = wk.rename(columns={
    wk.columns[1]: '周涨', wk.columns[2]: 'PR', wk.columns[3]: 'HR',
    wk.columns[4]: 'WXAB', wk.columns[5]: '波型', wk.columns[6]: '柱排周',
    wk.columns[13]: 'WXCD', wk.columns[14]: 'ZA周', wk.columns[15]: 'ZB周',
    wk.columns[16]: 'ZC周', wk.columns[17]: 'ZD周'
})
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)

def q(wx):
    if pd.isna(wx): return 'X'
    s = str(wx)
    if len(s) >= 2: return s[1]
    return 'X'
wk['护型'] = wk['WXAB'].apply(q)
wk = wk[wk['护型'] != 'X']

out = open('D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\周指标排名.txt', 'w', encoding='utf-8')

# 计算某指标内各分类的P3
def get_p3(mask):
    g = wk[mask]
    n = len(g)
    if n < 500: return None
    return (g['下周HR'] >= 3).mean() * 100

# 各指标的分类列表
indicators = {
    'WXCD(宏观)': [('金银', '金升|银升'),
                   ('唏待', '唏待'),
                   ('尿嘘降', '尿降|嘘降'),
                   ('屎降', '屎降')],
    'WXAB(中观)': [('甲', None), ('乙', None), ('己', None),
                   ('丙', None), ('丁', None), ('戊', None)],
    '周波型': [('Aa龙猪', 'Aa龙猪'), ('Dd头正芽', 'Dd头正芽'),
               ('Fd震正芽', 'Fd震正芽'), ('Ff震负', 'Ff震负'),
               ('Be龙管根', 'Be龙管根'), ('Fe震正根', 'Fe震正根'),
               ('De头正根', 'De头正根'), ('Df头负', 'Df头负'),
               ('Fa震正〇', 'Fa震正〇')],
    '周柱排': [('升.尾连', '升.尾连'), ('升.尾吞', '升.尾吞'),
               ('升.尾反孕', '升.尾反孕'), ('跌.尾连', '跌.尾连'),
               ('跌.尾吞', '跌.尾吞'), ('(人)人.吞吞', '(人)人.吞吞')],
    '周等型(ZA周)': [('ZA>3', 'gt3'), ('ZA=2~3', '2to3'), ('ZA=1', 'eq1'),
                     ('ZA=-1', 'eqn1'), ('ZA=-2~-3', 'n2to3'), ('ZA<-3', 'ltn3')],
    '站上WJC(ZC周)': [('ZC>0', 'zcpos'), ('ZC<=0', 'zcnpos')],
}

out.write('='*70+'\n')
out.write('周类指标 下周冲高预测力 综合排名\n')
out.write('='*70+'\n\n')

# 收集各指标区分度
results = []
for ind_name, cats in indicators.items():
    vals = []
    for label, pat in cats:
        if ind_name == 'WXCD(宏观)':
            m = wk['WXCD'].str.contains(pat, na=False, regex=True)
        elif ind_name == 'WXAB(中观)':
            m = wk['护型'] == label
        elif ind_name == '周波型':
            m = wk['波型'].str.contains(pat, na=False, regex=False)
        elif ind_name == '周柱排':
            m = wk['柱排周'].str.contains(pat, na=False, regex=False)
        elif ind_name == '周等型(ZA周)':
            if pat == 'gt3': m = wk['ZA周'] > 3
            elif pat == '2to3': m = (wk['ZA周'] >= 2) & (wk['ZA周'] <= 3)
            elif pat == 'eq1': m = wk['ZA周'] == 1
            elif pat == 'eqn1': m = wk['ZA周'] == -1
            elif pat == 'n2to3': m = (wk['ZA周'] >= -3) & (wk['ZA周'] <= -2)
            elif pat == 'ltn3': m = wk['ZA周'] < -3
        elif ind_name == '站上WJC(ZC周)':
            if pat == 'zcpos': m = wk['ZC周'] > 0
            else: m = wk['ZC周'] <= 0
        p3 = get_p3(m)
        if p3 is not None:
            vals.append((label, p3))
    if vals:
        vals.sort(key=lambda x: -x[1])
        best = vals[0][1]
        worst = vals[-1][1]
        diff = best - worst
        results.append((ind_name, diff, best, worst, vals[0][0], vals[-1][0]))

# 输出排名
results.sort(key=lambda x: -x[1])
out.write('区分度排名（越大越有效）：\n\n')
out.write(f'{"指标":<16} {"区分度":>8} {"最佳":>6} {"最差":>6}\n')
out.write('-'*40+'\n')
for ind, diff, best, worst, bn, wn in results:
    out.write(f'{ind:<16} {diff:>7.1f}pp {bn}{best:.1f}%  {wn}{worst:.1f}%\n')

out.write('\n\n' + '='*70 + '\n')
out.write('各指标明细\n')
out.write('='*70 + '\n\n')

for ind_name, cats in indicators.items():
    out.write(f'\n【{ind_name}】\n')
    vals = []
    for label, pat in cats:
        if ind_name == 'WXCD(宏观)':
            m = wk['WXCD'].str.contains(pat, na=False, regex=True)
        elif ind_name == 'WXAB(中观)':
            m = wk['护型'] == label
        elif ind_name == '周波型':
            m = wk['波型'].str.contains(pat, na=False, regex=False)
        elif ind_name == '周柱排':
            m = wk['柱排周'].str.contains(pat, na=False, regex=False)
        elif ind_name == '周等型(ZA周)':
            if pat == 'gt3': m = wk['ZA周'] > 3
            elif pat == '2to3': m = (wk['ZA周'] >= 2) & (wk['ZA周'] <= 3)
            elif pat == 'eq1': m = wk['ZA周'] == 1
            elif pat == 'eqn1': m = wk['ZA周'] == -1
            elif pat == 'n2to3': m = (wk['ZA周'] >= -3) & (wk['ZA周'] <= -2)
            elif pat == 'ltn3': m = wk['ZA周'] < -3
        elif ind_name == '站上WJC(ZC周)':
            if pat == 'zcpos': m = wk['ZC周'] > 0
            else: m = wk['ZC周'] <= 0
        p3 = get_p3(m)
        if p3 is not None:
            n = m.sum()
            vals.append((label, p3, n))
    vals.sort(key=lambda x: -x[1])
    for label, p3, n in vals:
        out.write(f'  {label:<12} 下周P3={p3:>5.1f}%  n={n:>6}\n')

out.close()
print('完成')