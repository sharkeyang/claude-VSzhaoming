# -*- coding: utf-8 -*-
"""
周级别最后一柱特征 全量数据验证
验证6.1~6.5中各特征对下周HR>=3%的预测力
"""
import pandas as pd, os, glob, random, warnings
warnings.simplefilter('ignore')
random.seed(42)

WK_DIR = 'D:\\@VSwork\\VS昭明计划VBA优化\\昭明算展\\谕组周'
wfiles = sorted(glob.glob(os.path.join(WK_DIR, '谕组周_*.csv')))
sampled = random.sample(wfiles, min(1500, len(wfiles)))

dfs = []
for i, f in enumerate(sampled):
    if i % 500 == 0: print(f'读入: {i}/{len(sampled)}', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) >= 10:
            df['fid'] = i
            dfs.append(df)
    except: continue
wk = pd.concat(dfs, ignore_index=True)
print(f'总行: {len(wk)}', flush=True)

# 列定位（按位置）
# 0:主期, 1:周涨, 2:PR, 3:HR, 4:WXAB, 5:波型, 6:柱排周
# 7:柱型, 8:层界, 9:?, 10:?, 11:?, 12:?, 13:WXCD
# 14:ZA周, 15:ZB周, 16:ZC周

wk = wk.rename(columns={
    wk.columns[1]: '周涨', wk.columns[2]: 'PR', wk.columns[3]: 'HR',
    wk.columns[5]: '波型', wk.columns[6]: '柱排周',
    wk.columns[14]: 'ZA周', wk.columns[15]: 'ZB周', wk.columns[16]: 'ZC周'
})
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['下下周HR'] = wk.groupby('fid')['HR'].shift(-2)

out = open('D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\周最后一柱验证.txt', 'w', encoding='utf-8')

def rep(name, mask, n_min=100):
    g = wk[mask]
    n = len(g)
    if n < n_min: return
    nh3 = (g['下周HR'] >= 3).mean() * 100
    nh2 = (g['下周HR'] >= 2).mean() * 100
    nhr = g['下周HR'].mean()
    n3w = (g['下下周HR'] >= 3).mean() * 100 if '下下周HR' in g else 0
    out.write(name.ljust(35) + ' n=' + str(n).rjust(5) + ' 下周P3=' + format(nh3, '.1f') + '% P2=' + format(nh2, '.1f') + '% 均幅=' + format(nhr, '.2f') + '%\n')
    return nh3

out.write('='*65+'\n')
out.write('周级别最后一柱特征 全量验证\n')
out.write('='*65+'\n\n')

# 0. 基线
out.write('基线：\n')
rep('全部样本', slice(None), 500)

# 1. 跌吞（阴吞前阳）
out.write('\n一、跌吞\n')
m = wk['柱排周'].str.contains('吞吞', na=False, regex=False)
rep('柱排含吞吞', m)
rep('柱排含吞吞+跌尾', m & wk['柱排周'].str.contains('跌', na=False))
rep('柱排含吞吞+升尾', m & wk['柱排周'].str.contains('升', na=False))

# 2. 上影线小柱（PR小但HR大）
out.write('\n二、上影线小柱（PR小+HR大）\n')
wk['上影比'] = wk['PR'].abs() / wk['HR'].replace(0, 0.01)
m_small = (wk['PR'].abs() < 2) & (wk['HR'] > 3)  # PR<2%但HR>3%
rep('上影线小柱(PR<2%+HR>3%)', m_small)
# 细分：连阳后
m_ly = wk['柱排周'].str.contains('升.尾连', na=False, regex=False)
rep('连阳后+上影线小柱', m_small & m_ly)

# 3. 连阳3+转阴
out.write('\n三、连阳3+转阴\n')
# 当前周是升尾连，但下周柱排转跌
m_ly3 = wk['柱排周'].str.contains('升.尾连', na=False, regex=False)
wk['下周柱排周'] = wk.groupby('fid')['柱排周'].shift(-1)
m_ly3toD = m_ly3 & wk['下周柱排周'].str.contains('跌', na=False, regex=False)
rep('连阳3+转阴', m_ly3toD)
# 连阳后转阴但未跌（连阳转平）
m_ly3toP = m_ly3 & wk['下周柱排周'].str.contains('升|人', na=False, regex=False)
rep('连阳3+续阳', m_ly3 & ~m_ly3toD, 100)

# 4. 连阳3+十字星（PR接近0）
out.write('\n四、连阳3+十字星\n')
m_cross = (wk['PR'].abs() < 0.5) & (wk['HR'] > 1)
rep('十字星(PR<0.5%+HR>1%)', m_cross)
rep('连阳3+十字星', m_cross & m_ly3)

# 5. 连阳逐步缩小（多周连阳递增衰减 - 需要前几周PR对比）
out.write('\n五、连阳逐步缩小\n')
# 用前一周PR和本周PR对比
wk['上周PR'] = wk.groupby('fid')['PR'].shift(1)
m_shrink = m_ly3 & (wk['PR'] < wk['上周PR']) & (wk['PR'] > 0)  # 本周阳柱小于上周
rep('连阳逐步缩小(阳柱递减)', m_shrink)

# 6. 连阳3+巨阳
out.write('\n六、连阳3+巨阳\n')
m_giant10 = wk['HR'] >= 10
m_giant20 = wk['HR'] >= 20
rep('连阳3+巨阳>10%', m_ly3 & m_giant10)
rep('连阳3+巨阳>20%', m_ly3 & m_giant20)

# 7. 升排+长上影
out.write('\n七、升排+长上影\n')
# 波型含龙猪/震正等（升排）+ HR>>PR（上影线长）
m_lz = wk['波型'].str.contains('Aa龙猪|Fe震正|Fd震正', na=False, regex=False)
m_long_shadow = (wk['HR'] - wk['PR'].abs()) > 3  # 上影线>3%
rep('升排+长上影', m_lz & m_long_shadow)

# 8. 升排+柱体缩小
out.write('\n八、升排+柱体缩小\n')
m_body_shrink = m_lz & (wk['PR'] < wk['上周PR']) & (wk['PR'] > 0)
rep('升排+柱体缩小', m_body_shrink)

# 9. 升排+ZA下降
out.write('\n九、升排+ZA下降\n')
wk['上周ZA'] = wk.groupby('fid')['ZA周'].shift(1)
m_za_down = m_lz & (wk['ZA周'] < wk['上周ZA'])
rep('升排+ZA下降', m_za_down)

# 10. 连阳后长上影/长下影
out.write('\n十、连阳后的特殊形态\n')
m_lz_up = wk['柱排周'].str.contains('升', na=False, regex=False)
rep('连阳+长上影(HR-PR>3)', m_lz_up & ((wk['HR']-wk['PR'].abs())>3))
rep('连阳+长下影(PR<0+HR>3)', m_lz_up & (wk['PR']<0) & (wk['HR']>3))

# 11. 对比汇总
out.write('\n' + '='*65 + '\n')
out.write('对比汇总（按下周P3降序）\n')
out.write('='*65 + '\n')

all_results = []
for label, mask in [
    ('全部样本基线', slice(None)),
    ('连阳3+巨阳>20%', m_ly3 & m_giant20),
    ('连阳3+巨阳>10%', m_ly3 & m_giant10),
    ('连阳3+续阳', m_ly3 & ~m_ly3toD),
    ('连阳+长上影', m_lz_up & ((wk['HR']-wk['PR'].abs())>3)),
    ('升排+ZA下降', m_za_down),
    ('柱排含吞吞', m),
    ('连阳逐步缩小', m_shrink),
    ('连阳3+十字星', m_cross & m_ly3),
    ('上影线小柱', m_small),
    ('连阳3+转阴', m_ly3toD),
    ('升排+长上影', m_lz & m_long_shadow),
    ('升排+柱体缩小', m_body_shrink),
]:
    p3 = rep(label, mask, 30)
    if p3 is not None:
        all_results.append((p3, label))

all_results.sort(key=lambda x: -x[0])
for p3, label in all_results:
    out.write(f'  {p3:>5.1f}%  {label}\n')

out.close()
print('完成')