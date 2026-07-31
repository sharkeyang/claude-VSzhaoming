import pandas as pd, os, glob
from collections import defaultdict

csv_dir = "d:/@VSwork/VS昭明计划VBA优化/昭明算展/谕组周"
all_files = glob.glob(os.path.join(csv_dir, "*.csv"))
print(f"Total files: {len(all_files)}")

def get_board(code):
    code = os.path.basename(code).replace('谕组周_', '').replace('.csv', '')
    try:
        num = int(code[2:]) if code[2:].isdigit() else 0
    except: num = 0
    if num >= 600000 and num <= 609999: return 'Qif'
    elif num >= 600000 and num <= 699999: return 'Qic'
    elif num >= 1 and num <= 399999: return 'Qimit'
    else: return 'Qin'

def match_strategy(row):
    wxcd = str(row.get('WXCD',''))
    wxab = str(row.get('WXAB',''))
    zhu = str(row.get('柱排周',''))
    bo = str(row.get('波型',''))
    ying = str(row.get('盈提示',''))
    za = row.get('ZA周', 0)
    hr = row.get('下周HR', float('nan'))
    if pd.isna(hr): return None

    is_gold = '金' in wxcd
    is_silver = '银' in wxcd
    wxab_good = sum(1 for x in ['甲','乙','己'] if x in wxab) > 0
    is_sheng = zhu and len(zhu) > 0 and zhu[0] == '升'
    not_pregnant = '尾反孕' not in zhu
    ying_str = str(ying) if ying != 'nan' else ''
    ying_gao = '高' in ying_str
    ying_gao_kuan = '高' in ying_str or '宽' in ying_str
    is_lz_lg = ('龙猪' in bo) or ('龙管' in bo)
    is_lz = '龙猪' in bo

    if is_gold and wxab_good:
        if is_sheng and not_pregnant:
            if ying_gao:
                return '金最优(全部)' if is_lz_lg else '金+盈高'
            else: return '金+升排+非孕'
        elif is_sheng: return '金+升排'
        else: return '金+多长'
    elif is_silver:
        if ying_gao_kuan: return '银+盈提示有'
        elif '己' in wxab: return '银+WXAB=己'
        elif is_sheng: return '银+柱排=升'
        elif is_lz: return '银+龙猪'
        elif za > 5 and za <= 10: return '银+ZA5~10'
    return None

# Collect data
strat_data = defaultdict(lambda: defaultdict(list))
silver_data = defaultdict(list)
board_all = defaultdict(list)
all_hr = []

for i, f in enumerate(all_files):
    if i % 1000 == 0: print(f"  {i}/{len(all_files)}...")
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 20: continue
        board = get_board(f)
        df['下周HR'] = df['HR'].shift(-1)
        hrs = df['下周HR'].dropna().tolist()
        all_hr.extend(hrs)
        for h in hrs: board_all[board].append(h)

        for _, row in df.iterrows():
            hr = row['下周HR']
            if pd.isna(hr): continue
            s = match_strategy(row)
            if s: strat_data[s][board].append(hr)

            wxcd = str(row.get('WXCD',''))
            wxab = str(row.get('WXAB',''))
            zhu = str(row.get('柱排周',''))
            bo = str(row.get('波型',''))
            ying = str(row.get('盈提示',''))
            za = row.get('ZA周', 0)
            ying_s = str(ying) if ying != 'nan' else ''
            is_silver = '银' in wxcd

            if is_silver:
                silver_data['银(全量)'].append(hr)
                if '己' in wxab: silver_data['银+WXAB=己'].append(hr)
                if '高' in ying_s or '宽' in ying_s: silver_data['银+盈提示有'].append(hr)
                if zhu and len(zhu) > 0 and zhu[0] == '升': silver_data['银+柱排=升'].append(hr)
                if '龙猪' in bo: silver_data['银+龙猪'].append(hr)
                if ('龙猪' in bo or '龙管' in bo) and '甲' in wxab: silver_data['银+龙猪/管+WXAB=甲'].append(hr)
                if '龙猪' in bo or '龙管' in bo: silver_data['银+龙猪/管'].append(hr)
                if '甲' in wxab: silver_data['银+WXAB=甲'].append(hr)
                if za > 5 and za <= 10: silver_data['银+ZA5~10'].append(hr)
    except: continue

def calc(vals):
    vals = [v for v in vals if not pd.isna(v)]
    if not vals: return (0,0,0,0,0,0)
    n = len(vals)
    return (n, sum(1 for x in vals if x>0)/n*100, sum(1 for x in vals if x>=1)/n*100,
            sum(1 for x in vals if x>=3)/n*100, sum(1 for x in vals if x>=5)/n*100, sum(vals)/n)

# 1. 全量基准
n, hr0, hr1, hr3, hr5, avg = calc(all_hr)
print(f"\n=== 全量基准 ===")
print(f"P(>0%)={hr0:.1f}%  P(>1%)={hr1:.1f}%  P(≥3%)={hr3:.1f}%  P(≥5%)={hr5:.1f}%  均HR={avg:.2f}%")

# 2. 金策略 × 市板
print(f"\n=== 金策略 × 市板 P(≥3%) ===")
boards = ['Qd','Qe','Qif','Qic','Qimit','Qin']
strats = ['金最优(全部)','金+盈高','金+升排+非孕','金+升排','金+多长']
header = f"{'策略':<22} {'全量':>8}"
for b in boards: header += f" {b:>8}"
print(header)
print('-' * 75)
for s in strats:
    all_v = []
    for b in boards: all_v.extend(strat_data[s].get(b, []))
    _, _, _, p3_all, _, _ = calc(all_v)
    row = f"{s:<22} {p3_all:>7.1f}%"
    for b in boards:
        v = strat_data[s].get(b, [])
        _, _, _, p3, _, _ = calc(v)
        row += f" {p3:>7.1f}%"
    print(row)

# 3. 银条件全量回测
print(f"\n=== 银条件全量回测 ===")
s_order = ['银(全量)','银+盈提示有','银+龙猪','银+柱排=升','银+龙猪/管+WXAB=甲','银+龙猪/管','银+WXAB=甲','银+ZA5~10','银+WXAB=己']
print(f"{'条件':<22} {'样本':>8} {'P(>0)':>7} {'均HR':>7} {'P(≥3%)':>7} {'P(≥5%)':>7}")
print('-' * 60)
for s in s_order:
    v = silver_data.get(s, [])
    n, hr0, _, hr3, hr5, avg = calc(v)
    if n > 0: print(f"{s:<22} {n:>8} {hr0:>6.1f}% {avg:>6.2f}% {hr3:>6.1f}% {hr5:>6.1f}%")

# 4. 市板分类
print(f"\n=== 市板分类 ===")
b_names = {'Qd':'指数','Qe':'基金ETF','Qif':'沪深300','Qic':'中证500','Qimit':'中证小盘','Qin':'非板块'}
for b in ['Qd','Qe','Qif','Qic','Qimit','Qin']:
    v = board_all.get(b, [])
    _, _, _, hr3, _, avg = calc(v)
    print(f"{b_names[b]:<10} 均HR={avg:.2f}%  P(≥3%)={hr3:.1f}%")

print(f"\n全量7463只: 均HR={sum(all_hr)/len(all_hr):.2f}%  P(≥3%)={sum(1 for x in all_hr if x>=3)/len(all_hr)*100:.1f}%")
print("Done")