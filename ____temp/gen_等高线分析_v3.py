# -*- coding: utf-8 -*-
"""
等高线分析 v3 — 以下日DSHR为核心指标
"""

import pandas as pd
import numpy as np
import os, glob, time

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')
MAX_FILES = 500
RANDOM_SEED = 42

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


def main():
    np.random.seed(RANDOM_SEED)
    t0 = time.time()

    pattern = os.path.join(DATA_DIR, '谕组日_*.csv')
    all_files = sorted(glob.glob(pattern))
    if len(all_files) > MAX_FILES:
        files = list(np.random.choice(all_files, MAX_FILES, replace=False))
    else:
        files = all_files
    print(f"抽样 {len(files)}/{len(all_files)} 个文件")

    all_rows = []
    for i, fpath in enumerate(files):
        try:
            df = pd.read_csv(fpath, encoding='gbk')
            if COL_ZA not in df.columns or len(df) < 5:
                continue
            df['等高线'] = df.apply(lambda r: classify_za(r[COL_ZA], r[COL_MID_SYM]), axis=1)
            # 前向持有期收益
            for d in [3, 5, 7, 10, 15, 20]:
                df[f'fwd_{d}d'] = df[COL_PR].shift(-d).rolling(d).sum().shift(-(d-1))
            all_rows.append(df)
        except:
            continue
        if (i+1) % 100 == 0:
            print(f"  已处理 {i+1}/{len(files)} ({time.time()-t0:.0f}s)")

    data = pd.concat(all_rows, ignore_index=True)
    print(f"\n总样本: {len(data):,} 行, {time.time()-t0:.0f}s")

    cats = ['上1', '上2', '上3', '上4', '下1', '下2', '下4']

    # ========== 1. 分布 ==========
    print("\n" + "=" * 80)
    print("一、等高线分类分布")
    print("=" * 80)
    dist = data['等高线'].value_counts()
    for c in cats:
        n = dist.get(c, 0)
        print(f"  {c}: {n:>10,} ({n/len(data)*100:>5.1f}%)")

    # ========== 2. 下日DSHR全分布 ==========
    print("\n" + "=" * 80)
    print("二、等高线 × 下日DSHR 全分布")
    print("=" * 80)
    print(f"{'分类':>6} | {'样本':>8} | {'下日>0':>8} | {'下日>1':>8} | {'下日>2':>8} | {'下日>3':>8} | {'下日>5':>8} | {'下日>8':>8} | {'下日平均':>8} | {'下日中位':>8} | {'P90':>8} | {'P95':>8}")
    print("-" * 110)
    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        nh = sub[COL_NEXT_HR]
        print(f"{c:>6} | {len(sub):>8,} | {(nh>0).mean():>7.1%} | {(nh>1).mean():>7.1%} | {(nh>2).mean():>7.1%} | {(nh>3).mean():>7.1%} | {(nh>5).mean():>7.1%} | {(nh>8).mean():>7.1%} | {nh.mean():>7.2f}% | {nh.median():>7.2f}% | {np.percentile(nh,90):>7.2f}% | {np.percentile(nh,95):>7.2f}%")

    # ========== 3. 持有期收益（DSHR累加方式） ==========
    print("\n" + "=" * 80)
    print("三、等高线 × 持有期DSHR（高幅累加，真实收益上限）")
    print("=" * 80)

    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 5000:
            continue
        if len(sub) > 100000:
            sub = sub.sample(100000, random_state=RANDOM_SEED)
        print(f"\n  {c} (n={len(sub):,}):")
        print(f"    {'持有天数':>8} | {'中位DSHR':>8} | {'平均DSHR':>8} | {'P90 DSHR':>8} | {'P95 DSHR':>8} | {'DSHR>5%':>8} | {'DSHR>10%':>8} | {'样本':>8}")
        for d in [3, 5, 7, 10, 15, 20]:
            col = f'fwd_{d}d'
            vals = sub[col].dropna()
            if len(vals) < 100:
                continue
            med = np.median(vals)
            avg = np.mean(vals)
            p90 = np.percentile(vals, 90)
            p95 = np.percentile(vals, 95)
            gt5 = (vals > 5).mean()
            gt10 = (vals > 10).mean()
            print(f"    {f'持有{d}天':>8} | {med:>7.2f}% | {avg:>7.2f}% | {p90:>7.2f}% | {p95:>7.2f}% | {gt5:>7.1%} | {gt10:>7.1%} | {len(vals):>8,}")

    # ========== 4. 鼎 vs 非鼎 细分 ==========
    print("\n" + "=" * 80)
    print("四、鼎 vs 非鼎 细分（所有分类）")
    print("=" * 80)
    print(f"{'分类':>6} | {'鼎':>6} | {'下日>2':>8} | {'下日>5':>8} | {'下日平均':>8} | {'持7天中位':>8} | {'非鼎':>6} | {'下日>2':>8} | {'下日>5':>8} | {'下日平均':>8} | {'持7天中位':>8}")
    print("-" * 110)
    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        ding = sub[sub[COL_TOP].str.contains('鼎', na=False)]
        noding = sub[~sub[COL_TOP].str.contains('鼎', na=False)]
        if len(ding) < 50:
            print(f"{c:>6} | {'—':>6} | {'—':>8} | {'—':>8} | {'—':>8} | {'—':>8} | {len(noding):>6,} | {(noding[COL_NEXT_HR]>2).mean():>7.1%} | {(noding[COL_NEXT_HR]>5).mean():>7.1%} | {noding[COL_NEXT_HR].mean():>7.2f}% | {noding['fwd_7d'].dropna().median():>7.2f}%")
        else:
            d_n2 = (ding[COL_NEXT_HR] > 2).mean()
            d_n5 = (ding[COL_NEXT_HR] > 5).mean()
            d_avg = ding[COL_NEXT_HR].mean()
            d_hp7 = ding['fwd_7d'].dropna().median()
            nd_n2 = (noding[COL_NEXT_HR] > 2).mean()
            nd_n5 = (noding[COL_NEXT_HR] > 5).mean()
            nd_avg = noding[COL_NEXT_HR].mean()
            nd_hp7 = noding['fwd_7d'].dropna().median()
            print(f"{c:>6} | {len(ding):>6,} | {d_n2:>7.1%} | {d_n5:>7.1%} | {d_avg:>7.2f}% | {d_hp7:>7.2f}% | {len(noding):>6,} | {nd_n2:>7.1%} | {nd_n5:>7.1%} | {nd_avg:>7.2f}% | {nd_hp7:>7.2f}%")

    # ========== 5. 上1/上2 × DXCD 交叉 ==========
    print("\n" + "=" * 80)
    print("五、等高线 × DXCD 交叉（以下日DSHR为核心）")
    print("=" * 80)
    for c in ['上1', '上2', '上3', '上4']:
        sub = data[data['等高线'] == c]
        if len(sub) < 500:
            continue
        print(f"\n  {c}:")
        print(f"    {'DXCD':>6} | {'样本':>8} | {'→ZE>0':>8} | {'下日>2':>8} | {'下日>5':>8} | {'下日平均':>8} | {'P90下日':>8} | {'持7天中位':>8}")
        for dxcd_val in ['上', '中', '下', '忐', '忠', '忑']:
            grp = sub[sub[COL_DXCD].str.contains(dxcd_val, na=False)]
            if len(grp) < 50:
                continue
            ze = (grp[COL_ZE] > 0).mean()
            n2 = (grp[COL_NEXT_HR] > 2).mean()
            n5 = (grp[COL_NEXT_HR] > 5).mean()
            navg = grp[COL_NEXT_HR].mean()
            n90 = np.percentile(grp[COL_NEXT_HR], 90)
            hp7 = grp['fwd_7d'].dropna().median()
            print(f"    {dxcd_val:>6} | {len(grp):>8,} | {ze:>7.1%} | {n2:>7.1%} | {n5:>7.1%} | {navg:>7.2f}% | {n90:>7.2f}% | {hp7:>7.2f}%")

    # ========== 6. 等高线 × 上日ZE/ZD 交叉 ==========
    # 看是否在DXZE>0和DXZE<0时，等高线的区分度不同
    print("\n" + "=" * 80)
    print("六、等高线 × 日ZE 交叉（ZE>0 vs ZE≤0 下的DSHR表现）")
    print("=" * 80)
    print(f"{'分类':>6} | {'ZE>0':>8} | {'下日>2':>8} | {'下日>5':>8} | {'下日平均':>8} | {'P90':>8} | {'ZE≤0':>8} | {'下日>2':>8} | {'下日>5':>8} | {'下日平均':>8} | {'P90':>8}")
    print("-" * 110)
    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        ze_pos = sub[sub[COL_ZE] > 0]
        ze_neg = sub[sub[COL_ZE] <= 0]
        if len(ze_pos) > 50:
            pn2 = (ze_pos[COL_NEXT_HR] > 2).mean()
            pn5 = (ze_pos[COL_NEXT_HR] > 5).mean()
            pavg = ze_pos[COL_NEXT_HR].mean()
            pp90 = np.percentile(ze_pos[COL_NEXT_HR], 90)
        else:
            pn2 = pn5 = pavg = pp90 = 0
        if len(ze_neg) > 50:
            nn2 = (ze_neg[COL_NEXT_HR] > 2).mean()
            nn5 = (ze_neg[COL_NEXT_HR] > 5).mean()
            navg = ze_neg[COL_NEXT_HR].mean()
            np90 = np.percentile(ze_neg[COL_NEXT_HR], 90)
        else:
            nn2 = nn5 = navg = np90 = 0
        print(f"{c:>6} | {len(ze_pos):>6,} | {pn2:>7.1%} | {pn5:>7.1%} | {pavg:>7.2f}% | {pp90:>7.2f}% | {len(ze_neg):>6,} | {nn2:>7.1%} | {nn5:>7.1%} | {navg:>7.2f}% | {np90:>7.2f}%")

    # ========== 7. 下日DSHR 分布直方（按分类） ==========
    print("\n" + "=" * 80)
    print("七、下日DSHR 分布直方图（按分类）")
    print("=" * 80)
    bins = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 15, 20]
    bin_labels = ['0~0.5', '0.5~1', '1~1.5', '1.5~2', '2~2.5', '2.5~3', '3~4', '4~5', '5~6', '6~8', '8~10', '10~15', '15~20']
    print(f"{'分类':>6} | {'样本':>8} | {'0~0.5':>8} | {'0.5~1':>8} | {'1~1.5':>8} | {'1.5~2':>8} | {'2~2.5':>8} | {'2.5~3':>8} | {'3~4':>8} | {'4~5':>8} | {'5~6':>8} | {'6~8':>8} | {'8~10':>8} | {'10~15':>8} | {'15~20':>8}")
    print("-" * 130)
    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        nh = sub[COL_NEXT_HR]
        hist_counts = []
        for i in range(len(bins)-1):
            cnt = ((nh > bins[i]) & (nh <= bins[i+1])).sum()
            pct = cnt / len(sub) * 100
            hist_counts.append(pct)
        print(f"{c:>6} | {len(sub):>8,} | " + " | ".join(f"{h:>6.1f}%" for h in hist_counts))

    print(f"\n分析完成！耗时 {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()