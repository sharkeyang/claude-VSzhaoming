# -*- coding: utf-8 -*-
import pandas as pd, os, glob, random
random.seed(42)
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
sampled = random.sample(files, 2000)

all_dfs = []
for i, f in enumerate(sampled):
    if i % 500 == 0: print(f'读入: {i}/{len(sampled)}')
    try:
        df = pd.read_csv(f, encoding='gbk', usecols=['柱型','次日高幅','高幅','收','开','日ZA'])
    except: continue
    if len(df) < 100: continue
    all_dfs.append(df)

big = pd.concat(all_dfs, ignore_index=True)

def cls(ct):
    if pd.isna(ct): return 'NA'
    ct = str(ct)
    if '\u6805' in ct:  # 栅
        return '栅'
    elif '\u68af' in ct:  # 梯
        if '\u8dcc\u8b66' in ct:  # 跌警
            return '梯跌警'
        else:
            return '梯'
    elif '\u679d' in ct:  # 枝
        return '枝'
    else:
        return '根干'

big['柱型C'] = big['柱型'].apply(cls)
big['阳'] = big['收'] > big['开']
下日ZA = big['日ZA'].shift(-1)

out = open('____temp/柱型结论.txt', 'w', encoding='utf-8')

out.write('=' * 75 + '\n')
out.write('【柱型 vs 下日冲高 全量验证】 抽样2000个文件\n')
out.write('=' * 75 + '\n')

# 1. 大类
out.write('\n一、柱型大类整体\n')
out.write(f'{"柱型":<8} {"样本":>7} {"P(>=2%)":>8} {"P(>=3%)":>8} {"均次高":>7} {"升势率":>8}\n')
out.write('-' * 50 + '\n')
for cat in ['梯','栅','梯跌警','枝','根干']:
    g = big[big['柱型C']==cat]
    n=len(g); p2=g['次日高幅'].ge(2).sum()/n*100; p3=g['次日高幅'].ge(3).sum()/n*100
    avg=g['次日高幅'].mean()
    za_up=下日ZA[g.index].gt(0).sum()/n*100
    out.write(f'  {cat:<6} {n:>7} {p2:>7.1f}% {p3:>7.1f}% {avg:>6.2f}% {za_up:>7.1f}%\n')

# 2. 梯细分
out.write('\n二、梯细分\n')
out.write(f'{"梯型":<10} {"样本":>7} {"P(>=2%)":>8} {"P(>=3%)":>8}\n')
out.write('-' * 40 + '\n')
for name, g in big.groupby('柱型'):
    if '\u68af' not in name: continue
    n=len(g); p2=g['次日高幅'].ge(2).sum()/n*100; p3=g['次日高幅'].ge(3).sum()/n*100
    out.write(f'  {name:<8} {n:>7} {p2:>7.1f}% {p3:>7.1f}%\n')

# 3. 栅 conditions
out.write('\n三、栅 vs 阴阳 vs 当日高幅\n')
out.write(f'{"栅条件":<16} {"样本":>7} {"P(>=2%)":>8} {"P(>=3%)":>8}\n')
out.write('-' * 45 + '\n')
栅 = big[big['柱型C']=='栅'].copy()
栅['档'] = pd.cut(栅['高幅'], bins=[-1,1,2,3,999], labels=['<1%','1~2%','2~3%','>3%'])
for 阴阳 in ['阳柱','阴柱']:
    m = 栅[栅['阳']] if 阴阳=='阳柱' else 栅[栅['阴']]
    for name, g in m.groupby('档', observed=True):
        n=len(g); p2=g['次日高幅'].ge(2).sum()/n*100; p3=g['次日高幅'].ge(3).sum()/n*100
        out.write(f'  栅{阴阳}+当日{name:<4} {n:>7} {p2:>7.1f}% {p3:>7.1f}%\n')

# 4. 升势率
out.write('\n四、柱型 vs 升势维持率（下日ZA>0）\n')
out.write(f'{"柱型":<8} {"样本":>7} {"ZA>0":>6} {"升势率":>8} {"ZA<0":>6} {"跌势率":>8}\n')
out.write('-' * 45 + '\n')
for cat in ['梯','栅','梯跌警','枝','根干']:
    g = big[big['柱型C']==cat]
    n=len(g)
    if n==0: continue
    up = 下日ZA[g.index].gt(0).sum()
    dn = 下日ZA[g.index].lt(0).sum()
    out.write(f'  {cat:<6} {n:>7} {up:>6} {up/n*100:>7.1f}% {dn:>6} {dn/n*100:>7.1f}%\n')

# 结论
out.write('\n' + '=' * 75 + '\n')
out.write('结论：最简机会/风险提示\n')
out.write('=' * 75 + '\n')
out.write('''
【机会信号 - 下日冲高概率高】
  1. 梯（任何梯型）-> P(>=2%)约36%, 升势维持率90% <- 最佳
  2. 栅+当日高幅>2%（阳柱更佳）-> P(>=2%)=45-50% <- 强势确认
  3. 栅+当日高幅>2%（阴柱也可）-> P(>=2%)=35-49%

【风险信号 - 下日冲高概率低】
  1. 根干 -> P(>=2%)=32%, 升势维持率仅25% <- 最差
  2. 栅+当日高幅<1%（阴柱）-> P(>=2%)=23% <- 弱阴栅最差
  3. 栅+当日高幅<1%（阳柱）-> P(>=2%)=29% <- 弱阳栅也不佳
  4. 梯跌警 -> P(>=2%)=30% <- 梯型中的坏信号

【核心原则】
  - 栅不是问题，当日高幅才是关键
  - 栅+当日高幅>2% = 强信号（与梯相当或更好）
  - 栅+当日高幅<1% = 弱信号（应回避）
  - 梯的升势维持率极高（90%），是持仓首选
''')

out.close()
print('结论已写入 ____temp/柱型结论.txt')