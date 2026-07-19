# -*- coding: utf-8 -*-
"""
冲高率全量分析 + 最后一柱/失势升排特征验证
基于 7463 只谕组 CSVs
"""
import csv, os, json
from collections import defaultdict
from datetime import datetime

# ─── 配置 ───────────────────────────────────────────────
D = "____temp/谕组"
OUT = "____temp/冲高分析结果.txt"
MIN_WEEKS = 200
MIN_MONTHS = 60

# 列索引（谕组CSV结构）
COL = {
    '主期': 0, '周涨': 1, 'PR': 2, 'HR': 3, 'WXAB': 4,
    '波型': 5, '柱排周': 6, '盈提示': 7, 'WXCD': 8,
    'ZA周': 9, 'ZB周': 10, 'ZC周': 11, '周龄': 12, '周键': 13
}

def parse_float(v):
    try: return float(v)
    except: return 0.0

def parse_int(v):
    try: return int(v)
    except: return 0

def is_上升(zpx):
    """判断是否为升排"""
    return zpx.startswith('升') or zpx.startswith('(升)')

def is_下跌(zpx):
    """判断是否为跌排"""
    return zpx.startswith('跌') or zpx.startswith('(跌)')

def is_人排(zpx):
    """判断是否为人排"""
    return zpx.startswith('(人)')

# ─── 主分析 ──────────────────────────────────────────────
def analyze():
    files = [f for f in os.listdir(D) if f.endswith('.csv')]
    print(f"总文件数: {len(files)}")

    # 结果容器
    weekly_all = []
    weekly_za_pos = []
    weekly_zc_pos = []
    weekly_za1_5 = []
    weekly_za_pos_zc_pos = []
    weekly_za1_5_no_preg = []
    weekly_jin_rise = []
    monthly_all = []

    # 最后一柱 & 失势升排
    last_pillar_stats = defaultdict(lambda: {'total': 0, 'fail_5w': 0, 'fail_3w': 0, 'fail_1w': 0})
    weak_rise_stats = defaultdict(lambda: {'total': 0, 'fail_5w': 0, 'fail_3w': 0, 'fail_1w': 0})

    count = 0
    for fname in sorted(files):
        code = fname.replace('谕组_', '').replace('.csv', '')
        path = os.path.join(D, fname)

        try:
            with open(path, 'r', encoding='gbk') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
        except:
            continue

        weeks = len(rows)
        if weeks < MIN_WEEKS:
            continue

        # 提取数值列
        hr_vals = [parse_float(r[COL['HR']]) for r in rows]
        pr_vals = [parse_float(r[COL['PR']]) for r in rows]
        za_vals = [r[COL['ZA周']] for r in rows]
        zc_vals = [r[COL['ZC周']] for r in rows]
        zpx_vals = [r[COL['柱排周']] for r in rows]
        bx_vals = [r[COL['波型']] for r in rows]
        wxab_vals = [r[COL['WXAB']] for r in rows]
        wxcd_vals = [r[COL['WXCD']] for r in rows]
        yts_vals = [r[COL['盈提示']] for r in rows]
        dates = [r[COL['主期']] for r in rows]

        # ── 1. 周冲高率 ──
        n_hr = sum(1 for h in hr_vals if h > 0)
        rate = n_hr / weeks * 100
        weekly_all.append((code, weeks, n_hr, rate))

        # 1b. ZA>0
        za_pos = [(hr_vals[i], za_vals[i]) for i in range(weeks) if parse_int(za_vals[i]) > 0]
        if za_pos:
            n = sum(1 for h, _ in za_pos if h > 0)
            weekly_za_pos.append((code, len(za_pos), n, n/len(za_pos)*100))

        # 1c. ZC>0
        zc_pos = [(hr_vals[i], zc_vals[i]) for i in range(weeks) if parse_int(zc_vals[i]) > 0]
        if zc_pos:
            n = sum(1 for h, _ in zc_pos if h > 0)
            weekly_zc_pos.append((code, len(zc_pos), n, n/len(zc_pos)*100))

        # 1d. ZA 1~5
        za1_5 = [(hr_vals[i], za_vals[i]) for i in range(weeks) if 1 <= parse_int(za_vals[i]) <= 5]
        if za1_5:
            n = sum(1 for h, _ in za1_5 if h > 0)
            weekly_za1_5.append((code, len(za1_5), n, n/len(za1_5)*100))

        # 1e. ZA>0 AND ZC>0
        za_zc_pos = [(hr_vals[i], za_vals[i], zc_vals[i]) for i in range(weeks)
                     if parse_int(za_vals[i]) > 0 and parse_int(zc_vals[i]) > 0]
        if za_zc_pos:
            n = sum(1 for h, _, _ in za_zc_pos if h > 0)
            weekly_za_pos_zc_pos.append((code, len(za_zc_pos), n, n/len(za_zc_pos)*100))

        # 1f. ZA1~5 + 非孕
        za1_5_no_preg = [(hr_vals[i], zpx_vals[i]) for i in range(weeks)
                         if 1 <= parse_int(za_vals[i]) <= 5 and '孕' not in zpx_vals[i]]
        if za1_5_no_preg:
            n = sum(1 for h, _ in za1_5_no_preg if h > 0)
            weekly_za1_5_no_preg.append((code, len(za1_5_no_preg), n, n/len(za1_5_no_preg)*100))

        # 1g. 金+升排 (WXCD含金, 柱排升)
        jin_rise = [(hr_vals[i], wxcd_vals[i], zpx_vals[i]) for i in range(weeks)
                    if '金' in wxcd_vals[i] and is_上升(zpx_vals[i])]
        if jin_rise:
            n = sum(1 for h, _, _ in jin_rise if h > 0)
            weekly_jin_rise.append((code, len(jin_rise), n, n/len(jin_rise)*100))

        # ── 2. 月冲高率 ──
        month_hr = defaultdict(list)
        for i in range(weeks):
            try:
                dt = datetime.strptime(dates[i], '%Y/%m/%d')
                mk = (dt.year, dt.month)
                month_hr[mk].append(hr_vals[i])
            except:
                pass

        if len(month_hr) >= MIN_MONTHS:
            n_month_hr = sum(1 for hrs in month_hr.values() if any(h > 0 for h in hrs))
            total_months = len(month_hr)
            monthly_all.append((code, total_months, n_month_hr, n_month_hr/total_months*100))

        # ── 3. 最后一柱特征 ──
        for i in range(weeks - 5):
            zpx = zpx_vals[i]
            hr = hr_vals[i]
            pr = pr_vals[i]

            # 特征1: 连阳3+ → 转阴
            if i >= 3:
                prev3_pr = [pr_vals[i-j] for j in range(1, 4)]
                if all(p >= 0 for p in prev3_pr) and pr < 0:
                    key = '1_连阳3+转阴'
                    last_pillar_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        last_pillar_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        last_pillar_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        last_pillar_stats[key]['fail_1w'] += 1

            # 特征2: 连阳3+ → 巨阳>10%
            if i >= 3:
                prev3_pr = [pr_vals[i-j] for j in range(1, 4)]
                if all(p >= 0 for p in prev3_pr):
                    if pr >= 10:
                        key = '2_连阳3+巨阳>10%'
                        last_pillar_stats[key]['total'] += 1
                        future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                        if any(z < 0 for z in future_zc):
                            last_pillar_stats[key]['fail_5w'] += 1
                        if any(z < 0 for z in future_zc[:3]):
                            last_pillar_stats[key]['fail_3w'] += 1
                        if future_zc and future_zc[0] < 0:
                            last_pillar_stats[key]['fail_1w'] += 1
                    if pr >= 20:
                        key2 = '3_连阳3+巨阳>20%'
                        last_pillar_stats[key2]['total'] += 1
                        future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                        if any(z < 0 for z in future_zc):
                            last_pillar_stats[key2]['fail_5w'] += 1
                        if any(z < 0 for z in future_zc[:3]):
                            last_pillar_stats[key2]['fail_3w'] += 1
                        if future_zc and future_zc[0] < 0:
                            last_pillar_stats[key2]['fail_1w'] += 1

            # 特征3: 跌吞（阴吞前阳）
            if i >= 1:
                prev_pr = pr_vals[i-1]
                if prev_pr > 0 and pr < 0 and abs(pr) > prev_pr:
                    key = '4_跌吞'
                    last_pillar_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        last_pillar_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        last_pillar_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        last_pillar_stats[key]['fail_1w'] += 1

            # 特征4: 连阳逐步缩小
            if i >= 3:
                prev_pr_abs = [abs(pr_vals[i-j]) for j in range(1, 4)]
                prev_pr_raw = [pr_vals[i-j] for j in range(1, 4)]
                if all(p >= 0 for p in prev_pr_raw) and prev_pr_abs[0] > prev_pr_abs[1] > prev_pr_abs[2]:
                    key = '5_连阳逐步缩小'
                    last_pillar_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        last_pillar_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        last_pillar_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        last_pillar_stats[key]['fail_1w'] += 1

            # 特征5: 上影线小柱（PR很小但HR很大）
            if i >= 1:
                prev_pr = pr_vals[i-1]
                if prev_pr > 0 and hr > 0 and hr > pr * 2 and pr < 2:
                    key = '6_上影线小柱'
                    last_pillar_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        last_pillar_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        last_pillar_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        last_pillar_stats[key]['fail_1w'] += 1

            # 特征6: 连阳3+ → 十字星（PR很小接近0，阴阳不定）
            if i >= 3:
                prev3_pr = [pr_vals[i-j] for j in range(1, 4)]
                if all(p >= 0 for p in prev3_pr) and abs(pr) < 0.5:
                    key = '7_连阳3+十字星'
                    last_pillar_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        last_pillar_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        last_pillar_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        last_pillar_stats[key]['fail_1w'] += 1

        # ── 4. 失势升排 ──
        for i in range(weeks - 5):
            zpx = zpx_vals[i]
            if not is_上升(zpx):
                continue

            hr = hr_vals[i]
            pr = pr_vals[i]

            # A: 升排+长上影 (HR >> PR)
            if hr > 0 and pr > 0 and hr > pr * 3 and pr < 5:
                key = 'A_升排+长上影'
                weak_rise_stats[key]['total'] += 1
                future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                if any(z < 0 for z in future_zc):
                    weak_rise_stats[key]['fail_5w'] += 1
                if any(z < 0 for z in future_zc[:3]):
                    weak_rise_stats[key]['fail_3w'] += 1
                if future_zc and future_zc[0] < 0:
                    weak_rise_stats[key]['fail_1w'] += 1

            # B: 升排+长下影
            if hr > 0 and abs(pr) < 1 and hr > 5:
                key = 'B_升排+长下影'
                weak_rise_stats[key]['total'] += 1
                future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                if any(z < 0 for z in future_zc):
                    weak_rise_stats[key]['fail_5w'] += 1
                if any(z < 0 for z in future_zc[:3]):
                    weak_rise_stats[key]['fail_3w'] += 1
                if future_zc and future_zc[0] < 0:
                    weak_rise_stats[key]['fail_1w'] += 1

            # C: 升排+柱体缩小
            if i >= 2:
                prev_pr = abs(pr_vals[i-1])
                prev2_pr = abs(pr_vals[i-2])
                if prev2_pr > 0 and prev_pr > 0 and prev2_pr > prev_pr > abs(pr):
                    key = 'C_升排+柱体缩小'
                    weak_rise_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        weak_rise_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        weak_rise_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        weak_rise_stats[key]['fail_1w'] += 1

            # D: 升排+大阳后大阴
            if i >= 1:
                prev_pr = pr_vals[i-1]
                if prev_pr > 8 and pr < -3:
                    key = 'D_升排+大阳后大阴'
                    weak_rise_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        weak_rise_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        weak_rise_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        weak_rise_stats[key]['fail_1w'] += 1

            # E: 升排+阴阳交替(震荡)
            if i >= 4:
                prev5_pr = [pr_vals[i-j] for j in range(1, 5)]
                signs = [1 if p >= 0 else -1 for p in prev5_pr]
                alt_count = sum(1 for j in range(len(signs)-1) if signs[j] != signs[j+1])
                if alt_count >= 2 and all(abs(p) < 5 for p in prev5_pr):
                    key = 'E_升排+震荡'
                    weak_rise_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        weak_rise_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        weak_rise_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        weak_rise_stats[key]['fail_1w'] += 1

            # F: 升排+ZA下降
            if i >= 1:
                cur_za = parse_int(za_vals[i])
                prev_za = parse_int(za_vals[i-1])
                if prev_za > 0 and cur_za < prev_za:
                    key = 'F_升排+ZA下降'
                    weak_rise_stats[key]['total'] += 1
                    future_zc = [parse_int(zc_vals[i+j]) for j in range(1, 6)]
                    if any(z < 0 for z in future_zc):
                        weak_rise_stats[key]['fail_5w'] += 1
                    if any(z < 0 for z in future_zc[:3]):
                        weak_rise_stats[key]['fail_3w'] += 1
                    if future_zc and future_zc[0] < 0:
                        weak_rise_stats[key]['fail_1w'] += 1

        count += 1
        if count % 1000 == 0:
            print(f"  已处理 {count}/{len(files)} 个文件...")

    print(f"\n共处理 {count} 个文件（≥{MIN_WEEKS}周）")

    # ─── 输出结果 ────────────────────────────────────
    lines = []
    lines.append("=" * 80)
    lines.append("冲高率全量分析报告")
    lines.append(f"数据：{count} 只股票（≥{MIN_WEEKS}周）")
    lines.append("=" * 80)

    # 一、周冲高率
    lines.append("\n\n" + "=" * 80)
    lines.append("一、周冲高率排名")
    lines.append("=" * 80)

    analyses = [
        ("全部条件", weekly_all),
        ("ZA>0", weekly_za_pos),
        ("ZC>0", weekly_zc_pos),
        ("ZA 1~5周", weekly_za1_5),
        ("ZA>0 AND ZC>0", weekly_za_pos_zc_pos),
        ("ZA1~5+非孕", weekly_za1_5_no_preg),
        ("金+升排", weekly_jin_rise),
    ]

    for label, data in analyses:
        lines.append(f"\n--- {label} ---")
        lines.append(f"{'代码':<12} {'样本周':>8} {'冲高次':>8} {'冲高率':>8}")
        lines.append("-" * 40)
        data.sort(key=lambda x: x[3], reverse=True)
        top = data[:15]
        for code, w, n, r in top:
            lines.append(f"{code:<12} {w:>8} {n:>8} {r:>7.2f}%")
        lines.append(f"  ... 共 {len(data)} 只，最高={top[0][3]:.2f}%，最低={data[-1][3]:.2f}%")
        if top[0][3] >= 99.99:
            lines.append(f"  🏆 存在100%冲高票！")

    # 二、月冲高率
    lines.append("\n\n" + "=" * 80)
    lines.append("二、月冲高率排名")
    lines.append("=" * 80)
    lines.append(f"（每月最后一周HR>0=月冲高，最低月数：{MIN_MONTHS}）")
    monthly_all.sort(key=lambda x: x[3], reverse=True)
    top_m = monthly_all[:20]
    lines.append(f"\n{'代码':<12} {'总月数':>8} {'冲高月':>8} {'月冲高率':>8}")
    lines.append("-" * 40)
    for code, m, n, r in top_m:
        lines.append(f"{code:<12} {m:>8} {n:>8} {r:>7.2f}%")
    lines.append(f"  ... 共 {len(monthly_all)} 只，最高={top_m[0][3]:.2f}%")
    if top_m[0][3] >= 99.99:
        lines.append(f"  🏆 存在100%月冲高票！")

    # 月冲高率最低
    monthly_rev = sorted(monthly_all, key=lambda x: x[3])
    lines.append(f"\n月冲高率最低:")
    for code, m, n, r in monthly_rev[:10]:
        lines.append(f"{code:<12} {m:>8} {n:>8} {r:>7.2f}%")

    # 三、最后一柱特征
    lines.append("\n\n" + "=" * 80)
    lines.append("三、最后一柱特征验证")
    lines.append("=" * 80)
    lines.append(f"\n{'特征':<20} {'样本':>8} {'5周ZC<0':>10} {'3周ZC<0':>10} {'1周ZC<0':>10}")
    lines.append("-" * 60)
    for key in sorted(last_pillar_stats.keys()):
        st = last_pillar_stats[key]
        lines.append(f"{key:<20} {st['total']:>8} "
                     f"{st['fail_5w']/st['total']*100:>9.1f}% "
                     f"{st['fail_3w']/st['total']*100:>9.1f}% "
                     f"{st['fail_1w']/st['total']*100:>9.1f}%")

    # 四、失势升排特征
    lines.append("\n\n" + "=" * 80)
    lines.append("四、失势升排特征验证")
    lines.append("=" * 80)
    lines.append(f"\n{'特征':<22} {'样本':>8} {'5周ZC<0':>10} {'3周ZC<0':>10} {'1周ZC<0':>10}")
    lines.append("-" * 60)
    for key in sorted(weak_rise_stats.keys()):
        st = weak_rise_stats[key]
        lines.append(f"{key:<22} {st['total']:>8} "
                     f"{st['fail_5w']/st['total']*100:>9.1f}% "
                     f"{st['fail_3w']/st['total']*100:>9.1f}% "
                     f"{st['fail_1w']/st['total']*100:>9.1f}%")

    # 五、条件组合统计
    lines.append("\n\n" + "=" * 80)
    lines.append("五、条件组合统计")
    lines.append("=" * 80)
    lines.append(f"\n{'条件':<20} {'样本数':>8} {'最高冲高率':>12} {'平均冲高率':>12}")
    lines.append("-" * 52)
    for name, data in analyses:
        if not data: continue
        rates = [x[3] for x in data]
        lines.append(f"{name:<20} {len(data):>8} {max(rates):>11.2f}% {sum(rates)/len(rates):>11.2f}%")

    # 写入文件
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n✅ 结果写入: {OUT}")
    print(f"   共 {count} 只股票")

    return {
        'weekly_all_top': [(x[0], round(x[3],2)) for x in weekly_all[:5]],
        'weekly_za_pos_top': [(x[0], round(x[3],2)) for x in weekly_za_pos[:5]],
        'weekly_zc_pos_top': [(x[0], round(x[3],2)) for x in weekly_zc_pos[:5]],
        'weekly_za1_5_top': [(x[0], round(x[3],2)) for x in weekly_za1_5[:5]],
        'weekly_za_zc_top': [(x[0], round(x[3],2)) for x in weekly_za_pos_zc_pos[:5]],
        'weekly_za1_5_no_preg_top': [(x[0], round(x[3],2)) for x in weekly_za1_5_no_preg[:5]],
        'weekly_jin_rise_top': [(x[0], round(x[3],2)) for x in weekly_jin_rise[:5]],
        'monthly_top': [(x[0], round(x[3],2)) for x in monthly_all[:5]],
        'monthly_bottom': [(x[0], round(x[3],2)) for x in monthly_rev[:5]],
        'last_pillar': {k: {'samples': v['total'], 'fail_5w_pct': round(v['fail_5w']/v['total']*100,1) if v['total']>0 else 0} for k,v in sorted(last_pillar_stats.items())},
        'weak_rise': {k: {'samples': v['total'], 'fail_5w_pct': round(v['fail_5w']/v['total']*100,1) if v['total']>0 else 0} for k,v in sorted(weak_rise_stats.items())},
    }

if __name__ == '__main__':
    result = analyze()
    with open('____temp/冲高分析结论.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n\n=== 主要结论 ===")
    print(f"周冲高(全部)最高: {result['weekly_all_top']}")
    print(f"周冲高(ZA>0): {result['weekly_za_pos_top']}")
    print(f"周冲高(ZC>0): {result['weekly_zc_pos_top']}")
    print(f"周冲高(ZA1~5): {result['weekly_za1_5_top']}")
    print(f"周冲高(ZA>0&ZC>0): {result['weekly_za_zc_top']}")
    print(f"周冲高(ZA1~5+非孕): {result['weekly_za1_5_no_preg_top']}")
    print(f"周冲高(金+升排): {result['weekly_jin_rise_top']}")
    print(f"月冲高: {result['monthly_top']}")
    print(f"月冲高最低: {result['monthly_bottom']}")
    print(f"最后一柱: {json.dumps(result['last_pillar'], ensure_ascii=False, indent=2)}")
    print(f"失势升排: {json.dumps(result['weak_rise'], ensure_ascii=False, indent=2)}")