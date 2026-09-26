# -*- coding: utf-8 -*-
"""验证 §6.8 管宽哼JA(col23) 分类 + 各等型介入点数据
管宽哼JA = 脸哼JA[23] = (龟结哼/日类JA-1)*100，只在升管(日ZA>0)时有值
扩管>60 / 平管0~60 / 窄管<0
"""
import io, os, glob, sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 列映射（VBA权威，勿信表头）
# col8=DXCD, col9=DXAB, col10=柱排, col13=日ZA, col14=日ZC, col19=BSHA, col23=管宽哼JA, col26=次日高幅, col30=上符串, col44=BT连阳

stats = defaultdict(lambda: {'n': 0, 'p3': 0, 'p5': 0, 'sum_nh': 0})

def add(label, nh):
    st = stats[label]
    st['n'] += 1
    if nh >= 3: st['p3'] += 1
    if nh >= 5: st['p5'] += 1
    st['sum_nh'] += nh

def deng_type(za):
    if za == 1: return '等1'
    elif za == 2: return '等2'
    elif za >= 3: return '等3'
    elif za == -1: return '等5(首下破)'
    elif za == -2: return '等6'
    elif za <= -3: return '等7'
    else: return '其他'

def zhupai_class(zp):
    if zp.startswith('升.'):
        if '尾连' in zp: return '升连'
        elif '尾吞' in zp: return '升吞'
        elif '尾反孕' in zp: return '升孕'
        else: return '升排其他'
    elif zp.startswith('跌.'):
        if '尾连' in zp: return '跌连'
        elif '尾吞' in zp: return '跌吞'
        elif '尾反孕' in zp: return '跌孕'
        else: return '跌排其他'
    elif zp.startswith('('):
        return '人排'
    else:
        return '其他'

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 31:
                continue
            try:
                cd = row[8]
                ab = row[9]
                zp = row[10]
                za = int(row[13])
                zc = int(row[14])
                bsha = float(row[19])
                gk = row[23].strip()  # 管宽哼JA
                nh = float(row[26])
                sf = row[30]  # 上符串
            except:
                continue
            hx = ab[0] if ab else ''
            dt = deng_type(za)
            zpc = zhupai_class(zp)
            # 管宽哼JA 分类
            if gk == '':
                gk_class = '空(跌管)'
            else:
                gkv = float(gk)
                if gkv > 60: gk_class = '扩管>60'
                elif gkv >= 0: gk_class = '平管0-60'
                else: gk_class = '窄管<0'
            # 触顶 = 上符串含A
            touch = 'A' in sf

            # ===== 等3 验证 =====
            if dt == '等3' and hx in ('a','b','r'):
                add(f'等3_甲乙己_基线', nh)
                add(f'等3_{zpc}', nh)
                add(f'等3_{zpc}_{gk_class}', nh)
                if touch:
                    add(f'等3_{zpc}_触顶', nh)
                else:
                    add(f'等3_{zpc}_未触顶', nh)

            # ===== 等1 验证 =====
            if dt == '等1' and hx in ('a','b','r'):
                add(f'等1_甲乙己_基线', nh)
                add(f'等1_{zpc}', nh)

            # ===== 等2 验证 =====
            if dt == '等2' and hx in ('a','b','r'):
                add(f'等2_甲乙己_基线', nh)
                add(f'等2_{zpc}', nh)
                if touch:
                    add(f'等2_触顶', nh)
                else:
                    add(f'等2_未触顶', nh)

            # ===== 等4 (乙DXZA<0) 验证 =====
            if za < 0 and hx == 'b':
                add(f'等4_乙ZA<0_{dt}', nh)

print('\n=== 管宽哼JA(col23) 分类分布（甲乙己升管）===')
for label in ('扩管>60', '平管0-60', '窄管<0', '空(跌管)'):
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%')

print('\n=== 等3 介入点验证 ===')
for label in sorted(stats.keys()):
    if not label.startswith('等3'): continue
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 次日P5%={st["p5"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')

print('\n=== 等1 介入点验证 ===')
for label in sorted(stats.keys()):
    if not label.startswith('等1'): continue
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')

print('\n=== 等2 介入点验证 ===')
for label in sorted(stats.keys()):
    if not label.startswith('等2'): continue
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')

print('\n=== 等4 (乙DXZA<0) 验证 ===')
for label in sorted(stats.keys()):
    if not label.startswith('等4'): continue
    st = stats[label]
    if st['n'] == 0: continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')
