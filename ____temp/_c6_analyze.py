# -*- coding: utf-8 -*-
import csv, glob, sys
from collections import Counter

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
print('NFILES:', len(files))

# columns of interest
# 9=护型, 10=柱排, 13=日ZA, 19=BSHA, 21=脸哼JA, 22=宽哼JC, 26=次日高幅, 30=上符串, 43=日等型
COLS = [9,10,13,19,21,22,26,30,43]

def parse_float(s):
    try:
        return float(s)
    except:
        return None

# aggregate counters
tot = 0
# 27: 合顶 vs 非合顶 次日高幅>=3%
heiding_n=0; heiding_hit=0
nonheiding_n=0; nonheiding_hit=0
# 29: 触顶(A) + BSHA>=8
touch_bsha8_n=0; touch_bsha8_hit=0
# 30: 触顶 vs 非触顶
touch_n=0; touch_hit=0
nontouch_n=0; nontouch_hit=0
# 31: DTZA thresholds
dtza_bins = {}  # key: label, value: [n, hit]
# 32: 等5 BSHA>=5
eq5_bsha5_n=0
# 37: 窄管占比 (两种定义)
narrow_JA_n=0  # 脸哼JA < threshold
narrow_JC_n=0  # 宽哼JC < threshold
# 38: 十字星 次日高幅>=3%
cross_n=0; cross_hit=0
# 39: 合顶天数
heiding_days = {}  # days -> [n, hit]
# 40: 乙护型 DXZA<0
yi_n=0; yi_za_neg_n=0; yi_za_neg_hit=0; yi_za_neg_total=0
# 41: 单阳 vs 升吞
danyang_n=0; danyang_hit=0
shengtun_n=0; shengtun_hit=0

for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)  # header
        for row in r:
            if len(row) < 70:
                continue
            tot += 1
            huxing = row[9]
            zhupai = row[10]
            dza = parse_float(row[13])
            bsha = parse_float(row[19])
            lianJA = parse_float(row[21])
            kuanJC = parse_float(row[22])
            cg = parse_float(row[26])  # 次日高幅
            shangfu = row[30]
            dengxing = row[43]
            hit = (cg is not None and cg >= 3.0)

            # 上符串 触顶 = 右端A
            touch = shangfu.endswith('A') if shangfu else False
            # 合顶 = 右端连续A>=2
            nA = 0
            if shangfu:
                for ch in reversed(shangfu):
                    if ch == 'A':
                        nA += 1
                    else:
                        break
            heiding = nA >= 2

            # 27
            if heiding:
                heiding_n += 1
                if hit: heiding_hit += 1
            else:
                nonheiding_n += 1
                if hit: nonheiding_hit += 1

            # 29, 30
            if touch:
                touch_n += 1
                if hit: touch_hit += 1
                if bsha is not None and bsha >= 8:
                    touch_bsha8_n += 1
                    if hit: touch_bsha8_hit += 1
            else:
                nontouch_n += 1
                if hit: nontouch_hit += 1

            # 31 DTZA thresholds
            if dza is not None:
                if dza > 0:
                    lab = 'DTZA>0'
                elif dza == 0:
                    lab = 'DTZA=0'
                else:
                    lab = 'DTZA<0'
                b = dtza_bins.setdefault(lab, [0,0])
                b[0]+=1
                if hit: b[1]+=1

            # 32 等5 BSHA>=5
            if dengxing and '等5' in dengxing and bsha is not None and bsha >= 5:
                eq5_bsha5_n += 1

            # 37 窄管
            if lianJA is not None and lianJA < 4:
                narrow_JA_n += 1
            if kuanJC is not None and kuanJC < 4:
                narrow_JC_n += 1

            # 38 十字星
            if zhupai and '十字星' in zhupai:
                cross_n += 1
                if hit: cross_hit += 1

            # 39 合顶天数
            if heiding:
                d = heiding_days.setdefault(nA, [0,0])
                d[0]+=1
                if hit: d[1]+=1

            # 40 乙护型
            if huxing and huxing[0] == 'b':
                yi_n += 1
                if dza is not None and dza < 0:
                    yi_za_neg_n += 1
                    yi_za_neg_total += 1
                    if hit: yi_za_neg_hit += 1

            # 41 单阳 vs 升吞
            if zhupai:
                if '单阳' in zhupai:
                    danyang_n += 1
                    if hit: danyang_hit += 1
                if '升吞' in zhupai:
                    shengtun_n += 1
                    if hit: shengtun_hit += 1

print('TOTAL rows:', tot)
def pct(n, hit):
    return (100.0*hit/n if n else 0.0), n

print('\n#27 合顶区分度')
p1,n1 = pct(heiding_n, heiding_hit)
p2,n2 = pct(nonheiding_n, nonheiding_hit)
print(f'  合顶: {p1:.2f}% (n={n1})')
print(f'  非合顶: {p2:.2f}% (n={n2})')
print(f'  区分度: {p1-p2:.2f}pp')

print('\n#29 触顶+BSHA>=8')
p,n = pct(touch_bsha8_n, touch_bsha8_hit)
print(f'  触顶+BSHA>=8: {p:.2f}% (n={n})')

print('\n#30 触顶增益')
p1,n1 = pct(touch_n, touch_hit)
p2,n2 = pct(nontouch_n, nontouch_hit)
print(f'  触顶: {p1:.2f}% (n={n1})')
print(f'  非触顶: {p2:.2f}% (n={n2})')
print(f'  增益: {p1-p2:.2f}pp')

print('\n#31 DTZA阈值')
for lab in ['DTZA>0','DTZA=0','DTZA<0']:
    if lab in dtza_bins:
        n,hit = dtza_bins[lab]
        p = 100.0*hit/n
        print(f'  {lab}: {p:.2f}% (n={n})')

print('\n#32 等5 BSHA>=5 样本:', eq5_bsha5_n)

print('\n#37 窄管占比 (阈值<4)')
print(f'  脸哼JA<4: {100.0*narrow_JA_n/tot:.2f}% (n={narrow_JA_n})')
print(f'  宽哼JC<4: {100.0*narrow_JC_n/tot:.2f}% (n={narrow_JC_n})')

print('\n#38 十字星')
p,n = pct(cross_n, cross_hit)
print(f'  十字星: {p:.2f}% (n={n})')

print('\n#39 合顶天数')
for d in sorted(heiding_days):
    n,hit = heiding_days[d]
    p = 100.0*hit/n
    print(f'  合顶{d}天: {p:.2f}% (n={n})')

print('\n#40 乙护型 DXZA<0')
print(f'  乙护型总数: {yi_n}')
print(f'  乙 DXZA<0: {yi_za_neg_n} ({100.0*yi_za_neg_n/yi_n if yi_n else 0:.2f}%)')
if yi_za_neg_total:
    p = 100.0*yi_za_neg_hit/yi_za_neg_total
    print(f'  乙 DXZA<0 次日高幅>=3%: {p:.2f}% (n={yi_za_neg_total})')

print('\n#41 单阳 vs 升吞')
p1,n1 = pct(danyang_n, danyang_hit)
p2,n2 = pct(shengtun_n, shengtun_hit)
print(f'  单阳: {p1:.2f}% (n={n1})')
print(f'  升吞: {p2:.2f}% (n={n2})')
