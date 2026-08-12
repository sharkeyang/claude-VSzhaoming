# -*- coding: utf-8 -*-
"""
等高线分类分析 v2 — 修正持有期收益计算
使用收盘价（涨幅累加）计算真正持有期收益
"""

import pandas as pd
import numpy as np
import os, glob, time

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')
MAX_FILES = 500
RANDOM_SEED = 42

# 列名
COL_ZA = '日ZA'
COL_ZC = '日ZC'
COL_ZE = '日ZE'
COL_MID_SYM = '中符串'
COL_TOP = '顶型'
COL_HR = '高幅'
COL_PR = '涨幅'
COL_NEXT_HR = '次日高幅'
COL_DXEF = 'DXEF'
COL_DXCD = 'DXCD'


def classify_za(za, mid_sym):
    if pd.isna(za) or za == '':
        return 'NA'
    za = float(za)
    mid_sym = str(mid_sym) if pd.notna(mid_sym) else ''
    has_cdef = any(c in mid_sym for c in ['C', 'D', 'E', 'F'])

    if za > 0:
        if za == 1: return '上1'
        elif za <= 4 and has_cdef: return '上2'
        elif za > 4 and has_cdef: return '上4'
        elif za >= 2: return '上3'
        else: return '上0'
    elif za < 0:
        za_abs = abs(za)
        if za == -1: return '下1'
        elif za_abs <= 4 and has_cdef: return '下2'
        elif za_abs > 4 and has_cdef: return '下4'
        elif za_abs >= 2: return '下3'
        else: return '下0'
    else:
        return '零轴'


def calc_forward_returns(df, max_days=30):
    """在同一只股票内计算前向N天累积收益（涨幅累加）"""
    for d in [3, 5, 7, 10, 15, 20, 30]:
        col = f'fwd_{d}d'
        if d <= max_days:
            df[col] = df[COL_PR].shift(-d).rolling(d).sum().shift(-(d-1))
        else:
            df[col] = np.nan
    return df


def main():
    np.random.seed(RANDOM_SEED)
    t0 = time.time()

    pattern = os.path.join(DATA_DIR, '谕组日_*.csv')
    all_files = sorted(glob.glob(pattern))
    print(f"共 {len(all_files)} 个CSV文件")

    if len(all_files) > MAX_FILES:
        files = list(np.random.choice(all_files, MAX_FILES, replace=False))
    else:
        files = all_files
    print(f"抽样 {len(files)} 个文件")

    # 逐文件读取+分类（避免跨股票边界错误）
    all_rows = []
    for i, fpath in enumerate(files):
        try:
            df = pd.read_csv(fpath, encoding='gbk')
            if COL_ZA not in df.columns or len(df) < 5:
                continue
            # 分类
            df['等高线'] = df.apply(lambda r: classify_za(r[COL_ZA], r[COL_MID_SYM]), axis=1)
            # 计算前向收益（在同一只股票内）
            df = calc_forward_returns(df)
            all_rows.append(df)
        except Exception as e:
            continue
        if (i+1) % 100 == 0:
            print(f"  已处理 {i+1}/{len(files)} ({time.time()-t0:.0f}s)")

    data = pd.concat(all_rows, ignore_index=True)
    print(f"\n总样本: {len(data):,} 行, 耗时 {time.time()-t0:.0f}s")

    cats = ['上1', '上2', '上3', '上4', '下1', '下2', '下3', '下4', '零轴']
    main_cats = ['上1', '上2', '上3', '上4', '下1', '下2', '下4']

    # ========== 1. 分布 ==========
    print("\n" + "=" * 80)
    print("一、等高线分类分布")
    print("=" * 80)
    dist = data['等高线'].value_counts()
    for c in cats:
        n = dist.get(c, 0)
        print(f"  {c}: {n:>10,} ({n/len(data)*100:>5.1f}%)")

    # ========== 2. 延续性指标 ==========
    print("\n" + "=" * 80)
    print("二、等高线分类 × 延续性指标")
    print("=" * 80)
    print(f"{'分类':>6} | {'样本':>8} | {'→ZE>0':>8} | {'→ZE+ZC>0':>8} | {'下日>2':>8} | {'下日平均':>8} | {'下日中位':>8}")
    print("-" * 80)

    summary = []
    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        row = {'分类': c, '样本': len(sub)}
        row['→ZE>0'] = (sub[COL_ZE] > 0).mean()
        row['→ZE>0+ZC>0'] = ((sub[COL_ZE] > 0) & (sub[COL_ZC] > 0)).mean()
        row['下日>2'] = (sub[COL_NEXT_HR] > 2).mean()
        row['下日平均'] = sub[COL_NEXT_HR].mean()
        row['下日中位'] = sub[COL_NEXT_HR].median()
        summary.append(row)
        print(f"{row['分类']:>6} | {row['样本']:>8,} | {row['→ZE>0']:>7.1%} | {row['→ZE>0+ZC>0']:>7.1%} | {row['下日>2']:>7.1%} | {row['下日平均']:>7.2f}% | {row['下日中位']:>7.2f}%")

    # ========== 3. 持有期收益（修正后用涨幅累加） ==========
    print("\n" + "=" * 80)
    print("三、等高线分类 × 持有期收益（修正版 — 涨幅累加）")
    print("=" * 80)

    for c in main_cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 5000:
            print(f"\n  {c} (n={len(sub):,}): 样本太少，跳过")
            continue
        if len(sub) > 100000:
            sub = sub.sample(100000, random_state=RANDOM_SEED)

        print(f"\n  {c} (n={len(sub):,}):")
        print(f"    {'持有天数':>8} | {'中位收益':>8} | {'平均收益':>8} | {'P90收益':>8} | {'胜率(>0)':>8} | {'样本':>8}")
        for d in [3, 5, 7, 10, 15, 20]:
            col = f'fwd_{d}d'
            vals = sub[col].dropna()
            if len(vals) < 100:
                continue
            med = np.median(vals)
            avg = np.mean(vals)
            p90 = np.percentile(vals, 90)
            win = (vals > 0).mean()
            print(f"    {f'持有{d}天':>8} | {med:>7.2f}% | {avg:>7.2f}% | {p90:>7.2f}% | {win:>7.1%} | {len(vals):>8,}")

    # ========== 4. 鼎 vs 非鼎 细分（上2/上4） ==========
    print("\n" + "=" * 80)
    print("四、上2/上4 鼎 vs 非鼎 细分")
    print("=" * 80)

    for c in ['上2', '上4']:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        ding = sub[sub[COL_TOP].str.contains('鼎', na=False)]
        noding = sub[~sub[COL_TOP].str.contains('鼎', na=False)]
        print(f"\n  {c} (n={len(sub):,}):")
        for label, grp in [('鼎', ding), ('非鼎', noding)]:
            if len(grp) < 50:
                continue
            ze = (grp[COL_ZE] > 0).mean()
            zc = (grp[COL_ZC] > 0).mean()
            next2 = (grp[COL_NEXT_HR] > 2).mean()
            next_m = grp[COL_NEXT_HR].mean()
            # 持有期
            hp7 = grp['fwd_7d'].dropna()
            hp7_m = hp7.median() if len(hp7) > 50 else 0
            hp7_p90 = np.percentile(hp7, 90) if len(hp7) > 50 else 0
            print(f"    {label} (n={len(grp):,}): →ZE>0={ze:.1%}  →ZC>0={zc:.1%}  下日>2={next2:.1%}  "
                  f"下日平均={next_m:.2f}%  持7天中位={hp7_m:.2f}%  P90={hp7_p90:.2f}%")

    # ========== 5. 与DXEF交叉 ==========
    print("\n" + "=" * 80)
    print("五、等高线 × DXEF 交叉分析")
    print("=" * 80)
    print(f"{'分类':>6} | {'金银唏':>10} | {'→ZE>0':>10} | {'下日>2':>10} | {'嘘尿屎':>10} | {'→ZE>0':>10} | {'下日>2':>10}")
    print("-" * 80)

    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        gold = sub[sub[COL_DXEF].str.contains('金|银|唏', na=False)]
        bad = sub[sub[COL_DXEF].str.contains('嘘|尿|屎', na=False)]
        gold_n, bad_n = len(gold), len(bad)
        g_ze = (gold[COL_ZE] > 0).mean() if gold_n > 50 else 0
        g_n2 = (gold[COL_NEXT_HR] > 2).mean() if gold_n > 50 else 0
        b_ze = (bad[COL_ZE] > 0).mean() if bad_n > 50 else 0
        b_n2 = (bad[COL_NEXT_HR] > 2).mean() if bad_n > 50 else 0
        print(f"{c:>6} | {gold_n:>8,} | {g_ze:>7.1%} | {g_n2:>7.1%} | {bad_n:>8,} | {b_ze:>7.1%} | {b_n2:>7.1%}")

    # ========== 6. 与DXCD交叉 ==========
    print("\n" + "=" * 80)
    print("六、等高线 × DXCD 交叉（上1中看DXCD区分度）")
    print("=" * 80)

    for c in ['上1', '上2']:
        sub = data[data['等高线'] == c]
        if len(sub) < 500:
            continue
        for dxcd_val in ['上', '中', '下', '忐', '忠', '忑']:
            grp = sub[sub[COL_DXCD].str.contains(dxcd_val, na=False)]
            if len(grp) < 50:
                continue
            ze = (grp[COL_ZE] > 0).mean()
            n2 = (grp[COL_NEXT_HR] > 2).mean()
            hp7 = grp['fwd_7d'].dropna()
            hp7_m = hp7.median() if len(hp7) > 50 else 0
            print(f"  {c}/DXCD={dxcd_val}: n={len(grp):,}  →ZE>0={ze:.1%}  下日>2={n2:.1%}  持7天中位={hp7_m:.2f}%")

    print(f"\n分析完成！总耗时 {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()