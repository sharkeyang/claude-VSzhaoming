# -*- coding: utf-8 -*-
"""
等高线分类分析 — 基于 DTZA(日ZA) + 日中符(中符串) + 日顶型(顶型)

分类规则：
DTZA > 0:
  上1: DTZA=1
  上2: DTZA≤4 且 日中符含CDEF
  上4: DTZA>4 且 日中符含CDEF
  上3: DTZA≥2 且 非上2/上4 (日中符=AB)

DTZA < 0: 镜像
  下1: DTZA=-1
  下2: DTZA≥-4 且 日中符含CDEF
  下4: DTZA<-4 且 日中符含CDEF
  下3: DTZA≤-2 且 非下2/下4

DTZA = 0: 零轴
"""

import pandas as pd
import numpy as np
import os, glob, sys
from collections import defaultdict

# === 配置 ===
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')
MAX_FILES = 500  # 抽样500只，够统计意义又不会太慢

# 列名
COL_ZA = '日ZA'
COL_ZC = '日ZC'
COL_ZE = '日ZE'
COL_MID_SYM = '中符串'
COL_TOP = '顶型'
COL_HR = '高幅'
COL_NEXT_HR = '次日高幅'
COL_DXEF = 'DXEF'

def classify_za(row):
    za = row[COL_ZA]
    mid_sym = str(row[COL_MID_SYM]) if pd.notna(row[COL_MID_SYM]) else ''

    if pd.isna(za) or za == '':
        return 'NA'
    za = float(za)

    # 日中符是否含CDEF
    has_cdef = any(c in mid_sym for c in ['C', 'D', 'E', 'F'])

    if za > 0:
        if za == 1:
            return '上1'
        elif za <= 4 and has_cdef:
            return '上2'
        elif za > 4 and has_cdef:
            return '上4'
        elif za >= 2:
            return '上3'
        else:
            return '上0'
    elif za < 0:
        za_abs = abs(za)
        if za == -1:
            return '下1'
        elif za_abs <= 4 and has_cdef:
            return '下2'
        elif za_abs > 4 and has_cdef:
            return '下4'
        elif za_abs >= 2:
            return '下3'
        else:
            return '下0'
    else:
        return '零轴'

def calc_holding_returns(subset, max_hold=30):
    """计算持有期收益（延续性核心指标）"""
    result = {}
    for d in [3, 5, 7, 10, 15, 20, 30]:
        returns = []
        for i in range(len(subset) - d):
            total = sum(subset.iloc[i+j][COL_HR] for j in range(1, d+1) if i+j < len(subset))
            returns.append(total)
        if returns:
            arr = np.array(returns)
            result[f'持有{d}天收益中位'] = np.median(arr)
            result[f'持有{d}天收益平均'] = np.mean(arr)
            result[f'持有{d}天P90'] = np.percentile(arr, 90)
            result[f'持有{d}天胜率'] = (arr > 0).mean()
            result[f'持有{d}天样本'] = len(arr)
    return result

def main():
    # 抽样读取
    pattern = os.path.join(DATA_DIR, '谕组日_*.csv')
    files = sorted(glob.glob(pattern))
    np.random.seed(42)
    if len(files) > MAX_FILES:
        files = list(np.random.choice(files, MAX_FILES, replace=False))

    print(f"抽样 {len(files)} 个CSV文件（共 {len(glob.glob(pattern))} 个）")

    all_rows = []
    for i, fpath in enumerate(files):
        try:
            df = pd.read_csv(fpath, encoding='gbk')
            if COL_ZA not in df.columns:
                continue
            all_rows.append(df)
        except:
            continue
        if (i+1) % 100 == 0:
            print(f"  已读取 {i+1}/{len(files)} ...")

    data = pd.concat(all_rows, ignore_index=True)
    print(f"\n总样本: {len(data):,} 行")

    # 分类
    data['等高线'] = data.apply(classify_za, axis=1)

    # 1. 分布
    print("\n" + "=" * 80)
    print("一、等高线分类分布")
    print("=" * 80)
    cats = ['上1','上2','上3','上4','下1','下2','下3','下4','零轴']
    dist = data['等高线'].value_counts()
    for c in cats:
        n = dist.get(c, 0)
        print(f"  {c}: {n:>10,} ({n/len(data)*100:>5.1f}%)")
    print(f"  NA: {dist.get('NA', 0):>10,} ({dist.get('NA', 0)/len(data)*100:>5.1f}%)")

    # 2. 延续性指标
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

    # 3. 持有期收益（延续性核心）
    print("\n" + "=" * 80)
    print("三、等高线分类 × 持有期收益（延续性核心）")
    print("=" * 80)

    # 只分析主要的6个分类，控制时间
    main_cats = ['上1','上2','上3','上4','下1','下2','下3','下4']
    for c in main_cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 5000:
            print(f"\n  {c} (n={len(sub):,}): 样本太少，跳过持有期分析")
            continue
        # 抽取最多10万行做持有期分析（平衡速度）
        if len(sub) > 100000:
            sub = sub.sample(100000, random_state=42)
        hp = calc_holding_returns(sub.reset_index(drop=True))
        print(f"\n  {c} (n={len(sub):,}):")
        print(f"    {'持有天数':>8} | {'中位收益':>8} | {'平均收益':>8} | {'P90收益':>8} | {'胜率':>6} | {'样本':>8}")
        for d in [3, 5, 7, 10, 15, 20]:
            print(f"    {f'持有{d}天':>8} | {hp.get(f'持有{d}天收益中位', 0):>7.2f}% | {hp.get(f'持有{d}天收益平均', 0):>7.2f}% | {hp.get(f'持有{d}天P90', 0):>7.2f}% | {hp.get(f'持有{d}天胜率', 0):>5.1%} | {hp.get(f'持有{d}天样本', 0):>8,}")

    # 4. 鼎 vs 非鼎 细分（上2和上4）
    print("\n" + "=" * 80)
    print("四、上2/上4 鼎 vs 非鼎 细分")
    print("=" * 80)

    for c in ['上2', '上4']:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        # 根据顶型判断鼎
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
            print(f"    {label} (n={len(grp):,}): →ZE>0={ze:.1%}  →ZC>0={zc:.1%}  下日>2={next2:.1%}  下日平均={next_m:.2f}%")

    # 5. 与DXEF交叉
    print("\n" + "=" * 80)
    print("五、等高线 × DXEF 交叉分析")
    print("=" * 80)
    print(f"{'分类':>6} | {'金银唏':>12} | {'金银唏→ZE>0':>14} | {'金银唏下日>2':>14} | {'嘘尿屎':>12} | {'嘘尿屎→ZE>0':>14} | {'嘘尿屎下日>2':>14}")
    print("-" * 80)

    for c in cats:
        sub = data[data['等高线'] == c]
        if len(sub) < 200:
            continue
        gold = sub[sub[COL_DXEF].str.contains('金|银|唏', na=False)]
        bad = sub[sub[COL_DXEF].str.contains('嘘|尿|屎', na=False)]
        gold_n = len(gold)
        bad_n = len(bad)
        gold_ze = (gold[COL_ZE] > 0).mean() if gold_n > 50 else 0
        gold_next2 = (gold[COL_NEXT_HR] > 2).mean() if gold_n > 50 else 0
        bad_ze = (bad[COL_ZE] > 0).mean() if bad_n > 50 else 0
        bad_next2 = (bad[COL_NEXT_HR] > 2).mean() if bad_n > 50 else 0
        print(f"{c:>6} | {gold_n:>8,} | {gold_ze:>11.1%} | {gold_next2:>11.1%} | {bad_n:>8,} | {bad_ze:>11.1%} | {bad_next2:>11.1%}")

    print("\n分析完成！")

if __name__ == '__main__':
    main()