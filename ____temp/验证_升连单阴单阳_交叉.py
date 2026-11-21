# -*- coding: utf-8 -*-
"""验证升连+单阴+单阳：已拉升/未拉升 × 当前升连/当前阴柱 交叉
"""
import csv, glob, os
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
COL_HR = 3
COL_WXZA = 18
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
            if next_hr is None: continue
            wxzc = to_float(row[COL_WXZC])
            if wxzc is None or wxzc <= 0: continue
            bf = row[COL_BF]
            ct = bf[-1] if bf else '?'
            pt = bf[-2] if len(bf) >= 2 else '?'
            p2t = bf[-3] if len(bf) >= 3 else '?'
            wxza = to_float(row[COL_WXZA])
            wxab = to_float(row[COL_WXAB])
            prev_wxab = to_float(rlist[i-1][COL_WXAB]) if i-1 >= 0 else None
            prev_wxzc = to_float(rlist[i-1][COL_WXZC]) if i-1 >= 0 else None
            recs.append((ct, pt, p2t, wxza, wxab, prev_wxab, prev_wxzc, next_hr))
    print(f'WXZC>0 有效行数: {len(recs)}', flush=True)

    def stats(cond, label):
        n = hr3 = hr1 = 0
        for ct, pt, p2t, wxza, wxab, prev_wxab, prev_wxzc, next_hr in recs:
            if cond(ct, pt, p2t, wxza, wxab, prev_wxab, prev_wxzc):
                n += 1
                if next_hr >= 3: hr3 += 1
                if next_hr >= 1: hr1 += 1
        if n == 0:
            print(f'{label}: n=0', flush=True); return
        print(f'{label}: n={n:,} | HR>=1% {hr1/n*100:.1f}% | HR>=3% {hr3/n*100:.1f}%', flush=True)

    def is_3seq(ct, pt, p2t):
        return p2t in ('V','v') and pt in ('O','o','Q')
    def wxab_just(wxab, prev_wxab):
        return wxab is not None and wxab > 0 and prev_wxab is not None and prev_wxab <= 0
    def wxzc_just(wxzc, prev_wxzc):
        return wxzc is not None and wxzc > 0 and prev_wxzc is not None and prev_wxzc <= 0
    def not_just(za, ab, pab, pzc):
        return not (wxab_just(ab,pab) or wxzc_just(za,pzc))

    print('\n===== 升连+单阴+单阳：已拉升/未拉升 × 当前柱型 =====', flush=True)
    # 未拉升 + 当前升连
    stats(lambda ct,pt,p2t,za,ab,pab,pzc: is_3seq(ct,pt,p2t) and ct=='Q' and (wxab_just(ab,pab) or wxzc_just(za,pzc)), '未拉升+当前升连')
    # 未拉升 + 当前阴
    stats(lambda ct,pt,p2t,za,ab,pab,pzc: is_3seq(ct,pt,p2t) and ct in ('V','W','v') and (wxab_just(ab,pab) or wxzc_just(za,pzc)), '未拉升+当前阴')
    # 已拉升 + 当前升连
    stats(lambda ct,pt,p2t,za,ab,pab,pzc: is_3seq(ct,pt,p2t) and ct=='Q' and not_just(za,ab,pab,pzc), '已拉升+当前升连')
    # 已拉升 + 当前阴
    stats(lambda ct,pt,p2t,za,ab,pab,pzc: is_3seq(ct,pt,p2t) and ct in ('V','W','v') and not_just(za,ab,pab,pzc), '已拉升+当前阴')

if __name__ == '__main__':
    main()
