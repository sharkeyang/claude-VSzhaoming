# -*- coding: utf-8 -*-
"""C8 文档审核 v2：金条件=ZC>0+甲乙己, 银条件=ZC>0+丙丁戊
输出 UTF-8 文件。
"""
import glob, csv, os

DATA_DIR = r"d:/@VSwork/VS昭明计划VBA优化/昭明算展/谕组周"
OUT = r"d:/@VSwork/VS昭明计划VBA优化/____temp/c8_result2.txt"

C_HR = 3
C_HUXING = 4
C_BOXING = 5
C_ZHUP = 6
C_YING = 12
C_ZC = 15   # ZC周

def is_jin(hx): return hx[0] in ('a','b','r') if hx else False
def is_yin(hx): return hx[0] in ('c','z','y') if hx else False
def is_sheng(zp): return '升' in zp if zp else False
def is_feiyun(zp): return ('孕' not in zp) if zp else False
def is_yinggao(yg): return ('盈' in yg or '高' in yg) if yg else False
def is_long(bx): return ('龙猪' in bx or '龙管' in bx) if bx else False

stats = {}
def add(name, hit):
    stats.setdefault(name, [0,0])
    stats[name][0] += 1
    if hit: stats[name][1] += 1

files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
out = open(OUT, 'w', encoding='utf-8')
print(f"文件数: {len(files)}", file=out)

n_rows = 0
for f in files:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        header = next(r)
        rows = list(r)
    for i in range(len(rows)-1):
        cur = rows[i]; nxt = rows[i+1]
        hx = cur[C_HUXING]; zp = cur[C_ZHUP]; bx = cur[C_BOXING]; yg = cur[C_YING]
        zc = cur[C_ZC]
        try: zc_val = float(zc)
        except: zc_val = 0.0
        try: hr_val = float(nxt[C_HR])
        except: hr_val = 0.0
        hit = hr_val >= 3.0
        n_rows += 1

        zc_pos = zc_val > 0
        # 金系 = ZC>0 + 甲乙己
        if zc_pos and is_jin(hx):
            if is_sheng(zp):
                add('金升', hit)
                if is_feiyun(zp):
                    add('金升非', hit)
                    if is_yinggao(yg):
                        add('金升非盈', hit)
                        if is_long(bx):
                            add('金升非盈龙', hit)
        # 银系 = ZC>0 + 丙丁戊
        if zc_pos and is_yin(hx):
            if is_sheng(zp):
                add('银升', hit)
            if is_yinggao(yg):
                add('银盈', hit)
        # 己护型 (不限ZC)
        if hx and hx[0]=='r':
            add('己', hit)

print(f"总行数: {n_rows}", file=out)
print("", file=out)
print("策略\t样本\tP(>=3%)\t达标数", file=out)
for name in ['金升','金升非','金升非盈','金升非盈龙','银升','银盈','己']:
    if name in stats:
        n,h = stats[name]
        print(f"{name}\t{n}\t{100.0*h/n:.1f}%\t{h}", file=out)
print("DONE", file=out)
out.close()
