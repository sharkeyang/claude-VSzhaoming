# -*- coding: utf-8 -*-
"""C8 文档审核：用新元数据(周类62列)计算各策略 P(≥3%) 真实值
输出到 UTF-8 文件，避免控制台 GBK 乱码。
"""
import glob, csv, os, sys
from collections import Counter

DATA_DIR = r"d:/@VSwork/VS昭明计划VBA优化/昭明算展/谕组周"
OUT = r"d:/@VSwork/VS昭明计划VBA优化/____temp/c8_result.txt"

# 列索引 (0-based)
C_HR = 3        # 下周高幅
C_HUXING = 4    # 护型 (a甲/b乙/c丙/z丁/y戊/r己)
C_BOXING = 5    # 波型
C_ZHUP = 6      # 柱排
C_YING = 12     # 盈提示

def is_jin(hx):  # 金系 = 甲乙己
    return hx[0] in ('a', 'b', 'r') if hx else False

def is_sheng(zp):  # 升排 = 柱排含"升"
    return '升' in zp if zp else False

def is_feiyun(zp):  # 非孕 = 柱排不含"孕"
    return ('孕' not in zp) if zp else False

def is_yinggao(yg):  # 盈高 = 盈提示含"盈"或"高"
    return ('盈' in yg or '高' in yg) if yg else False

def is_long(zp):  # 龙猪/管 = 波型含"龙猪"或"龙管"
    return ('龙猪' in zp or '龙管' in zp) if zp else False

# 统计器：每个策略记录 (总样本, 达标样本)
stats = {}

def add(name, hit):
    if name not in stats:
        stats[name] = [0, 0]
    stats[name][0] += 1
    if hit:
        stats[name][1] += 1

files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
print(f"文件数: {len(files)}", file=open(OUT, 'w', encoding='utf-8'))

n_rows = 0
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        header = next(r)
        prev = None  # (row, hit_flag_dict) 上一行
        # 我们需要"下周HR"：即当前行的 HR 是上一行条件的下周冲高
        # 所以对每行，用上一行的条件判断，用当前行 HR 判断是否≥3%
        rows = []
        for row in r:
            rows.append(row)
        for i in range(len(rows) - 1):
            cur = rows[i]
            nxt = rows[i+1]
            hx = cur[C_HUXING]
            zp = cur[C_ZHUP]
            bx = cur[C_BOXING]
            yg = cur[C_YING]
            hr_next = nxt[C_HR]
            try:
                hr_val = float(hr_next)
            except:
                hr_val = 0.0
            hit = hr_val >= 3.0
            n_rows += 1

            # 金系策略
            if is_jin(hx):
                if is_sheng(zp):
                    add('金升', hit)
                    if is_feiyun(zp):
                        add('金升非', hit)
                        if is_yinggao(yg):
                            add('金升非盈', hit)
                            if is_long(bx):
                                add('金升非盈龙', hit)
            # 己护型
            if hx and hx[0] == 'r':
                add('己', hit)
            # 银系 = 非金系且 WXZC>0 (四域不在金区但仍在WJC之上)
            # 简化：银系 = 护型非甲乙己 (丙丁戊) 且 ZC>0
            if hx and hx[0] in ('c', 'z', 'y'):
                add('银系(丙丁戊)', hit)

print(f"总行数(有下一行): {n_rows}", file=open(OUT, 'a', encoding='utf-8'))
print("", file=open(OUT, 'a', encoding='utf-8'))
print("策略\t样本\tP(>=3%)\t达标数", file=open(OUT, 'a', encoding='utf-8'))
for name in ['金升', '金升非', '金升非盈', '金升非盈龙', '己', '银系(丙丁戊)']:
    if name in stats:
        n, h = stats[name]
        pct = 100.0 * h / n if n else 0
        print(f"{name}\t{n}\t{pct:.1f}%\t{h}", file=open(OUT, 'a', encoding='utf-8'))
print("DONE", file=open(OUT, 'a', encoding='utf-8'))
