# -*- coding: utf-8 -*-
"""
重新验证验证3（帐篷=升管）——修正parse_ding后
用户理论：帐篷=甲升管阴后阳反包触顶，本质是升管中的回调反弹
对比不同"触顶"定义：
A. 顶态G（原定义）
B. 核心顶型是触顶型（a龙/b龙/d虎天劫/c雀/e非/f武/e篪/b龙篪）
C. 核心顶型是a龙（最强触顶）
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

TOUCH_DING = {'a龙','b龙','d虎天劫','d虎AZ劫','c雀','e非','f武','e篪','b龙篪'}

# 加载数据
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
                frows.append((zf, dtza, hx, ds, dc))
            except (ValueError, IndexError):
                continue
    files.append(frows)

total = sum(len(f) for f in files)
print(f'总行数: {total}')

def cont_up(frows, i, la=3):
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][1] <= 0:
            return False
    return True

# 场景：甲护型 + 日ZA>0 + 阴柱后阳柱反包
# 分组A: 顶态G vs 非顶态G
# 分组B: 核心顶型触顶型 vs 其他
# 分组C: 核心顶型a龙 vs 其他
stats = {
    'A_touch': [0,0], 'A_notouch': [0,0],
    'B_touch': [0,0], 'B_notouch': [0,0],
    'C_touch': [0,0], 'C_notouch': [0,0],
}
for frows in files:
    for i in range(1, len(frows)-1):
        zf, dtza, hx, ds, dc = frows[i]
        pzf, pdtza, phx, pds, pdc = frows[i-1]
        if hx=='甲' and dtza>0 and zf>0 and pzf<0:
            # 分组A: 顶态G
            if ds=='G':
                stats['A_touch'][1] += 1
                if cont_up(frows, i): stats['A_touch'][0] += 1
            else:
                stats['A_notouch'][1] += 1
                if cont_up(frows, i): stats['A_notouch'][0] += 1
            # 分组B: 核心顶型触顶型
            if dc in TOUCH_DING:
                stats['B_touch'][1] += 1
                if cont_up(frows, i): stats['B_touch'][0] += 1
            else:
                stats['B_notouch'][1] += 1
                if cont_up(frows, i): stats['B_notouch'][0] += 1
            # 分组C: 核心顶型a龙
            if dc=='a龙':
                stats['C_touch'][1] += 1
                if cont_up(frows, i): stats['C_touch'][0] += 1
            else:
                stats['C_notouch'][1] += 1
                if cont_up(frows, i): stats['C_notouch'][0] += 1

print('\n=== 分组A: 顶态G vs 非顶态G ===')
if stats['A_touch'][1]:
    print(f'顶态G(触顶): n={stats["A_touch"][1]}, 未来3日继续升管={stats["A_touch"][0]/stats["A_touch"][1]*100:.1f}%')
if stats['A_notouch'][1]:
    print(f'非顶态G: n={stats["A_notouch"][1]}, 未来3日继续升管={stats["A_notouch"][0]/stats["A_notouch"][1]*100:.1f}%')

print('\n=== 分组B: 核心顶型触顶型 vs 其他 ===')
if stats['B_touch'][1]:
    print(f'触顶型(a龙/b龙/d虎天劫/c雀/e非/f武/e篪/b龙篪): n={stats["B_touch"][1]}, 未来3日继续升管={stats["B_touch"][0]/stats["B_touch"][1]*100:.1f}%')
if stats['B_notouch'][1]:
    print(f'其他顶型: n={stats["B_notouch"][1]}, 未来3日继续升管={stats["B_notouch"][0]/stats["B_notouch"][1]*100:.1f}%')

print('\n=== 分组C: 核心顶型a龙 vs 其他 ===')
if stats['C_touch'][1]:
    print(f'a龙: n={stats["C_touch"][1]}, 未来3日继续升管={stats["C_touch"][0]/stats["C_touch"][1]*100:.1f}%')
if stats['C_notouch'][1]:
    print(f'其他: n={stats["C_notouch"][1]}, 未来3日继续升管={stats["C_notouch"][0]/stats["C_notouch"][1]*100:.1f}%')
