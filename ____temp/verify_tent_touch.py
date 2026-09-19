# -*- coding: utf-8 -*-
"""
验证帐篷（回调后阳柱触顶，未来继续触顶/创新高）
用户定义：升管中暂时阴柱或下破DJA，再次阳柱触顶后可能再次连续触顶入管
指标：回调后阳柱触顶(a龙)，未来N天再次触顶(a龙)或创新高概率
"""
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_ding(s):
    if not s: return None,None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

# 加载数据: (涨幅, 日ZA, 护型, 顶态, 核心顶型, 收盘价)
files = []
for fp in glob.glob(DATA_DIR + '/*.csv'):
    frows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62:
                continue
            try:
                zf = float(row[5])
                dtza = int(row[13])
                hx = row[9][1] if len(row[9]) > 1 else None
                ds, dc = parse_ding(row[43])
                close = float(row[1])
                frows.append((zf, dtza, hx, ds, dc, close))
            except (ValueError, IndexError):
                continue
    files.append(frows)

total = sum(len(f) for f in files)
print(f'总行数: {total}')

def again_touch(frows, i, la=5):
    """未来la天内再次触顶(a龙)"""
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][4] == 'a龙':
            return True
    return False

def new_high(frows, i, la=5):
    """未来la天内创新高(收盘>当前收盘)"""
    cur = frows[i][5]
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][5] > cur:
            return True
    return False

# 场景：甲护型 + 升管(日ZA>0) + 阳柱触顶(a龙)
# 分组：回调后触顶 vs 无回调直接触顶
# 回调 = 之前5日内出现阴柱(zf<0)或下破DJA(dtza<0)
stats = {
    '回调后触顶': [0,0,0],  # [总数, 再次触顶, 创新高]
    '无回调触顶': [0,0,0],
}
# 细分：回调类型
sub = collections.defaultdict(lambda: [0,0,0])

for frows in files:
    N = len(frows)
    for i in range(1, N-1):
        zf, dtza, hx, ds, dc, close = frows[i]
        if hx != '甲' or dtza <= 0 or zf <= 0 or dc != 'a龙':
            continue
        # 阳柱触顶(a龙)
        # 检查之前5日内是否有回调(阴柱或下破DJA)
        has_callback = False
        cb_type = '无'
        for k in range(i-1, max(i-6, -1), -1):
            if frows[k][1] < 0:  # 下破DJA
                has_callback = True
                cb_type = '下破DJA'
                break
            if frows[k][0] < 0:  # 阴柱
                has_callback = True
                cb_type = '阴柱'
                break
        key = '回调后触顶' if has_callback else '无回调触顶'
        stats[key][0] += 1
        if again_touch(frows, i): stats[key][1] += 1
        if new_high(frows, i): stats[key][2] += 1
        if has_callback:
            sub[cb_type][0] += 1
            if again_touch(frows, i): sub[cb_type][1] += 1
            if new_high(frows, i): sub[cb_type][2] += 1

print(f'\n=== 甲升管阳柱触顶(a龙)，未来5日 ===')
for key in ['回调后触顶', '无回调触顶']:
    tot, at, nh = stats[key]
    if tot:
        print(f'{key}: n={tot}, 再次触顶={at/tot*100:.1f}%, 创新高={nh/tot*100:.1f}%')

print(f'\n=== 回调类型细分 ===')
for cb, (tot, at, nh) in sorted(sub.items(), key=lambda x:-x[1][0]):
    if tot:
        print(f'{cb}: n={tot}, 再次触顶={at/tot*100:.1f}%, 创新高={nh/tot*100:.1f}%')
