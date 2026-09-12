# -*- coding: utf-8 -*-
"""
位os基顶型 确认阶梯型上升路径 验证
====================================================
用户假设：a龙、b龙、d虎 且未下破DJA（日ZA>0），都可能是阶梯型上升路径。

阶梯型上升 = 价格像台阶逐级上升（涨一段→回调→再涨一段），而非直线拉升。
验证指标：
  ① 各顶型 P(≥3%)/均高幅（DXZC>0 + 日ZA>0）
  ② 各顶型 持续天数（阶梯型应持续较久）
  ③ 后续创新高概率（阶梯型回调后应能再创新高）
  ④ 对比 a龙/b龙/d虎 vs c雀/e非/e篪/f武

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅, 43=顶型
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

def to_f(v):
    try: return float(v)
    except: return None

def core_dx(dx):
    """提取核心顶型：a龙/b龙/c雀/d虎/e非/f武/e篪"""
    s = dx.strip()
    if 'a龙' in s: return 'a龙'
    if 'b龙' in s: return 'b龙'
    if 'd虎' in s: return 'd虎'
    if 'c雀' in s: return 'c雀'
    if 'e非' in s: return 'e非'
    if 'f武' in s: return 'f武'
    if 'e篪' in s: return 'e篪'
    return '其他'

# 统计: 顶型 -> [n, hr3, sum_hr, 持续天数累计]
stats = defaultdict(lambda: [0, 0, 0.0, 0])
# 创新高统计: 顶型 -> [n, 创新高数]
newhigh = defaultdict(lambda: [0, 0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    rows = []
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 43: continue
                rows.append(row)
    except Exception:
        continue
    # 逐行处理
    for idx, row in enumerate(rows):
        dxcd = row[8].strip()
        za = to_f(row[13])
        zc = to_f(row[14])
        hr = to_f(row[26])
        if za is None or hr is None: continue
        if hr < -50 or hr > 50: continue
        # 条件：DXZC>0 + 日ZA>0（未下破DJA）
        if zc is None or zc <= 0 or za <= 0: continue
        dx = core_dx(row[43])
        stats[dx][0] += 1
        stats[dx][1] += (1 if hr >= 3 else 0)
        stats[dx][2] += hr
        # 持续天数：连续同顶型
        # 创新高：后续5天内是否创新高（用后续最高价 vs 当前收盘）
        # 简化：用后续5天最高收盘 vs 当前收盘
        if idx + 5 < len(rows):
            cur_close = to_f(rows[idx][1])
            if cur_close is not None:
                fut_high = max(to_f(rows[j][3]) for j in range(idx+1, min(idx+6, len(rows))) if to_f(rows[j][3]) is not None)
                if fut_high is not None:
                    newhigh[dx][0] += 1
                    if fut_high > cur_close:
                        newhigh[dx][1] += 1

print(f'高波池文件: {files_core}')
print()

# 持续天数：需要单独统计连续同顶型run
# 重新统计持续天数
dur = defaultdict(list)
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    cur_dx = None; cur_len = 0
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 43: continue
                za = to_f(row[13]); zc = to_f(row[14])
                if za is None or zc is None: continue
                if zc <= 0 or za <= 0:
                    if cur_dx is not None:
                        dur[cur_dx].append(cur_len); cur_dx=None; cur_len=0
                    continue
                dx = core_dx(row[43])
                if dx == cur_dx:
                    cur_len += 1
                else:
                    if cur_dx is not None:
                        dur[cur_dx].append(cur_len)
                    cur_dx = dx; cur_len = 1
            if cur_dx is not None:
                dur[cur_dx].append(cur_len)
    except Exception:
        pass

print('=' * 78)
print('① 各顶型 P(≥3%)/均高幅（DXZC>0 + 日ZA>0 未下破DJA）')
print('=' * 78)
print(f'{"顶型":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"持续天数":>8} {"5日创新高":>10}')
print('-' * 60)
order = ['a龙', 'b龙', 'd虎', 'c雀', 'e非', 'e篪', 'f武']
for dx in order:
    s = stats[dx]
    if s[0] == 0: continue
    d = dur[dx]
    avg_dur = sum(d)/len(d) if d else 0
    nh = newhigh[dx]
    nh_pct = nh[1]/nh[0]*100 if nh[0] else 0
    print(f'{dx:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {avg_dur:>7.1f}天 {nh_pct:>9.1f}%')

print()
print('=' * 78)
print('② 阶梯型上升验证：a龙/b龙/d虎 vs 其他')
print('=' * 78)
for grp, members in [('阶梯候选(a龙/b龙/d虎)', ['a龙','b龙','d虎']), ('其他(c雀/e非/e篪/f武)', ['c雀','e非','e篪','f武'])]:
    n=sum(stats[m][0] for m in members)
    hr3=sum(stats[m][1] for m in members)
    hr=sum(stats[m][2] for m in members)
    d=sum(len(dur[m]) for m in members)
    dd=sum(sum(dur[m]) for m in members)
    nh_n=sum(newhigh[m][0] for m in members)
    nh_h=sum(newhigh[m][1] for m in members)
    print(f'{grp}: n={n:,} P(≥3%)={hr3/n*100:.2f}% 均高幅={hr/n:.2f}% 持续={dd/d:.1f}天 5日创新高={nh_h/nh_n*100:.1f}%' if nh_n else f'{grp}: n={n:,} P(≥3%)={hr3/n*100:.2f}% 均高幅={hr/n:.2f}% 持续={dd/d:.1f}天')
