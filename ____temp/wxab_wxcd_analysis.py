"""WXAB引领WXCD变化 统计分析"""
import os, csv, glob
from collections import defaultdict, Counter

DIR = r"D:\@VSwork\VS昭明计划VBA优化\____temp\谕组"
files = glob.glob(os.path.join(DIR, "谕组_*.csv"))
print(f"找到 {len(files)} 只股票的谕组数据")

# 定义优先级编码
WXAB_ORDER = {'甲': 4, '乙': 3, '己': 2, '丙': 1, '戊': 0, '丁': 0}
WXCD_ORDER = {'金': 3, '银': 2, '铜': 1, '铁': 0, '屎': 0, '尿': 0, '唏': 0, '嘘': 0}

def wxab_score(s):
    """提取WXAB中最高优先级字符的分数"""
    if not s: return -1
    for c in '甲乙己丙戊':
        if c in s: return WXAB_ORDER.get(c, 0)
    return -1

def wxcd_score(s):
    """提取WXCD中最高优先级字符的分数"""
    if not s: return -1
    for c in '金银铜铁屎尿唏嘘':
        if c in s: return WXCD_ORDER.get(c, 0)
    return -1

def wxab_label(s):
    for c in '甲乙己丙戊':
        if c in s: return c
    return '?'

def wxcd_label(s):
    for c in '金银铜':
        if c in s: return c
    if '铁' in s: return '铁'
    for c in '屎尿唏嘘':
        if c in s: return c
    return '?'

# 数据收集
all_transitions = []  # (WXAB_前, WXCD_前, WXAB_后, WXCD_后, 领先周数)
total_rows = 0

for f in files[:2000]:  # 先跑2000只
    stock = os.path.basename(f).replace('谕组_', '').replace('.csv', '')
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        reader = csv.DictReader(fh)
        rows = []
        for row in reader:
            total_rows += 1
            wxab = row.get('WXAB', '')
            wxcd = row.get('WXCD', '')
            if wxab and wxcd:
                rows.append((wxab, wxcd, wxab_score(wxab), wxcd_score(wxcd)))

    # 扫描WXAB提升 → 后续WXCD提升的匹配
    for i in range(len(rows) - 4):
        wab_now, wcd_now, sab_now, scd_now = rows[i]
        sab_prev = rows[i-1][2] if i > 0 else sab_now

        # WXAB升了？
        if sab_now > sab_prev and sab_now >= 2:  # 升到己以上
            wab_lbl = wxab_label(wab_now)
            wcd_lbl = wxcd_label(wcd_now)
            # 看后续1-4周WXCD是否升
            for lag in range(1, 5):
                if i + lag >= len(rows): break
                _, _, _, scd_future = rows[i + lag]
                if scd_future > scd_now and scd_future >= 2:  # 银以上
                    future_wcd = wxcd_label(rows[i + lag][1])
                    all_transitions.append((wab_lbl, wcd_lbl, future_wcd, lag, stock))
                    break

print(f"\n处理数据: {total_rows} 行")

# 统计: WXAB领先WXCD的分布
if all_transitions:
    print(f"\nWXAB提升后WXCD跟随: {len(all_transitions)} 次")

    # 按领先周数分布
    lag_dist = Counter(t[3] for t in all_transitions)
    print("\n=== 领先周数分布 ===")
    for lag in sorted(lag_dist):
        print(f"  领先{lag}周: {lag_dist[lag]}次 ({lag_dist[lag]/len(all_transitions)*100:.1f}%)")

    # 按WXAB类别统计
    ab_dist = Counter(t[0] for t in all_transitions)
    print("\n=== WXAB触发类别 ===")
    for ab in sorted(ab_dist, key=lambda x: WXAB_ORDER.get(x, 0), reverse=True):
        print(f"  WXAB={ab}: {ab_dist[ab]}次 ({ab_dist[ab]/len(all_transitions)*100:.1f}%)")

    # 按WXCD目标分布
    cd_dist = Counter(t[2] for t in all_transitions)
    print("\n=== WXCD到达目标 ===")
    for cd in sorted(cd_dist, key=lambda x: WXCD_ORDER.get(x, 0), reverse=True):
        print(f"  →{cd}: {cd_dist[cd]}次 ({cd_dist[cd]/len(all_transitions)*100:.1f}%)")

    # 关键: 无WXAB提升时的WXCD变化(基准)
    print("\n=== 基准: WXAB未提升时WXCD自然转好的概率 ===")

else:
    print("无有效转换数据")

# 基线: 无条件WXCD转好的概率
wxcd_improve = 0
wxcd_total = 0
for f in files[:500]:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        reader = csv.DictReader(fh)
        prev_cd = None
        for row in reader:
            wxcd = row.get('WXCD', '')
            if wxcd:
                scd = wxcd_score(wxcd)
                if prev_cd is not None and scd > prev_cd and scd >= 2:
                    wxcd_improve += 1
                wxcd_total += 1
                prev_cd = scd

print(f"\n基准概率: WXCD自然转好 {wxcd_improve}/{wxcd_total} = {wxcd_improve/wxcd_total*100:.1f}%")

print("\n=== 完成 ===")