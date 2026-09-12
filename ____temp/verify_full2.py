# -*- coding: utf-8 -*-
import csv, glob
from collections import Counter, defaultdict

files = glob.glob('谕组日_*.csv')
HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 结果容器
zhuanjia_deng = Counter()
zhuanjia_total = 0
jia_e2 = defaultdict(lambda: [0,0])   # (分组) -> [样本, 次日冲高]
jia_e3 = defaultdict(lambda: [0,0])   # (柱排方向) -> [样本, 次日冲高]
jia_e3_break = defaultdict(lambda: [0,0])  # (柱排方向) -> [样本, 次日下破DJA]

def parse_dxab(hx_str):
    # DXAB数值 = 索引4 (a甲↗上1.I 中的 '1')
    try:
        return int(hx_str[4])
    except:
        return None

def zhu_dir_class(zhu):
    # 柱排分类: 升排/跌排/跌吞/阴阳阴等
    if zhu.startswith('升'):
        return '升排'
    if zhu.startswith('跌'):
        # 区分跌排 vs 跌吞
        if '吞' in zhu:
            return '跌吞'
        return '跌排'
    if zhu.startswith('(升)'):
        return '(升)人'
    if zhu.startswith('(跌)'):
        return '(跌)人'
    if zhu.startswith('(人)'):
        return '(人)人'
    return '其他:'+zhu[:4]

n=0
for fp in files:
    prev_hx = None
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62: continue
            cur_hx = row[9][0]
            deng = row[44]
            za = row[13]
            zhu = row[10]
            next_hr = row[26]
            # 由己转甲
            if prev_hx == 'r' and cur_hx == 'a':
                zhuanjia_deng[deng] += 1
                zhuanjia_total += 1
            # 甲+等2: 按DTZA/DXAB分组
            if cur_hx == 'a' and deng == '等2':
                try:
                    dtza = int(za)
                    next_hr_f = float(next_hr)
                except:
                    dtza, next_hr_f = None, None
                if dtza is not None and next_hr_f is not None:
                    dxab = parse_dxab(row[9])
                    if dxab is not None:
                        if dxab > 10:
                            grp = 'DXAB>10'
                        elif dtza <= 3:
                            grp = 'DTZA<=3(转甲初期)'
                        else:
                            grp = 'DTZA>3'
                        jia_e2[grp][0] += 1
                        if next_hr_f > 3: jia_e2[grp][1] += 1
            # 甲+等3: 按柱排方向分组
            if cur_hx == 'a' and deng == '等3':
                try:
                    next_hr_f = float(next_hr)
                except:
                    next_hr_f = None
                grp = zhu_dir_class(zhu)
                if next_hr_f is not None:
                    jia_e3[grp][0] += 1
                    if next_hr_f > 3: jia_e3[grp][1] += 1
            prev_hx = cur_hx
            n += 1

print('总行数:', n)
print('\n=== 假设1b: 由己转甲当天 日等型分布 ===')
print('由己转甲样本数:', zhuanjia_total)
for k,v in zhuanjia_deng.most_common():
    print(f'  {k}: {v} ({v/zhuanjia_total*100:.2f}%)')

print('\n=== 假设2: 甲+等2 按DTZA/DXAB分组 次日冲高P(>=3%) ===')
for grp, (tot, hit) in sorted(jia_e2.items()):
    pct = hit/tot*100 if tot else 0
    print(f'  {grp:<22}: 样本{tot:>8} 冲高{hit:>7} P={pct:.2f}%')

print('\n=== 假设3: 甲+等3 按柱排方向分组 次日冲高P(>=3%) ===')
for grp, (tot, hit) in sorted(jia_e3.items()):
    pct = hit/tot*100 if tot else 0
    print(f'  {grp:<12}: 样本{tot:>8} 冲高{hit:>7} P={pct:.2f}%')
