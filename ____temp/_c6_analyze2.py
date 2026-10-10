# -*- coding: utf-8 -*-
import csv, glob
from collections import Counter

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
print('NFILES:', len(files))

def pf(s):
    try: return float(s)
    except: return None

# counters
tot=0
# 27 合顶
heiding_n=0; heiding_hit=0
nonheiding_n=0; nonheiding_hit=0
# 29/30 触顶
touch_n=0; touch_hit=0
nontouch_n=0; nontouch_hit=0
touch_bsha8_n=0; touch_bsha8_hit=0
# 31 DTZA
dtza_pos_n=0; dtza_pos_hit=0
dtza_neg_n=0; dtza_neg_hit=0
dtza_zero_n=0
# 32 等5 BSHA5
eq5_bsha5_n=0
# 37 窄管
narrow_JA_n=0; narrow_JC_n=0
# 38 十字星 (OHLC)
cross_n=0; cross_hit=0
# 39 合顶天数 full
heiding_days = {}  # days -> [n, hit]
# 40 乙
yi_n=0; yi_za_neg_n=0; yi_za_neg_hit=0
# 41 单阳柱(今升昨非升) vs 升吞
danyang_n=0; danyang_hit=0
shengtun_n=0; shengtun_hit=0

prev_zhangfu = None  # previous row 涨幅

for f in files:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        prev_zhangfu = None
        for row in r:
            if len(row)<70: continue
            tot+=1
            huxing=row[9]; zhupai=row[10]
            dza=pf(row[13]); bsha=pf(row[19])
            lianJA=pf(row[21]); kuanJC=pf(row[22])
            cg=pf(row[26]); shangfu=row[30]; dengxing=row[43]
            zhangfu=pf(row[5])
            o=pf(row[2]); h=pf(row[3]); l=pf(row[4]); c=pf(row[1])
            hit = (cg is not None and cg>=3.0)

            # 触顶/合顶 from 上符串 rightmost A
            nA=0
            if shangfu:
                for ch in reversed(shangfu):
                    if ch=='A': nA+=1
                    else: break
            touch = nA>=1
            heiding = nA>=2

            if heiding:
                heiding_n+=1
                if hit: heiding_hit+=1
            else:
                nonheiding_n+=1
                if hit: nonheiding_hit+=1

            if touch:
                touch_n+=1
                if hit: touch_hit+=1
                if bsha is not None and bsha>=8:
                    touch_bsha8_n+=1
                    if hit: touch_bsha8_hit+=1
            else:
                nontouch_n+=1
                if hit: nontouch_hit+=1

            if dza is not None:
                if dza>0:
                    dtza_pos_n+=1
                    if hit: dtza_pos_hit+=1
                elif dza<0:
                    dtza_neg_n+=1
                    if hit: dtza_neg_hit+=1
                else:
                    dtza_zero_n+=1

            if dengxing and '等5' in dengxing and bsha is not None and bsha>=5:
                eq5_bsha5_n+=1

            if lianJA is not None and lianJA<4: narrow_JA_n+=1
            if kuanJC is not None and kuanJC<4: narrow_JC_n+=1

            # 十字星: 实体<10%全幅 且 上影<=2*实体
            if o is not None and h is not None and l is not None and c is not None:
                full = h-l
                if full>0:
                    body = abs(c-o)
                    upper = h - max(c,o)
                    if body < 0.1*full and upper <= 2*body:
                        cross_n+=1
                        if hit: cross_hit+=1

            # 合顶天数 full (0,1,2,...)
            d = heiding_days.setdefault(nA, [0,0])
            d[0]+=1
            if hit: d[1]+=1

            # 乙护型
            if huxing and huxing[0]=='b':
                yi_n+=1
                if dza is not None and dza<0:
                    yi_za_neg_n+=1
                    if hit: yi_za_neg_hit+=1

            # 单阳柱 = 今升昨非升 (今涨幅>0 且 昨涨幅<=0)
            if zhangfu is not None and zhangfu>0 and prev_zhangfu is not None and prev_zhangfu<=0:
                danyang_n+=1
                if hit: danyang_hit+=1
            # 升吞 = 柱排含 '升吞'
            if zhupai and '升吞' in zhupai:
                shengtun_n+=1
                if hit: shengtun_hit+=1

            prev_zhangfu = zhangfu

print('TOTAL:', tot)
def pct(n,hit): return (100.0*hit/n if n else 0.0), n

print('\n#27 合顶区分度')
p1,n1=pct(heiding_n,heiding_hit); p2,n2=pct(nonheiding_n,nonheiding_hit)
print(f'  合顶 {p1:.2f}% (n={n1}) vs 非合顶 {p2:.2f}% (n={n2}) = {p1-p2:.2f}pp')

print('\n#29 触顶+BSHA>=8')
p,n=pct(touch_bsha8_n,touch_bsha8_hit)
print(f'  {p:.2f}% (n={n})')

print('\n#30 触顶增益')
p1,n1=pct(touch_n,touch_hit); p2,n2=pct(nontouch_n,nontouch_hit)
print(f'  触顶 {p1:.2f}% (n={n1}) vs 非触顶 {p2:.2f}% (n={n2}) = +{p1-p2:.2f}pp')

print('\n#31 DTZA阈值')
p,n=pct(dtza_pos_n,dtza_pos_hit); print(f'  DTZA>0 {p:.2f}% (n={n})')
p,n=pct(dtza_neg_n,dtza_neg_hit); print(f'  DTZA<0 {p:.2f}% (n={n})')
print(f'  DTZA=0 n={dtza_zero_n}')

print('\n#32 等5 BSHA>=5 样本:', eq5_bsha5_n)

print('\n#37 窄管占比(<4)')
print(f'  脸哼JA<4 {100.0*narrow_JA_n/tot:.2f}% (n={narrow_JA_n})')
print(f'  宽哼JC<4 {100.0*narrow_JC_n/tot:.2f}% (n={narrow_JC_n})')

print('\n#38 十字星')
p,n=pct(cross_n,cross_hit)
print(f'  {p:.2f}% (n={n})')

print('\n#39 合顶天数 (上符串右端A数)')
for d in sorted(heiding_days):
    n,hit=heiding_days[d]
    p=100.0*hit/n
    print(f'  {d}天 {p:.2f}% (n={n})')

print('\n#40 乙护型')
print(f'  乙总数 {yi_n}, 乙DXZA<0 {yi_za_neg_n} ({100.0*yi_za_neg_n/yi_n if yi_n else 0:.2f}%)')
if yi_za_neg_n:
    p=100.0*yi_za_neg_hit/yi_za_neg_n
    print(f'  乙DXZA<0 次日高幅>=3% {p:.2f}% (n={yi_za_neg_n})')

print('\n#41 单阳柱(今升昨非升) vs 升吞')
p1,n1=pct(danyang_n,danyang_hit); p2,n2=pct(shengtun_n,shengtun_hit)
print(f'  单阳柱 {p1:.2f}% (n={n1})')
print(f'  升吞 {p2:.2f}% (n={n2})')
