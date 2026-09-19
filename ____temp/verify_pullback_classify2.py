# -*- coding: utf-8 -*-
"""
回调分类 v2：阴柱回调 / 下破DJA回调 的细分
====================================================
修正：阴柱 = 涨幅[5]<0 = 并符串[34]末位 ∈ {W跌连, V跌吞, v跌孕}
     阳柱 = 涨幅[5]>=0 = 并符串[34]末位 ∈ {Q升连, O升吞, o升孕}
     （已验证 100% 一致）

背景：
  甲护型 + 升管(日ZA>0) + 阳柱(zf>0)，前5日内有回调
  阴柱回调: n=162万, 再次触顶/升排=96.3%
  下破DJA回调: n=70.4万, 再次触顶/升排=99.6%

本次分类：
  ① 阴柱回调 → 按回调阴柱的并符末位分类：
      单阴柱(跌孕v) / 单阴柱(跌吞V) / 连阴(跌连W) / 阴阳阴(人排) / 其他
  ② 下破DJA回调 → 按下破柱数分类：
      下破1柱 / 2柱 / 3柱 / 4柱 / 5柱 / 6柱+ / 其他
  ③ 下破DJA回调 → 下破期间(DXZA<0)柱排是否出现 升连/升吞/升孕
  ④ 下破柱数 × 下破期间柱排

指标：未来5日再次触顶(a龙)或升排概率
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
            if len(row) < 35:
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

def is_shengpai(zp):
    return zp.startswith('升') or zp.startswith('(升)')

def again_signal(frows, i, la=5):
    """未来la天内再次触顶(a龙)或升排"""
    for j in range(i+1, min(i+1+la, len(frows))):
        if is_touch(frows[j][3]) or is_shengpai(frows[j][4]):
            return True
    return False

def classify_yin(last, zp):
    """阴柱回调：按回调阴柱的并符末位分类"""
    if '人' in zp:
        return '阴阳阴(人排)'
    if last == 'v': return '单阴柱(跌孕)'
    if last == 'V': return '单阴柱(跌吞)'
    if last == 'W': return '连阴(跌连)'
    return f'其他({last})'

def classify_xp_zp(zp):
    """下破期间柱排：是否升连/升吞/升孕"""
    s = zp.strip()
    if '人' in s:
        return '人排'
    if s.startswith('升'):
        if '尾连' in s: return '升连'
        if '反孕' in s: return '升孕'
        if '尾吞' in s or '连后吞' in s: return '升吞'
    if s.startswith('跌'):
        if '尾连' in s: return '跌连'
        if '反孕' in s: return '跌孕'
        if '尾吞' in s or '连后吞' in s: return '跌吞'
    return '其他'

def bucket_below(n):
    if n <= 3: return f'下破{n}柱'
    if n <= 5: return f'下破{n}柱'
    return '下破6柱+'

# 统计
yin_stats = collections.defaultdict(lambda: [0, 0])   # 阴柱回调分类
xp_stats = collections.defaultdict(lambda: [0, 0])    # 下破柱数
xp_zp_stats = collections.defaultdict(lambda: [0, 0]) # 下破期间柱排
xp_zp_by_col = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))  # 下破柱数 × 柱排

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
            if frows[k][1] < 0:  # 下破DJA
                cb_type = '下破DJA'
                cb_idx = k
                break
            if frows[k][0] < 0:  # 阴柱
                cb_type = '阴柱'
                cb_idx = k
                break
        if cb_type is None:
            continue
        sig = again_signal(frows, i)
        if cb_type == '阴柱':
            cls = classify_yin(frows[cb_idx][5], frows[cb_idx][4])
            yin_stats[cls][0] += 1
            if sig: yin_stats[cls][1] += 1
        else:  # 下破DJA
            # 统计下破柱数：从 cb_idx 往前数连续 dtza<0
            n_below = 0
            j = cb_idx
            while j >= 0 and frows[j][1] < 0:
                n_below += 1
                j -= 1
            col_cls = bucket_below(n_below)
            xp_stats[col_cls][0] += 1
            if sig: xp_stats[col_cls][1] += 1
            # 下破期间柱排（取下破段内所有柱排，看是否出现升连/升吞/升孕）
            zps = set()
            for j in range(cb_idx - n_below + 1, cb_idx + 1):
                zps.add(classify_xp_zp(frows[j][4]))
            has_sheng = any(z in ('升连', '升吞', '升孕') for z in zps)
            if has_sheng:
                xp_zp_stats['有升连/升吞/升孕'][0] += 1
                if sig: xp_zp_stats['有升连/升吞/升孕'][1] += 1
            else:
                xp_zp_stats['无升连/升吞/升孕'][0] += 1
                if sig: xp_zp_stats['无升连/升吞/升孕'][1] += 1
            for z in zps:
                xp_zp_by_col[col_cls][z][0] += 1
                if sig: xp_zp_by_col[col_cls][z][1] += 1

def report(title, stats):
    print(f'\n=== {title} ===')
    print(f'{"类别":<22} {"n":>10} {"再次触顶/升排":>14}')
    print('-' * 50)
    for k, (tot, sig) in sorted(stats.items(), key=lambda x: -x[1][0]):
        if tot:
            print(f'{k:<22} {tot:>10,} {sig/tot*100:>13.1f}%')

report('① 阴柱回调分类（按回调阴柱并符末位）', yin_stats)
report('② 下破DJA回调分类（按下破柱数）', xp_stats)
report('③ 下破DJA回调（下破期间是否出现升连/升吞/升孕）', xp_zp_stats)

print(f'\n=== ④ 下破柱数 × 下破期间柱排 ===')
for col in ['下破1柱', '下破2柱', '下破3柱', '下破4柱', '下破5柱', '下破6柱+']:
    if col not in xp_zp_by_col: continue
    print(f'\n-- {col} --')
    print(f'{"柱排":<22} {"n":>10} {"再次触顶/升排":>14}')
    print('-' * 50)
    for z, (tot, sig) in sorted(xp_zp_by_col[col].items(), key=lambda x: -x[1][0]):
        if tot:
            print(f'{z:<22} {tot:>10,} {sig/tot*100:>13.1f}%')
