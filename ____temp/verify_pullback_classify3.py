# -*- coding: utf-8 -*-
"""
回调分类 v3：修正"再次触顶/升排"指标
====================================================
问题：原指标 is_shengpai = zp.startswith('升') 太宽泛，
     升管(日ZA>0)里79.5%柱排都是'升'开头，导致概率虚高到99%。

修正：用更严格、有区分度的指标：
  指标A: 未来5日再次触顶(a龙顶型)
  指标B: 未来5日出现升.尾连(连续升连，真正的升排)
  指标C: 未来5日再次触顶(a龙) 或 升.尾连

同时对比基线：无回调阳柱
"""
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_ding(s):
    if not s: return None, None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

# 加载数据: (涨幅, 日ZA, 护型, 核心顶型, 柱排, 并符末位)
files = []
for fp in glob.glob(DATA_DIR + '/*.csv'):
    frows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 44:
                continue
            try:
                zf = float(row[5])
                dtza = int(row[13])
                hx = row[9][1] if len(row[9]) > 1 else None
                ds, dc = parse_ding(row[43])
                zhupai = row[10]
                bf = row[34].strip()
                last = bf[-1] if bf else ''
                frows.append((zf, dtza, hx, dc, zhupai, last))
            except (ValueError, IndexError):
                continue
    files.append(frows)

total = sum(len(f) for f in files)
print(f'总行数: {total}')

def is_touch(dc):
    return dc == 'a龙'

def is_shengliandian(zp):
    """真正的升排：升.尾连(连续升连)"""
    return zp.startswith('升.尾连')

def again_touch(frows, i, la=5):
    """未来la天内再次触顶(a龙)"""
    for j in range(i+1, min(i+1+la, len(frows))):
        if is_touch(frows[j][3]):
            return True
    return False

def again_shengliandian(frows, i, la=5):
    """未来la天内出现升.尾连"""
    for j in range(i+1, min(i+1+la, len(frows))):
        if is_shengliandian(frows[j][4]):
            return True
    return False

def classify_yin(last, zp):
    if '人' in zp:
        return '阴阳阴(人排)'
    if last == 'v': return '单阴柱(跌孕)'
    if last == 'V': return '单阴柱(跌吞)'
    if last == 'W': return '连阴(跌连)'
    return f'其他({last})'

def bucket_below(n):
    if n <= 3: return f'下破{n}柱'
    if n <= 5: return f'下破{n}柱'
    return '下破6柱+'

# 统计: 类别 -> [n, 触顶, 升连, 触顶或升连]
yin_stats = collections.defaultdict(lambda: [0,0,0,0])
xp_stats = collections.defaultdict(lambda: [0,0,0,0])
base_stats = [0,0,0,0]  # 无回调阳柱基线

for frows in files:
    N = len(frows)
    for i in range(1, N-1):
        zf, dtza, hx, dc, zp, last = frows[i]
        if hx != '甲' or dtza <= 0 or zf <= 0:
            continue
        # 阳柱，扫描前5日找回调
        cb_type = None
        cb_idx = None
        for k in range(i-1, max(i-6, -1), -1):
            if frows[k][1] < 0:
                cb_type = '下破DJA'; cb_idx = k; break
            if frows[k][0] < 0:
                cb_type = '阴柱'; cb_idx = k; break
        t = again_touch(frows, i)
        s = again_shengliandian(frows, i)
        if cb_type is None:
            base_stats[0] += 1
            if t: base_stats[1] += 1
            if s: base_stats[2] += 1
            if t or s: base_stats[3] += 1
        elif cb_type == '阴柱':
            cls = classify_yin(frows[cb_idx][5], frows[cb_idx][4])
            yin_stats[cls][0] += 1
            if t: yin_stats[cls][1] += 1
            if s: yin_stats[cls][2] += 1
            if t or s: yin_stats[cls][3] += 1
        else:
            n_below = 0
            j = cb_idx
            while j >= 0 and frows[j][1] < 0:
                n_below += 1; j -= 1
            col_cls = bucket_below(n_below)
            xp_stats[col_cls][0] += 1
            if t: xp_stats[col_cls][1] += 1
            if s: xp_stats[col_cls][2] += 1
            if t or s: xp_stats[col_cls][3] += 1

def report(title, stats):
    print(f'\n=== {title} ===')
    print(f'{"类别":<20} {"n":>9} {"触顶":>8} {"升连":>8} {"触顶或升连":>12}')
    print('-' * 62)
    for k, (tot, t, s, ts) in sorted(stats.items(), key=lambda x: -x[1][0]):
        if tot:
            print(f'{k:<20} {tot:>9,} {t/tot*100:>7.1f}% {s/tot*100:>7.1f}% {ts/tot*100:>11.1f}%')

print('\n=== 基线：无回调阳柱 ===')
b = base_stats
print(f'{"类别":<20} {"n":>9} {"触顶":>8} {"升连":>8} {"触顶或升连":>12}')
print('-' * 62)
print(f'{"无回调阳柱":<20} {b[0]:>9,} {b[1]/b[0]*100:>7.1f}% {b[2]/b[0]*100:>7.1f}% {b[3]/b[0]*100:>11.1f}%')

report('① 阴柱回调分类', yin_stats)
report('② 下破DJA回调分类', xp_stats)
