# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 用户操作规则验证
# 基线: DXCD=上/忐 + DXZC>0 + 甲乙己(DXZA>0)
# 优化: 基线 + 入管判定过滤(DTZA=1升连/DTZA=2升连或跌孕/DTZA=3排除阴阳阴)

def zhu_class(zhu):
    """柱排分类: 升连/跌孕/阴阳阴/其他"""
    if zhu.startswith('升') and '连' in zhu:
        return '升连'
    if zhu.startswith('跌') and '孕' in zhu:
        return '跌孕'
    if zhu.startswith('(人)'):
        return '阴阳阴'
    if zhu.startswith('(升)人') or zhu.startswith('(跌)人'):
        return '人排'
    return '其他'

# 统计: (规则) -> [样本, P>=3%]
r = defaultdict(lambda:[0,0])

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        nxt = rows[i+1]
        dxcd = row[8]
        dxzc = int(row[14])
        hx = row[9]
        hx0 = hx[0]
        za = int(row[13])
        zhu = row[10]
        try:
            nxt_hr = float(nxt[26])
        except:
            continue
        p3 = 1 if nxt_hr >= 3 else 0
        # 基线: DXCD=上/忐 + DXZC>0 + 甲乙己
        if dxcd in ('上','忐') and dxzc > 0 and hx0 in ('a','b','r'):
            r['基线(甲乙己)'][0] += 1
            if p3: r['基线(甲乙己)'][1] += 1
            # 优化: 入管判定过滤
            zc = zhu_class(zhu)
            ok = False
            if za == 1:
                ok = (zc == '升连')
            elif za == 2:
                ok = (zc in ('升连','跌孕'))
            elif za >= 3:
                ok = (zc != '阴阳阴')  # 排除阴阳阴
            if ok:
                r['优化(入管过滤)'][0] += 1
                if p3: r['优化(入管过滤)'][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 用户操作规则验证: 基线 vs 优化(入管判定过滤) ===')
print(f"{'规则':<20}{'样本':>9}{'P>=3%':>8}{'P':>8}")
for k,(tot,hit) in r.items():
    print(f"{k:<20}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%")
