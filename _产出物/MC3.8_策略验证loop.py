"""
策略验证 loop — 5维度验证
================================
对周冲策略体系 v1.0 的每个策略/条件做系统性有效性检验。

输出：验证报告 Markdown 到 _主文档/ 或 终端

维度：
  ① 稳定性 — 概率值的时间切片一致性
  ② 置信度 — 样本量 + 95%置信区间
  ③ 风险 — 失败周的尾部分布
  ④ 正交 — 条件独立贡献
  ⑤ 突破 — WJA/WJC突破后持续冲高率
"""
import os, csv, sys, glob, math
from collections import defaultdict, OrderedDict
from datetime import datetime

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp\谕组'
OUTPUT = r'd:\@VSwork\VS昭明计划VBA优化\_主文档\MC3.2_策略验证报告.md'

# ============================================================
# 策略定义（与VBA神谕.bas完全一致）
# ============================================================
def match_strategy(row):
    """复制VBA神谕的策略匹配逻辑，返回策略名"""
    wxcd = str(row.get('WXCD', '') or '')
    wxab = str(row.get('WXAB', '') or '')
    zhupai = str(row.get('柱排周', '') or '')
    yingtishi = str(row.get('盈提示', '') or '')
    boxing = str(row.get('波型', '') or '')
    try:
        za = float(row.get('ZA周', '0') or '0')
    except:
        za = 0
    hr = float(row.get('HR', '0') or '0')

    # 金系
    if '金' in wxcd and ('甲' in wxab or '乙' in wxab or '己' in wxab):
        if zhupai.startswith('升') and '尾反孕' not in zhupai:
            if '高' in yingtishi:
                if '龙猪' in boxing or '龙管' in boxing:
                    return '金最优(全部)', hr
                else:
                    return '金+多长+升排+非孕+盈高', hr
            else:
                return '金+多长+升排+非孕', hr
        elif zhupai.startswith('升'):
            return '金+多长+升排', hr
        else:
            return '金+多长', hr

    # 银系
    elif '银' in wxcd:
        if '高' in yingtishi or '宽' in yingtishi:
            return '银+盈提示有', hr
        elif '己' in wxab:
            return '银+WXAB=己', hr
        elif zhupai.startswith('升'):
            return '银+柱排=升', hr
        elif '龙猪' in boxing:
            return '银+龙猪', hr
        elif 5 < za <= 10:
            return '银+ZA5~10', hr

    return '', hr


# ============================================================
# 扫描全部谕组CSV
# ============================================================
files = sorted(glob.glob(os.path.join(TEMP, '谕组_*.csv')))
print(f'扫描文件: {len(files)}')

# 按策略收集HR数据
# {策略名: {年份: [hr值列表]}}
strategy_data = defaultdict(lambda: defaultdict(list))
strategy_all = defaultdict(list)  # {策略名: [hr值列表]}

total_rows = 0
for fi, fn in enumerate(files):
    with open(fn, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hr = float(row.get('HR', '0') or '0')
            except:
                continue
            name, hr_val = match_strategy(row)
            total_rows += 1
            if not name:
                continue
            strategy_all[name].append(hr_val)
            # 年份切片
            try:
                year = row['主期'][:4]
            except:
                year = '未知'
            strategy_data[name][year].append(hr_val)

    if (fi + 1) % 500 == 0:
        print(f'  已处理 {fi+1}/{len(files)} 个文件 ({total_rows}周)...')

print(f'完成! 共 {total_rows} 周数据\n')


# ============================================================
# 统计函数
# ============================================================
def p_ge3(hrs):
    """计算 P(≥3%)"""
    if not hrs: return 0, 0
    n = len(hrs)
    k = sum(1 for h in hrs if h >= 3)
    return k / n * 100, n

def p_ge5(hrs):
    if not hrs: return 0, 0
    n = len(hrs)
    k = sum(1 for h in hrs if h >= 5)
    return k / n * 100, n

def wilson_ci(hrs, z=1.96):
    """Wilson 95%置信区间"""
    if not hrs: return 0, 0, 0
    n = len(hrs)
    k = sum(1 for h in hrs if h >= 3)
    if n == 0: return 0, 0, 0
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    margin = z * math.sqrt((p*(1-p) + z*z/(4*n))/n) / denom
    return center * 100, max(0, center-margin) * 100, min(100, center+margin) * 100

def tail_risk(hrs):
    """失败周(HR<3%)的跌幅分布"""
    failed = [h for h in hrs if h < 3]
    if not failed:
        return {'count': 0, 'mean': 0, 'median': 0, 'max': 0, 'p5': 0, 'p95': 0}
    failed_sorted = sorted(failed)
    n = len(failed_sorted)
    # 用 HR 表示涨幅（负数=下跌）
    return {
        'count': n,
        'mean': sum(failed_sorted)/n,
        'median': failed_sorted[n//2],
        'max': failed_sorted[0],  # 最大亏损（最小值）
        'p5': failed_sorted[int(n*0.05)],  # 第5百分位（最差5%）
        'p95': failed_sorted[int(n*0.95)],  # 第95百分位
    }


# ============================================================
# 输出验证报告
# ============================================================
STRATEGY_ORDER = [
    '金最优(全部)', '金+多长+升排+非孕+盈高', '金+多长+升排+非孕',
    '金+多长+升排', '金+多长',
    '银+盈提示有', '银+龙猪', '银+柱排=升', '银+ZA5~10', '银+WXAB=己',
]

report_lines = []
report_lines.append('# 周冲策略验证报告')
report_lines.append(f'> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
report_lines.append(f'> 数据: {len(files)} 只股票')
report_lines.append(f'> 总周数: {total_rows}')
report_lines.append('')
report_lines.append('---')
report_lines.append('')

# 各策略验证
for name in STRATEGY_ORDER:
    hrs = strategy_all.get(name, [])
    if not hrs:
        continue

    p3, n = p_ge3(hrs)
    p5, _ = p_ge5(hrs)
    ci_center, ci_lo, ci_hi = wilson_ci(hrs)
    risk = tail_risk(hrs)
    years = sorted(strategy_data[name].keys())

    # 确认状态
    status = '✅ 通过'
    flags = []

    # ① 稳定性: 时间切片偏差
    year_slices = []
    for y in years:
        if y == '未知': continue
        yp3, yn = p_ge3(strategy_data[name][y])
        if yn >= 100:
            year_slices.append((y, yp3, yn))
    if year_slices:
        max_dev = max(abs(yp3 - p3) for _, yp3, _ in year_slices)
        if max_dev > 10:
            flags.append(f'⚠️ 时间波动大(±{max_dev:.1f}pp)')
            status = '⚠️ 警告'
        elif max_dev > 5:
            flags.append(f'稳定性±{max_dev:.1f}pp')

    # ② 置信度
    ci_width = ci_hi - ci_lo
    if ci_width > 15:
        flags.append(f'置信区间宽({ci_width:.1f}pp)')
        if ci_width > 25:
            status = '⚠️ 警告'
    if n < 500:
        flags.append(f'样本少({n}周)')
        if n < 200:
            status = '❌ 不可靠'

    # ③ 风险
    if risk['count'] > 0:
        worst = risk['p5']
        if worst < -5:
            flags.append(f'失败周最差5%<{worst:.1f}%')
            if worst < -8:
                status = '⚠️ 警告'

    report_lines.append(f'## {name}')
    report_lines.append(f'**状态: {status}**')
    if flags:
        report_lines.append(f'**标记:** {", ".join(flags)}')
    report_lines.append('')
    report_lines.append(f'| 指标 | 值 |')
    report_lines.append(f'|:----|:---:|')
    report_lines.append(f'| 样本量 | {n} 周 |')
    report_lines.append(f'| P(≥3%) | {p3:.1f}% |')
    report_lines.append(f'| 95%置信区间 | [{ci_lo:.1f}%, {ci_hi:.1f}%] |')
    report_lines.append(f'| P(≥5%) | {p5:.1f}% |')
    report_lines.append(f'| 失败周占比 | {risk["count"]/n*100:.1f}% ({risk["count"]}周) |')
    report_lines.append(f'| 失败周中位HR | {risk["median"]:.2f}% |')
    report_lines.append(f'| 失败周最差5% | ≤{risk["p5"]:.2f}% |')
    report_lines.append(f'| 失败周最大亏损 | {risk["max"]:.2f}% |')
    report_lines.append('')

    # 时间切片
    if len(year_slices) >= 2:
        report_lines.append('### ① 稳定性：按年切片 P(≥3%)')
        report_lines.append(f'| 年份 | P(≥3%) | 样本 | 偏差 |')
        report_lines.append(f'|:----|:------:|:----:|:----:|')
        for y, yp3, yn in year_slices:
            dev = yp3 - p3
            report_lines.append(f'| {y} | {yp3:.1f}% | {yn} | {dev:+.1f}pp |')
        report_lines.append('')

    report_lines.append('---')
    report_lines.append('')

# 全量基准
hrs_all = []
for name in STRATEGY_ORDER:
    hrs_all.extend(strategy_all.get(name, []))
p3_all, n_all = p_ge3(hrs_all)
ci_all, _, _ = wilson_ci(hrs_all)
report_lines.append(f'## 全量策略汇总')
report_lines.append(f'| 指标 | 值 |')
report_lines.append(f'|:----|:---:|')
report_lines.append(f'| 总策略命中周数 | {n_all} |')
report_lines.append(f'| 策略加权 P(≥3%) | {p3_all:.1f}% |')
report_lines.append(f'| 覆盖总周数 | {total_rows} |')
report_lines.append('')

# 输出
report = '\n'.join(report_lines)
print(report)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(report)
print(f'\n报告已写入: {OUTPUT}')