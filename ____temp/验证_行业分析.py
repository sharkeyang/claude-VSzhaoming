#!/usr/bin/env python3
"""行业分析：大盘vs行业vs个股的三层关系"""
import csv
from collections import Counter, defaultdict

CSV_PATH = r"D:\@VSwork\VS昭明计划VBA优化\____temp\大盘个股联动.csv"

def classify(cang_first):
    """仓周类首字: 金/银=好, 屎/尿=坏, 其他=中"""
    if cang_first in ("金", "银"):
        return "好"
    elif cang_first in ("屎", "尿"):
        return "坏"
    return "中"

def main():
    with open(CSV_PATH, 'r', encoding='gbk') as f:
        reader = csv.reader(f)
        header = next(reader)
        # 确认列数
        col_count = len(header)
        print(f"列数: {col_count} ({header})")

        data = []
        for row in reader:
            if not row or not row[0]:
                continue
            cang_zhou = row[3] if len(row) > 3 else ""
            dai_zhou = row[4] if len(row) > 4 else ""
            industry = row[7] if len(row) > 7 else ""
            is_wide = row[8] if len(row) > 8 else ""
            cang_first = cang_zhou[0] if cang_zhou else ""
            promote = dai_zhou[3] if len(dai_zhou) >= 4 else ""
            data.append((row[0], row[1] if len(row) > 1 else "",
                        classify(cang_first), industry, promote, is_wide))

    indexes = [d for d in data if d[5] == "是"]
    stocks = [d for d in data if d[5] != "是" and d[3] != ""]
    stocks_all = [d for d in data if d[5] != "是"]

    print(f"\n全量个股: {len(stocks_all)} 只")
    print(f"有行业分类: {len(stocks)} 只")

    # 1. 行业整体分布
    print(f"\n{'='*60}")
    print("行业整体分布（按好票率排序）")
    print(f"{'='*60}")
    ind_stats = {}
    for s in stocks:
        ind = s[3]
        if ind not in ind_stats:
            ind_stats[ind] = {"好": 0, "中": 0, "坏": 0, "总": 0}
        ind_stats[ind][s[2]] += 1
        ind_stats[ind]["总"] += 1

    # 按好票率排序
    ind_sorted = sorted(ind_stats.items(), key=lambda x: x[1]["好"]/x[1]["总"] if x[1]["总"] > 0 else 0, reverse=True)
    print(f"{'行业':<12} {'好票率':>8} {'好':>6} {'中':>6} {'坏':>6} {'总':>6}")
    print(f"{'-'*12} {'-'*8} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
    for ind, st in ind_sorted:
        if st["总"] < 10:  # 过滤样本太少
            continue
        good_rate = st["好"] / st["总"] * 100
        print(f"{ind:<12} {good_rate:>7.1f}% {st['好']:>6} {st['中']:>6} {st['坏']:>6} {st['总']:>6}")

    # 2. 防御性行业 vs 进攻性行业
    print(f"\n{'='*60}")
    print("防御性行业（大盘坏时仍好） vs 进攻性行业（好票率最高）")
    print(f"{'='*60}")
    print(f"\n防御性行业 TOP10（大盘全坏时好票率最高）:")
    top_good = sorted(ind_stats.items(), key=lambda x: x[1]["好"]/x[1]["总"] if x[1]["总"] > 10 else 0, reverse=True)[:10]
    print(f"{'行业':<12} {'好票率':>8}")
    for ind, st in top_good:
        print(f"  {ind:<12} {st['好']/st['总']*100:>7.1f}% ({st['好']}/{st['总']})")

    print(f"\n进攻性行业 TOP10（好票率最高，不限大盘条件）:")
    # 实际上今天大盘全坏，所以"进攻性"只能看相对好票率
    for ind, st in top_good:
        print(f"  {ind:<12} {st['好']/st['总']*100:>7.1f}%")

    # 3. 行业指数映射验证
    print(f"\n{'='*60}")
    print("行业指数映射验证（行业 vs 映射指数）")
    print(f"{'='*60}")
    # 检查映射表中的指数是否在数据中
    idx_cidls = [d[0] for d in indexes]
    idx_names = {d[0]: d[1] for d in indexes}
    print(f"\n数据中的指数: {len(indexes)} 个")
    for idx in indexes:
        print(f"  {idx[0]} {idx[1]} 仓周类={idx[2][0] if idx[2] else ''}")

    # 4. 行业 vs 行业指数对比
    print(f"\n{'='*60}")
    print("行业仓周类 vs 对应指数仓周类对比")
    print(f"{'='*60}")
    # 行业指数映射（从跨码管理模块的映射表）
    # 这里只验证数据中存在的行业指数
    ind_index_map = {  # 益盟行业 → 指数CIDL
        "银行": "sz399986", "证券期货": "sz399975", "保险": "sz399809",
        "有色金属": "sz399395", "钢铁": "sz399440", "煤炭开采": "sz399998",
        "石油石化": "sz399439", "航天国防": "sz399967", "房地产": "sz399393",
        "酿酒": "sz399997", "食品加工": "sz399396",
        "医药制造": "sz399933", "医疗服务": "sz399989", "医疗器械": "sz399989",
        "工程建筑": "sz399995", "建材": "sz399359", "水泥": "sz399359",
        "软件开发": "sz399935", "软件服务": "sz399935",
        "通信设备": "sz399389", "通信服务": "sz399389",
        "文化传媒": "sz399397", "影视动漫": "sz399971",
        "电力": "sz399438", "环境保护": "sh000827",
        "公用事业": "sz399438",
        "汽车制造": "sz399417", "汽车零部件": "sz399417",
        "光伏设备": "sz399808", "电源设备": "sz399808",
        "仓储物流": "sz399353",
    }

    print(f"{'行业':<12} {'好票率':>8} {'对应指数':<14} {'指数仓周':>10}")
    for ind, idx_cidl in list(ind_index_map.items())[:20]:  # 前20个
        if ind in ind_stats:
            st = ind_stats[ind]
            good_rate = st["好"] / st["总"] * 100 if st["总"] > 0 else 0
            idx_cang = ""
            for idx in indexes:
                if idx[0] == idx_cidl:
                    idx_cang = idx[2][0] if idx[2] else ""
                    break
            print(f"{ind:<12} {good_rate:>7.1f}% {idx_cidl:<14} {idx_cang:>10}")

    print(f"\n{'='*60}")
    print("分析完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()