# -*- coding: utf-8 -*-
"""重新验证 §6.12.0.5 与 5.3.3 位置决策表相互印证
验证操盘核心 vs 5.3.3 位置决策表的 P(≥3%)
"""
import io, os, glob, sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 列映射
# col8=DXCD, col9=DXAB, col13=日ZA, col14=日ZC, col19=BSHA, col26=次日高幅, col44=BT连阳(等型)
# 护型: DXAB第1字符 (a=甲, b=乙, r=己, y=戊, c=丙, d=丁)

stats = defaultdict(lambda: {'n': 0, 'p3': 0, 'h2': 0, 'sum_nh': 0})

def add(label, nh, h2):
    st = stats[label]
    st['n'] += 1
    if nh >= 3:
        st['p3'] += 1
    if nh >= 2:
        st['h2'] += 1
    st['sum_nh'] += nh

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 45:
                continue
            try:
                cd = row[8]
                ab = row[9]
                za = int(row[13])
                zc = int(row[14])
                bsha = float(row[19])
                nh = float(row[26])
                deng = row[44]  # BT连阳(等型)
            except:
                continue
            # 护型第1字符
            hx = ab[0] if ab else ''
            # DXAB>0 = 正交箭头 ↗
            is_zhenjiao = '↗' in ab and cd in ('上', '忐')
            # 等型: 等1/等2/等3/等5
            # BT连阳列格式复杂，用日ZA判断等型
            # 等1=日ZA=1, 等2=日ZA=2, 等3=日ZA>=3, 等5=日ZA=-1
            if za == 1:
                deng_type = '等1'
            elif za == 2:
                deng_type = '等2'
            elif za >= 3:
                deng_type = '等3'
            elif za == -1:
                deng_type = '等5'
            else:
                deng_type = '其他'

            # 操盘核心 = DJC丘(DXZC>0) + 真正交(DXAB>0 + DXCD上/忐) + DJA丘(日ZA>0)
            is_djc = zc > 0
            is_zhenjiao = '↗' in ab and cd in ('上', '忐')
            is_dja = za > 0
            is_caopan = is_djc and is_zhenjiao and is_dja

            if is_caopan:
                add('操盘核心', nh, nh)
                if deng_type == '等1':
                    add('操盘核心+等1', nh, nh)
                elif deng_type == '等3':
                    add('操盘核心+等3', nh, nh)
                if bsha >= 5:
                    add('操盘核心+BSHA5', nh, nh)
                else:
                    add('操盘核心+BSHA<5', nh, nh)
                if deng_type == '等1' and bsha >= 5:
                    add('操盘核心等1+BSHA5', nh, nh)
                elif deng_type == '等1' and bsha < 5:
                    add('操盘核心等1+BSHA<5', nh, nh)

            # 5.3.3 位置决策表
            if zc > 0 and hx == 'a':  # ZC>0 + 甲
                if deng_type == '等1':
                    add('5.3.3等1+ZC>0+甲', nh, nh)
                elif deng_type == '等3':
                    add('5.3.3等3+ZC>0+甲', nh, nh)
            if zc > 0 and hx in ('a', 'b', 'r'):  # ZC>0 + 甲乙己
                if deng_type == '等1':
                    add('5.3.3等1+ZC>0+甲乙己', nh, nh)

            # 等5 超跌反弹
            if deng_type == '等5' and zc > 0 and hx == 'b':  # 等5+ZC>0+乙
                if bsha >= 5:
                    add('等5+ZC>0+乙+BSHA5', nh, nh)
                else:
                    add('等5+ZC>0+乙+BSHA<5', nh, nh)

print('\n=== 操盘核心 vs 5.3.3 位置决策表 P(≥3%) ===')
for label in ('操盘核心', '操盘核心+等1', '操盘核心+等3',
              '5.3.3等1+ZC>0+甲', '5.3.3等3+ZC>0+甲', '5.3.3等1+ZC>0+甲乙己',
              '操盘核心+BSHA5', '操盘核心+BSHA<5', '操盘核心等1+BSHA5', '操盘核心等1+BSHA<5',
              '等5+ZC>0+乙+BSHA5', '等5+ZC>0+乙+BSHA<5'):
    st = stats[label]
    if st['n'] == 0:
        continue
    print(f'{label}: n={st["n"]}, H2%={st["h2"]/st["n"]*100:.1f}%, P3%={st["p3"]/st["n"]*100:.1f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')