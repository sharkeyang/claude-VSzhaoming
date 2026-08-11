import csv, os, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

datadir = r'昭明算展\谕组周'
files = sorted(os.listdir(datadir))
print(f'总文件: {len(files)}')

# 数据容器
wxab_stats = defaultdict(lambda: {'t': 0, 'cd_good': 0, 'cd_jin': 0})
wxab_cd = defaultdict(lambda: {'t': 0, 'ok': 0})
# ZC/ZA/ZB
z3 = defaultdict(lambda: {'t': 0, 'ok': 0})
# 波型/柱排
wave_jin = defaultdict(lambda: {'t': 0, 'ok': 0})
zp_jin = defaultdict(lambda: {'t': 0, 'ok': 0})
# 时间序列
ab_fwd_t = 0; ab_fwd_ok = 0  # WXAB转好→WXCD转好
ab_rev_t = 0; ab_rev_ok = 0   # WXAB转差→WXCD转差
cd_fwd_t = 0; cd_fwd_ok = 0   # WXCD转好→WXAB转好
cd_rev_t = 0; cd_rev_ok = 0   # WXCD转差→WXAB转差
# WXZA/WXZB
s1_t = 0; s1_zb_neg = 0  # WXAB>0, WXZA<0
s2_t = 0; s2_za_neg = 0; s2_zb_pos = 0  # WXAB<0, WXZA>0
# 金升+甲/乙
jina_t = 0; jina_ok = 0
jinb_t = 0; jinb_ok = 0
# 5周续持率
def is_多长(w):
    zc = float(w.get('ZC周', 0) or 0)
    zb = float(w.get('ZB周', 0) or 0)
    return zc > 0 and zb > 0 and ('金' in str(w.get('WXCD', '')))

processed = 0
for fname in files:
    code = fname.replace('谕组周_', '').replace('.csv', '')
    fp = os.path.join(datadir, fname)
    try:
        with open(fp, 'r', encoding='gbk') as f:
            rows = list(csv.DictReader(f))
    except:
        continue

    for i in range(len(rows) - 5):
        w = rows[i]
        wxcd = str(w.get('WXCD', ''))
        wxab = str(w.get('WXAB', ''))
        zc = float(w.get('ZC周', 0) or 0)
        za = float(w.get('ZA周', 0) or 0)
        zb = float(w.get('ZB周', 0) or 0)
        波型 = str(w.get('波型', ''))
        柱排 = str(w.get('柱排周', ''))
        w5 = rows[i + 5]
        still = is_多长(w5)
        cd_good = '金' in wxcd or '银' in wxcd
        cd_jin = '金升' in wxcd
        ab_good = '甲' in wxab or '乙' in wxab
        ab_bad = not ab_good

        # WXAB各等级金银率
        for ab in ['甲','乙','丙','丁','戊','己']:
            if ab in wxab:
                wxab_stats[ab]['t'] += 1
                if cd_good: wxab_stats[ab]['cd_good'] += 1
                if cd_jin: wxab_stats[ab]['cd_jin'] += 1
                break

        # 5周续持率 × WXAB
        for ab in ['甲','乙','丙','丁','戊','己']:
            if ab in wxab:
                wxab_cd[ab]['t'] += 1
                if still: wxab_cd[ab]['ok'] += 1
                break

        # 金升+甲/乙
        if cd_jin:
            if '甲' in wxab:
                jina_t += 1
                if still: jina_ok += 1
            if '乙' in wxab:
                jinb_t += 1
                if still: jinb_ok += 1

        # ZC/ZA/ZB
        z3key = f'ZC{"+" if zc>0 else "-"}|ZA{"+" if za>0 else "-"}|ZB{"+" if zb>0 else "-"}'
        z3[z3key]['t'] += 1
        if still: z3[z3key]['ok'] += 1

        # 金升+波型
        if cd_jin:
            for wt in ['龙猪','龙管','头正','震正','震负']:
                if wt in 波型:
                    wave_jin[wt]['t'] += 1
                    if still: wave_jin[wt]['ok'] += 1
                    break
            # 金升+柱排
            if 柱排.startswith('升'):
                zp_jin['升排']['t'] += 1
                if still: zp_jin['升排']['ok'] += 1
            elif 柱排.startswith('跌'):
                zp_jin['跌排']['t'] += 1
                if still: zp_jin['跌排']['ok'] += 1

        # WXZA/WXZB场景
        if ab_good and za < 0:
            s1_t += 1
            if zb < 0: s1_zb_neg += 1
        if ab_bad and za > 0 and i < len(rows) - 1:
            s2_t += 1
            n_za = float(rows[i+1].get('ZA周', 0) or 0)
            n_zb = float(rows[i+1].get('ZB周', 0) or 0)
            if n_za < 0: s2_za_neg += 1
            if n_zb > 0: s2_zb_pos += 1

        # 时间序列
        if i > 0:
            prev = rows[i-1]
            p_ab = str(prev.get('WXAB', ''))
            p_cd = str(prev.get('WXCD', ''))
            p_ab_good = '甲' in p_ab or '乙' in p_ab
            p_cd_good = '金' in p_cd or '银' in p_cd
            c_ab_good = ab_good
            c_cd_good = cd_good

            if not p_ab_good and c_ab_good:  # AB转好
                ab_fwd_t += 1
                if c_cd_good and not p_cd_good: ab_fwd_ok += 1
            if p_ab_good and not c_ab_good:  # AB转差
                ab_rev_t += 1
                if not c_cd_good and p_cd_good: ab_rev_ok += 1
            if not p_cd_good and c_cd_good:  # CD转好
                cd_fwd_t += 1
                if c_ab_good and not p_ab_good: cd_fwd_ok += 1
            if p_cd_good and not c_cd_good:  # CD转差
                cd_rev_t += 1
                if not c_ab_good and p_ab_good: cd_rev_ok += 1

    processed += 1
    if processed % 1000 == 0:
        print(f'  已处理: {processed}/{len(files)}', flush=True)

# 输出结果
print('\n' + '='*60)
print('全量7463只 月基策略数据')
print('='*60)

print('\n1. WXAB各等级金银率：')
for ab in ['甲','乙','丙','丁','戊','己']:
    d = wxab_stats[ab]
    pct_g = d['cd_good']/d['t']*100
    pct_j = d['cd_jin']/d['t']*100
    print(f'  WXAB={ab}: {d["t"]:>7}次, <金银>率 {pct_g:>5.1f}%, <多长>率 {pct_j:>5.1f}%')

print('\n2. WXAB各等级5周续持率：')
for ab in ['甲','乙','丙','丁','戊','己']:
    d = wxab_cd[ab]
    pct = d['ok']/d['t']*100
    print(f'  WXAB={ab}: {d["t"]:>7}次, 5周续持率 {pct:>5.1f}%')

print(f'\n3. 金升+甲: {jina_t}次, 5周续持率 {jina_ok/jina_t*100:.1f}%')
print(f'   金升+乙: {jinb_t}次, 5周续持率 {jinb_ok/jinb_t*100:.1f}%')

print('\n4. WXAB>0且WXZA<0 → WXZB<0: {}/{} = {:.1f}%'.format(s1_zb_neg, s1_t, s1_zb_neg/s1_t*100))
print(f'    WXAB<0且WXZA>0 → 下周WXZA<0: {s2_za_neg}/{s2_t} = {s2_za_neg/s2_t*100:.1f}%')
print(f'    WXAB<0且WXZA>0 → 下周WXZB>0: {s2_zb_pos}/{s2_t} = {s2_zb_pos/s2_t*100:.1f}%')

print(f'\n5. WXAB转好→WXCD转好: {ab_fwd_ok}/{ab_fwd_t} = {ab_fwd_ok/ab_fwd_t*100:.1f}%')
print(f'    WXAB转差→WXCD转差: {ab_rev_ok}/{ab_rev_t} = {ab_rev_ok/ab_rev_t*100:.1f}%')
print(f'    WXCD转好→WXAB转好: {cd_fwd_ok}/{cd_fwd_t} = {cd_fwd_ok/cd_fwd_t*100:.1f}%')
print(f'    WXCD转差→WXAB转差: {cd_rev_ok}/{cd_rev_t} = {cd_rev_ok/cd_rev_t*100:.1f}%')

print('\n6. ZC/ZA/ZB三线组合：')
for key in sorted(z3.keys()):
    d = z3[key]
    pct = d['ok']/d['t']*100
    print(f'  {key}: {d["t"]:>7}次, 5周续持率 {pct:>5.1f}%')

print('\n7. 金升+波型：')
for wt in ['龙猪','龙管','头正','震正','震负']:
    d = wave_jin[wt]
    if d['t'] > 0:
        print(f'  金升+{wt}: {d["t"]:>7}次, 5周续持率 {d["ok"]/d["t"]*100:.1f}%')

print('\n8. 金升+柱排：')
for zp in ['升排','跌排']:
    d = zp_jin[zp]
    if d['t'] > 0:
        print(f'  金升+{zp}: {d["t"]:>7}次, 5周续持率 {d["ok"]/d["t"]*100:.1f}%')