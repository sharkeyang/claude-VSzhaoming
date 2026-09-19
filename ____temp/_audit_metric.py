# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

def parse_ding(s):
    if not s: return None, None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'
files = []
for fp in glob.glob(DATA_DIR + '/*.csv'):
    frows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 44: continue
            try:
                zf = float(row[5]); dtza = int(row[13])
                hx = row[9][1] if len(row[9])>1 else None
                dc = parse_ding(row[43])[1]
                zp = row[10]
                bf = row[34].strip(); last = bf[-1] if bf else ''
                frows.append((zf, dtza, hx, dc, zp, last))
            except: continue
    files.append(frows)

# 审计：在"甲护型+升管+阳柱+回调后"样本里，未来5天"升"开头柱排占比
# 以及 未来5天 a龙 / 升.尾连 占比
import collections
# 统计回调后阳柱样本的 未来5天 各指标命中率
stats = collections.defaultdict(lambda: [0,0,0,0,0])  # n, 升开头, a龙, 升.尾连, 升.尾连或a龙

for frows in files:
    N = len(frows)
    # 预计算未来5天窗口
    fut_sheng = [False]*N; fut_touch=[False]*N; fut_sl=[False]*N
    for i in range(N-1,-1,-1):
        lo=i+1; hi=min(i+5,N-1)
        if lo<=hi:
            fut_sheng[i]=any(frows[j][4].startswith('升') or frows[j][4].startswith('(升)') for j in range(lo,hi+1))
            fut_touch[i]=any(frows[j][3]=='a龙' for j in range(lo,hi+1))
            fut_sl[i]=any(frows[j][4].startswith('升.尾连') for j in range(lo,hi+1))
    for i in range(1, N-1):
        zf, dtza, hx, dc, zp, last = frows[i]
        if hx != '甲' or dtza <= 0 or zf <= 0: continue
        cb_type=None; cb_idx=None
        for k in range(i-1, max(i-6,-1), -1):
            if frows[k][1] < 0: cb_type='下破DJA'; cb_idx=k; break
            if frows[k][0] < 0: cb_type='阴柱'; cb_idx=k; break
        if cb_type is None: continue
        key = cb_type
        stats[key][0]+=1
        stats[key][1]+=fut_sheng[i]
        stats[key][2]+=fut_touch[i]
        stats[key][3]+=fut_sl[i]
        stats[key][4]+=fut_touch[i] or fut_sl[i]

print('=== 回调后阳柱，未来5天各指标命中率 ===')
print(f'{"类型":<10} {"n":>9} {"升开头":>8} {"a龙":>7} {"升.尾连":>8} {"a龙或升连":>10}')
print('-'*60)
for k,(tot,sh,t,sl,ts) in sorted(stats.items(), key=lambda x:-x[1][0]):
    print(f'{k:<10} {tot:>9,} {sh/tot*100:>7.1f}% {t/tot*100:>6.1f}% {sl/tot*100:>7.1f}% {ts/tot*100:>9.1f}%')
