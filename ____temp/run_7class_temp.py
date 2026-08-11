"""月基策略7分类统计：周层四域 → 7类 5周续持率"""
import csv, os, sys
from collections import defaultdict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

BASE = r'昭明算展\谕组周_备份_20260804'
files = sorted(os.listdir(BASE))

def classify(wxcd, wxab, zc, zb, 波型, 柱排, hr, 周涨=0, za_down=False):
    """周层四域 → 7分类"""
    # Parse WXCD
    cd_gold = wxcd.startswith('金升') if wxcd else False
    cd_silver = wxcd.startswith('银升') if wxcd else False
    cd_positive = cd_gold  # 金升 = CD>0

    zc_pos = zc > 0
    zb_pos = zb > 0

    # 多长: ZC>0 + CD>0(金升) + ZB>0
    if zc_pos and cd_positive and zb_pos:
        # 多长内部三分类
        is_longzhu = '龙猪' in 波型
        is_shengpai = '升' in 柱排[:2] if 柱排 else False

        # 消极信号: 跌吞(暂缺)/ZA下降/本周涨<0/震正波型
        has_negative = False
        if '震正' in 波型:
            has_negative = True
        if 周涨 < 0:
            has_negative = True
        if za_down:
            has_negative = True
        if hr < 0:
            has_negative = True

        if is_longzhu and is_shengpai:
            return '多长(积极)'
        elif has_negative:
            return '多长(消极)'
        else:
            return '多长(不定)'

    # 多被: ZC>0 但 (CD≤0 或 ZB≤0)
    elif zc_pos and (not cd_positive or not zb_pos):
        if cd_gold:  # 金系ZB≤0
            return '多被(金)'
        else:
            return '多被(银)'

    # 空看: ZC≤0 但 CD>0 或 ZB>0
    elif not zc_pos and (cd_positive or zb_pos):
        return 'NA(空看)'

    # 空长: 三空全
    else:
        return 'NA(空长)'


# Stats storage
cat_stats = defaultdict(lambda: {'total': 0, '续持5周': 0, '总样本': 0})

processed = 0
for fname in files:
    if not fname.startswith('谕组周_') or not fname.endswith('.csv'):
        continue
    code = fname.replace('谕组周_', '').replace('.csv', '')
    fpath = os.path.join(BASE, fname)

    try:
        with open(fpath, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            weeks = list(reader)
    except:
        continue

    # Sort by 主期
    weeks.sort(key=lambda w: str(w.get('主期', '')))

    # For each week, classify and check 5-week continuation
    n = len(weeks)
    for i, w in enumerate(weeks):
        try:
            zc = int(w.get('ZC周', 0) or 0)
            zb = int(w.get('ZB周', 0) or 0)
            za = int(w.get('ZA周', 0) or 0)
            hr = float(w.get('HR', 0) or 0)
            周涨 = float(w.get('周涨', 0) or 0)
        except:
            continue

        wxcd = str(w.get('WXCD', ''))
        wxab = str(w.get('WXAB', ''))
        波型 = str(w.get('波型', ''))
        柱排 = str(w.get('柱排周', ''))

        # ZA下降: compare with previous week
        za_down = False
        if i > 0:
            try:
                prev_za = int(weeks[i-1].get('ZA周', 0) or 0)
                if za < prev_za:
                    za_down = True
            except:
                pass

        cat = classify(wxcd, wxab, zc, zb, 波型, 柱排, hr, 周涨, za_down)
        cat_stats[cat]['总样本'] += 1

        # Check 5 weeks later: is still in 多长?
        if i + 5 < n:
            w5 = weeks[i + 5]
            try:
                zc5 = int(w5.get('ZC周', 0) or 0)
                zb5 = int(w5.get('ZB周', 0) or 0)
            except:
                continue
            wxcd5 = str(w5.get('WXCD', ''))
            cd_pos5 = wxcd5.startswith('金升') if wxcd5 else False

            # 多长5周后: 用简化条件（只需ZC>0 + CD>0 + ZB>0，不再细分）
            is_多长5 = zc5 > 0 and cd_pos5 and zb5 > 0
            cat_stats[cat]['total'] += 1
            if is_多长5:
                cat_stats[cat]['续持5周'] += 1

    processed += 1
    if processed % 1000 == 0:
        print(f'Processed {processed}/{len(files)}')

print(f'\nProcessed {processed} files total')
print()

# Output table
categories = ['多长(积极)', '多长(不定)', '多长(消极)', '多被(金)', '多被(银)', 'NA(空看)', 'NA(空长)']
print(f"{'类别':<12} {'样本':>8} {'5周续持率':>10} {'5周转负率':>10} {'占比':>6}")
print('-' * 50)
total_all = sum(cat_stats[c]['总样本'] for c in categories)
for cat in categories:
    s = cat_stats[cat]
    total = s['total']
    cont = s['续持5周']
    rate = cont / total * 100 if total > 0 else 0
    neg_rate = 100 - rate
    total_count = s['总样本']
    pct = total_count / total_all * 100 if total_all > 0 else 0
    total_str = f'{total_count//10000}万' if total_count >= 10000 else str(total_count)
    print(f"{cat:<12} {total_str:>8} {rate:>9.1f}% {neg_rate:>9.1f}% {pct:>5.1f}%")