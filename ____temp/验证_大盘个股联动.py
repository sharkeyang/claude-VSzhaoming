#!/usr/bin/env python3
"""验证大盘DXZC/DXZA与个股走势的关系 — 读取CSV分析"""
import csv
from collections import Counter

CSV_PATH = r"D:\@VSwork\VS昭明计划VBA优化\____temp\大盘个股联动.csv"

def main():
    # 读取CSV
    data = []  # [(cidl, name, 日冲策分, 仓周类首字, 月基带周, 月基带日, 策略, 是宽基)]
    with open(CSV_PATH, 'r', encoding='gbk') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or not row[0]:
                continue
            cidl = row[0]
            name = row[1] if len(row) > 1 else ""
            ri_chong = float(row[2]) if len(row) > 2 and row[2] else None
            cang_zhou = row[3] if len(row) > 3 else ""
            dai_zhou = row[4] if len(row) > 4 else ""
            dai_ri = row[5] if len(row) > 5 else ""
            ce_lue = row[6] if len(row) > 6 else ""
            is_wide = row[7] if len(row) > 7 else ""
            cang_zhou_first = cang_zhou[0] if cang_zhou else ""
            data.append((cidl, name, ri_chong, cang_zhou_first, dai_zhou, dai_ri, ce_lue, is_wide))

    print(f"读取 {len(data)} 行数据")

    # 分离指数和个股
    indexes = [d for d in data if d[7] == "是"]
    stocks = [d for d in data if d[7] != "是"]

    print(f"\n指数: {len(indexes)} 个")
    for idx in indexes:
        print(f"  {idx[0]} {idx[1]} 日冲策分={idx[2]} 仓周类={idx[3]} 月基带周={idx[4]}")

    print(f"\n个股: {len(stocks)} 个")

    # 分类: 仓周类首字 金/银=好, 唏/嘘=中, 屎/尿=坏
    def classify(cang_zhou_first):
        if cang_zhou_first in ("金", "银"):
            return "好"
        elif cang_zhou_first in ("屎", "尿"):
            return "坏"
        else:
            return "中"

    # 个股整体分布
    stock_classes = Counter()
    for s in stocks:
        stock_classes[classify(s[3])] += 1

    print(f"\n个股整体分布:")
    total = sum(stock_classes.values())
    for cls in ["好", "中", "坏"]:
        pct = stock_classes[cls] / total * 100 if total else 0
        print(f"  {cls}: {stock_classes[cls]}({pct:.1f}%)")

    # 从月基带周提取促动方向
    # 格式: (护级)促动(护级)，位置4(0-index=3)是第一个促动
    def get_promote(dai_zhou):
        if len(dai_zhou) >= 4:
            return dai_zhou[3]
        return ""

    def promote_score(p):
        if p in ("▲", "↗"):
            return "好"
        elif p in ("↘", "▽"):
            return "坏"
        else:
            return "中"

    idx_promotes = [get_promote(d[4]) for d in indexes]
    print(f"\n指数月基带周促动: {idx_promotes}")

    bad_count = sum(1 for p in idx_promotes if promote_score(p) == "坏")
    good_count = sum(1 for p in idx_promotes if promote_score(p) == "好")

    print(f"指数坏方向: {bad_count}/3, 好方向: {good_count}/3")

    # 用日冲策分判断
    idx_scores = [d[2] for d in indexes if d[2] is not None]
    print(f"指数日冲策分: {idx_scores}")
    low_count = sum(1 for s in idx_scores if s < 50)
    high_count = sum(1 for s in idx_scores if s >= 50)

    # 交叉分析1: 指数促动方向 vs 个股
    print(f"\n{'='*50}")
    print(f"方法一: 月基带周促动方向")
    print(f"{'='*50}")

    if bad_count >= 2:
        # 指数方向坏时，个股分布
        cls_bad = Counter()
        for s in stocks:
            cls_bad[classify(s[3])] += 1
        print(f"\n当 {bad_count}/3 指数方向为坏时:")
        for cls in ["好", "中", "坏"]:
            pct = cls_bad[cls] / total * 100 if total else 0
            print(f"  个股{cls}: {cls_bad[cls]}({pct:.1f}%)")

    if good_count >= 2:
        # 指数方向好时，个股分布
        cls_good = Counter()
        for s in stocks:
            cls_good[classify(s[3])] += 1
        print(f"\n当 {good_count}/3 指数方向为好时:")
        for cls in ["好", "中", "坏"]:
            pct = cls_good[cls] / total * 100 if total else 0
            print(f"  个股{cls}: {cls_good[cls]}({pct:.1f}%)")

    # 交叉分析2: 日冲策分 vs 个股
    print(f"\n{'='*50}")
    print(f"方法二: 日冲策分(对应DXZC/DXZA)")
    print(f"{'='*50}")

    if low_count >= 2:
        # 日冲策分低时
        cls_low = Counter()
        for s in stocks:
            cls_low[classify(s[3])] += 1
        print(f"\n当 {low_count}/3 指数日冲策分<50时:")
        for cls in ["好", "中", "坏"]:
            pct = cls_low[cls] / total * 100 if total else 0
            print(f"  个股{cls}: {cls_low[cls]}({pct:.1f}%)")

    if high_count >= 2:
        # 日冲策分高时
        cls_high = Counter()
        for s in stocks:
            cls_high[classify(s[3])] += 1
        print(f"\n当 {high_count}/3 指数日冲策分>=50时:")
        for cls in ["好", "中", "坏"]:
            pct = cls_high[cls] / total * 100 if total else 0
            print(f"  个股{cls}: cls_high[cls]({pct:.1f}%)")

    # 对比: 两种方法在"坏"条件下的个股坏率
    print(f"\n{'='*50}")
    print(f"对比总结")
    print(f"{'='*50}")
    if bad_count >= 2:
        bad_pct = cls_bad["坏"] / total * 100 if total else 0
        print(f"方法一(促动坏): 个股坏率 {bad_pct:.1f}%")
    if low_count >= 2:
        low_pct = cls_low["坏"] / total * 100 if total else 0
        print(f"方法二(日冲低): 个股坏率 {low_pct:.1f}%")

    print(f"\n分析完成")

if __name__ == "__main__":
    main()