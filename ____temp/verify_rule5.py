# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

def zhu_class(zhu):
    if zhu.startswith('升') and '连' in zhu: return '升连'
    if zhu.startswith('跌') and '孕' in zhu: return '跌孕'
    if zhu.startswith('(人)'): return '阴阳阴'
    if zhu.startswith('(升)人') or zhu.startswith('(跌)人'): return '人排'
    return '其他'

# 完整规则验证
# 基线: DXCD=上/忐 + DXZC>0 + 甲乙己
# 优化介入: 基线 + 入管判定过滤(DTZA=1升连/DTZA=2升连或跌孕/DTZA=3排除阴阳阴)
# 但DTZA=1升连无效, 测试两种: 用户原规则 vs 修正规则(DTZA=1不过滤)
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
        hx0 = row[9][0]
        za = int(row[13])
        zhu = row[10]
        try:
            nxt_hr = float(nxt[26])
        except:
            continue
        p3 = 1 if nxt_hr >= 3 else 0
        if dxcd in ('上','忐') and dxzc > 0 and hx0 in ('a','b','r'):
            r['基线(甲乙己)'][0] += 1
            if p3: r['基线(甲乙己)'][1] += 1
            zc = zhu_class(zhu)
            # 用户原规则
            ok_user = False
            if za == 1:
                ok_user = (zc == '升连')
            elif za == 2:
                ok_user = (zc in ('升连','跌孕'))
            elif za >= 3:
                ok_user = (zc != '阴阳阴')
            if ok_user:
                r['用户原规则'][0] += 1
                if p3: r['用户原规则'][1] += 1
            # 修正规则: DTZA=1不过滤(因为升连无效)
            ok_fix = False
            if za == 1:
                ok_fix = True  # DTZA=1不过滤
            elif za == 2:
                ok_fix = (zc in ('升连','跌孕'))
            elif za >= 3:
                ok_fix = (zc != '阴阳阴')
            if ok_fix:
                r['修正规则(DTZA=1不过滤)'][0] += 1
                if p3: r['修正规则(DTZA=1不过滤)'][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 完整规则验证: 基线 vs 用户原规则 vs 修正规则 ===')
print(f"{'规则':<26}{'样本':>9}{'P>=3%':>8}{'P':>8}")
for k,(tot,hit) in r.items():
    print(f"{k:<26}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%")
