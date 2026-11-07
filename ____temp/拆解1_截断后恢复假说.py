# -*- coding: utf-8 -*-
"""拆解1：截断后恢复假说验证
对每次"两线截断"退出，追踪后续N天是否恢复（重新满足介入条件），
对比"截断后重新介入"vs"如果不截断一直持有到下次Z退"的收益。
"""
import csv, sys, io, os, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL_DATE = 0
COL_CLOSE = 1
COL_DXCD = 8
COL_ZDJ = 81

TWO_LINE_BELOW = {'忠', '忑'}
ZD_AH = {'A', 'H'}

def load_rows(filepath):
    try:
        with open(filepath, encoding='gbk') as fp:
            r = csv.reader(fp)
            next(r)
            return list(r)
    except:
        return None

def get_state(row):
    if len(row) <= COL_ZDJ:
        return None, None, None, None
    try:
        close = float(row[COL_CLOSE])
    except:
        return None, None, None, None
    dxcd = row[COL_DXCD]
    zdj = row[COL_ZDJ]
    zdj_first = zdj[0] if len(zdj) > 0 else ''
    return close, dxcd, zdj_first, row[COL_DATE]

def analyze_stock(rows):
    """返回两类交易：
    1. 截断交易：触发两线截断时的买入价、卖出价、以及如果不截断持有到下次Z退的卖出价
    2. 截断后恢复：截断后多少天内重新满足介入条件
    """
    results = []
    in_pos = False
    buy_price = 0.0
    buy_idx = 0
    for i, row in enumerate(rows):
        close, dxcd, zdj_first, date = get_state(row)
        if close is None:
            continue
        if not in_pos:
            if zdj_first in ZD_AH and dxcd not in TWO_LINE_BELOW:
                in_pos = True
                buy_price = close
                buy_idx = i
        else:
            if zdj_first == 'Z':
                # Z退出：记录并继续找下次介入
                in_pos = False
            elif dxcd in TWO_LINE_BELOW:
                # 两线截断：记录截断交易 + 追踪恢复
                cut_sell = close
                cut_ret = (cut_sell - buy_price) / buy_price * 100
                # 追踪如果不截断，持有到下次Z退的卖出价
                hold_sell = None
                hold_ret = None
                for j in range(i+1, len(rows)):
                    c2, d2, z2, _ = get_state(rows[j])
                    if c2 is None:
                        continue
                    if z2 == 'Z':
                        hold_sell = c2
                        hold_ret = (hold_sell - buy_price) / buy_price * 100
                        break
                # 追踪截断后恢复：多少天后重新满足介入条件
                recover_days = None
                recover_price = None
                for j in range(i+1, len(rows)):
                    c2, d2, z2, _ = get_state(rows[j])
                    if c2 is None:
                        continue
                    if z2 == 'Z':
                        break  # 先Z退了，没机会恢复
                    if z2 in ZD_AH and d2 not in TWO_LINE_BELOW:
                        recover_days = j - i
                        recover_price = c2
                        break
                results.append({
                    'cut_ret': cut_ret,
                    'hold_ret': hold_ret,  # 不截断持有到Z退
                    'recover_days': recover_days,
                    'recover_price': recover_price,
                    'cut_sell': cut_sell,
                })
                in_pos = False
    return results

files = sorted(glob.glob('昭明算展/谕组日/谕组日_*.csv'))
t0 = time.time()
all_cut = []
recover_count = 0
no_recover_count = 0
recover_rets = []  # 截断后重新介入的收益
for i, f in enumerate(files):
    rows = load_rows(f)
    if not rows:
        continue
    res = analyze_stock(rows)
    all_cut.extend(res)
    if (i+1) % 1000 == 0:
        print(f'  进度 {i+1}/{len(files)} 用时{time.time()-t0:.0f}s')

n = len(all_cut)
print(f'\n========== 拆解1：截断后恢复假说 ==========')
print(f'两线截断交易总数: {n}')

# 1. 截断交易本身的收益
cut_rets = [r['cut_ret'] for r in all_cut]
print(f'\n--- 截断交易本身 ---')
print(f'平均收益: {sum(cut_rets)/n:+.3f}%  中位: {sorted(cut_rets)[n//2]:+.3f}%')
print(f'胜率: {sum(1 for r in cut_rets if r>0)/n*100:.1f}%')

# 2. 如果不截断，持有到下次Z退的收益
hold_rets = [r['hold_ret'] for r in all_cut if r['hold_ret'] is not None]
nh = len(hold_rets)
print(f'\n--- 如果不截断，持有到下次Z退 ---')
print(f'有对应Z退的: {nh}/{n} ({nh/n*100:.1f}%)')
if nh:
    print(f'平均收益: {sum(hold_rets)/nh:+.3f}%  中位: {sorted(hold_rets)[nh//2]:+.3f}%')
    print(f'胜率: {sum(1 for r in hold_rets if r>0)/nh*100:.1f}%')
    # 对比：截断 vs 不截断
    paired = [(r['cut_ret'], r['hold_ret']) for r in all_cut if r['hold_ret'] is not None]
    better_cut = sum(1 for c, h in paired if c > h)
    print(f'\n--- 配对对比（同一笔交易）---')
    print(f'截断更好: {better_cut}/{nh} ({better_cut/nh*100:.1f}%)')
    print(f'不截断更好: {nh-better_cut}/{nh} ({(nh-better_cut)/nh*100:.1f}%)')
    avg_cut = sum(c for c, h in paired) / nh
    avg_hold = sum(h for c, h in paired) / nh
    print(f'截断平均: {avg_cut:+.3f}%  不截断平均: {avg_hold:+.3f}%  差异: {avg_cut-avg_hold:+.3f}pp')

# 3. 截断后恢复情况
rec = [r for r in all_cut if r['recover_days'] is not None]
norec = [r for r in all_cut if r['recover_days'] is None]
print(f'\n--- 截断后恢复情况 ---')
print(f'恢复（重新满足介入条件）: {len(rec)}/{n} ({len(rec)/n*100:.1f}%)')
print(f'未恢复（直接Z退）: {len(norec)}/{n} ({len(norec)/n*100:.1f}%)')
if rec:
    days = [r['recover_days'] for r in rec]
    print(f'恢复天数: 平均{sum(days)/len(days):.1f}天 中位{sorted(days)[len(days)//2]}天')
    # 恢复的交易：截断时卖出价 vs 恢复时买入价（摩擦成本）
    frictions = [(r['recover_price'] - r['cut_sell']) / r['cut_sell'] * 100 for r in rec if r['recover_price'] and r['cut_sell']]
    nf = len(frictions)
    print(f'摩擦成本（恢复买入价-截断卖出价）: 平均{sum(frictions)/nf:+.3f}% 中位{sorted(frictions)[nf//2]:+.3f}%')
    better_after = sum(1 for x in frictions if x < 0)  # 恢复时价格更低=赚了
    print(f'恢复时价格更低（截断赚了）: {better_after}/{nf} ({better_after/nf*100:.1f}%)')
    print(f'恢复时价格更高（截断亏了摩擦）: {nf-better_after}/{nf} ({(nf-better_after)/nf*100:.1f}%)')
