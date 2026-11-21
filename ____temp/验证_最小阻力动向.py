# -*- coding: utf-8 -*-
"""验证最小阻力动向理论（2026-11-15）— WXZC>0 口径，与§8.6一致
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
COL_ZHOUZHANG = 1
COL_HR = 3
COL_WXZA = 18
COL_WXZB = 19
COL_WXZC = 20
COL_WXAB = 24
COL_BF = 53

def to_float(s):
    try: return float(s)
    except: return None

def main():
    by_fid = defaultdict(list)
    for f in glob.glob(os.path.join(DATA_DIR, '谕组周_*.csv')):
        fid = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
        with open(f, encoding='gbk') as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                if len(row) >= 54:
                    by_fid[fid].append(row)

    recs = []
    for fid, rlist in by_fid.items():
        for i, row in enumerate(rlist):
            next_hr = to_float(rlist[i+1][COL_HR]) if i+1 < len(rlist) else None
            next_zz = to_float(rlist[i+1][COL_ZHOUZHANG]) if i+1 < len(rlist) else None
            if next_hr is None:
                continue
            wxzc = to_float(row[COL_WXZC])
            if wxzc is None or wxzc <= 0:   # 只取 WXZC>0
                continue
            bf = row[COL_BF]
            ct = bf[-1] if bf else '?'
            pt = bf[-2] if len(bf) >= 2 else '?'
            p2t = bf[-3] if len(bf) >= 3 else '?'
            p3t = bf[-4] if len(bf) >= 4 else '?'
            wxza = to_float(row[COL_WXZA])
            wxzb = to_float(row[COL_WXZB])
            wxab = to_float(row[COL_WXAB])
            recs.append((ct, pt, p2t, p3t, wxza, wxzb, wxab, next_hr, next_zz))
    print(f'WXZC>0 有效行数: {len(recs)}', flush=True)

    def stats(cond, label):
        n = hr3 = hr1 = up = 0
        for ct, pt, p2t, p3t, wxza, wxzb, wxab, next_hr, next_zz in recs:
            if cond(ct, pt, p2t, p3t, wxza, wxzb, wxab):
                n += 1
                if next_hr >= 3: hr3 += 1
                if next_hr >= 1: hr1 += 1
                if next_zz is not None and next_zz > 0: up += 1
        if n == 0:
            print(f'{label}: n=0', flush=True); return
        print(f'{label}: n={n:,} | 涨>0 {up/n*100:.1f}% | HR>=1% {hr1/n*100:.1f}% | HR>=3% {hr3/n*100:.1f}%', flush=True)

    def wxab_pos(wxab): return wxab is not None and wxab > 0
    def wxza_pos(wxza): return wxza is not None and wxza > 0
    def wxza_neg(wxza): return wxza is not None and wxza < 0
    def wxzb_neg(wxzb): return wxzb is not None and wxzb < 0
    def shengpai(ct): return ct in ('Q','O','o','v')
    def diepai(ct): return ct in ('V','W')

    print('\n===== 1. 无阻链 vs 有阻链 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: wxab_pos(ab) and wxza_pos(za) and shengpai(ct), '无阻链(升排)')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: wxab_pos(ab) and wxza_pos(za) and diepai(ct), '有阻链(跌排)')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: wxab_pos(ab) and wxza_pos(za), '沃土全量')

    print('\n===== 2. 前柱升连 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: pt == 'Q', '前柱升连')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: pt == 'Q' and ct in ('Q','O','o'), '前柱升连+当前阳')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: pt == 'Q' and ct in ('V','v'), '前柱升连+当前阴')

    print('\n===== 3. 升连+单阴 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p2t == 'Q' and pt in ('V','v'), '前2柱升连+前柱单阴')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p2t == 'Q' and pt in ('V','v') and ct in ('O','o','Q'), '升连+单阴+当前阳')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p2t == 'Q' and pt in ('V','v') and ct in ('V','W','v'), '升连+单阴+当前阴')

    print('\n===== 4. 升连+单阴+单阳 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p2t in ('V','v') and pt in ('O','o','Q') and ct in ('V','W','v'), '升连+单阴+单阳+当前阴')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p2t in ('V','v') and pt in ('O','o','Q') and ct == 'Q', '升连+单阴+单阳+当前升连')

    print('\n===== 5. 升连+单阴+跌连 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p3t == 'Q' and p2t in ('V','v') and pt == 'W', '前3柱升连+前2柱单阴+前柱跌连')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p3t == 'Q' and p2t in ('V','v') and pt == 'W' and ct in ('O','o','Q'), '升连+单阴+跌连+当前阳')

    print('\n===== 6. WJA之上跌吞/跌连 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: wxza_pos(za) and ct in ('V','W'), 'WXZA>0+跌吞/跌连')

    print('\n===== 7. 三柱平移 =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: p2t not in ('Q','W') and pt not in ('Q','W') and ct not in ('Q','W'), '三柱平移')

    print('\n===== 8. 下破WJA/WJB =====', flush=True)
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: wxza_neg(za), 'WXZA<0(下破WJA)')
    stats(lambda ct,pt,p2t,p3t,za,zb,ab: wxzb_neg(zb), 'WXZB<0(下破WJB)')

if __name__ == '__main__':
    main()
