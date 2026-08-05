import csv, os, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

datadir = r'昭明算展\谕组周'
files = sorted(os.listdir(datadir))[:500]
stock_data = defaultdict(list)

for fname in files:
    code = fname.replace('谕组周_', '').replace('.csv', '')
    fp = os.path.join(datadir, fname)
    with open(fp, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['code'] = code
            stock_data[code].append(row)

def is_多长(w):
    zc = float(w.get('ZC周', 0) or 0)
    zb = float(w.get('ZB周', 0) or 0)
    return zc > 0 and zb > 0 and ('金' in str(w.get('WXCD', '')))

# 规律1: WXCD变化后WXAB的跟随
print('=== 规律1: WXCD变化后WXAB的跟随 ===')
cd_to_good = 0; cd_to_good_t = 0
cd_to_bad = 0; cd_to_bad_t = 0

for code, weeks in stock_data.items():
    for i in range(1, len(weeks)):
        prev = weeks[i-1]; curr = weeks[i]
        p_cd = str(prev.get('WXCD', '')); c_cd = str(curr.get('WXCD', ''))
        p_ab = str(prev.get('WXAB', '')); c_ab = str(curr.get('WXAB', ''))
        p_cd_good = '金' in p_cd or '银' in p_cd
        c_cd_good = '金' in c_cd or '银' in c_cd
        p_ab_good = '甲' in p_ab or '乙' in p_ab
        c_ab_good = '甲' in c_ab or '乙' in c_ab

        if not p_cd_good and c_cd_good:
            cd_to_good_t += 1
            if not p_ab_good and c_ab_good:
                cd_to_good += 1
        if p_cd_good and not c_cd_good:
            cd_to_bad_t += 1
            if p_ab_good and not c_ab_good:
                cd_to_bad += 1

print(f'WXCD转好->WXAB跟随转好: {cd_to_good}/{cd_to_good_t} = {cd_to_good/cd_to_good_t*100:.1f}%')
print(f'WXCD转差->WXAB跟随转差: {cd_to_bad}/{cd_to_bad_t} = {cd_to_bad/cd_to_bad_t*100:.1f}%')

# 规律2: ZC/ZA/ZB三线状态组合 -> 续持率
print('\n=== 规律2: ZC/ZA/ZB三线组合 -> 5周续持率 ===')
zc_za_zb = defaultdict(lambda: {'t': 0, 'ok': 0})
for code, weeks in stock_data.items():
    for i in range(len(weeks) - 5):
        w = weeks[i]
        zc = float(w.get('ZC周', 0) or 0)
        za = float(w.get('ZA周', 0) or 0)
        zb = float(w.get('ZB周', 0) or 0)
        key = f'ZC{"+" if zc>0 else "-"}|ZA{"+" if za>0 else "-"}|ZB{"+" if zb>0 else "-"}'
        zc_za_zb[key]['t'] += 1
        if is_多长(weeks[i+5]):
            zc_za_zb[key]['ok'] += 1

for key in sorted(zc_za_zb.keys()):
    d = zc_za_zb[key]
    pct = d['ok']/d['t']*100
    print(f'  {key}: {d["t"]:>6}次, 5周续持率 {pct:>5.1f}%')

# 规律3: 波型+金升 -> 续持率
print('\n=== 规律3: 金升+波型 -> 5周续持率 ===')
wave_cd = defaultdict(lambda: {'t': 0, 'ok': 0})
for code, weeks in stock_data.items():
    for i in range(len(weeks) - 5):
        w = weeks[i]
        波型 = str(w.get('波型', ''))
        wxcd = str(w.get('WXCD', ''))
        if '金升' not in wxcd:
            continue
        for wt in ['龙猪','龙管','头正','震正','震负']:
            if wt in 波型:
                wave_cd[wt]['t'] += 1
                if is_多长(weeks[i+5]):
                    wave_cd[wt]['ok'] += 1
                break

for wt in ['龙猪','龙管','头正','震正','震负']:
    d = wave_cd[wt]
    if d['t'] > 0:
        pct = d['ok']/d['t']*100
        print(f'  金升+{wt}: {d["t"]:>6}次, 5周续持率 {pct:>5.1f}%')

# 规律4: 柱排+金升 -> 续持率
print('\n=== 规律4: 金升+柱排 -> 5周续持率 ===')
zp_cd = defaultdict(lambda: {'t': 0, 'ok': 0})
for code, weeks in stock_data.items():
    for i in range(len(weeks) - 5):
        w = weeks[i]
        柱排 = str(w.get('柱排周', ''))
        wxcd = str(w.get('WXCD', ''))
        if '金升' not in wxcd:
            continue
        if 柱排.startswith('升'):
            zp_cd['升排']['t'] += 1
            if is_多长(weeks[i+5]): zp_cd['升排']['ok'] += 1
        elif 柱排.startswith('人'):
            zp_cd['人排']['t'] += 1
            if is_多长(weeks[i+5]): zp_cd['人排']['ok'] += 1
        elif 柱排.startswith('跌'):
            zp_cd['跌排']['t'] += 1
            if is_多长(weeks[i+5]): zp_cd['跌排']['ok'] += 1

for zp in ['升排','人排','跌排']:
    d = zp_cd[zp]
    if d['t'] > 0:
        pct = d['ok']/d['t']*100
        print(f'  金升+{zp}: {d["t"]:>6}次, 5周续持率 {pct:>5.1f}%')

# 规律5: WXAB=乙时不同波型
print('\n=== 规律5: WXAB=乙+波型 -> 5周续持率 ===')
ab_yi_wave = defaultdict(lambda: {'t': 0, 'ok': 0})
for code, weeks in stock_data.items():
    for i in range(len(weeks) - 5):
        w = weeks[i]
        wxab = str(w.get('WXAB', ''))
        波型 = str(w.get('波型', ''))
        if '乙' not in wxab:
            continue
        for wt in ['龙猪','龙管','头正','震正','震负']:
            if wt in 波型:
                ab_yi_wave[wt]['t'] += 1
                if is_多长(weeks[i+5]):
                    ab_yi_wave[wt]['ok'] += 1
                break

for wt in ['龙猪','龙管','头正','震正','震负']:
    d = ab_yi_wave[wt]
    if d['t'] > 0:
        pct = d['ok']/d['t']*100
        print(f'  WXAB=乙+{wt}: {d["t"]:>6}次, 5周续持率 {pct:>5.1f}%')

# 规律6: WXAB=甲时不同波型
print('\n=== 规律6: WXAB=甲+波型 -> 5周续持率 ===')
ab_jia_wave = defaultdict(lambda: {'t': 0, 'ok': 0})
for code, weeks in stock_data.items():
    for i in range(len(weeks) - 5):
        w = weeks[i]
        wxab = str(w.get('WXAB', ''))
        波型 = str(w.get('波型', ''))
        if '甲' not in wxab:
            continue
        for wt in ['龙猪','龙管','头正','震正','震负']:
            if wt in 波型:
                ab_jia_wave[wt]['t'] += 1
                if is_多长(weeks[i+5]):
                    ab_jia_wave[wt]['ok'] += 1
                break

for wt in ['龙猪','龙管','头正','震正','震负']:
    d = ab_jia_wave[wt]
    if d['t'] > 0:
        pct = d['ok']/d['t']*100
        print(f'  WXAB=甲+{wt}: {d["t"]:>6}次, 5周续持率 {pct:>5.1f}%')