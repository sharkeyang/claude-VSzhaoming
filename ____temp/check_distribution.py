# -*- coding: utf-8 -*-
"""日冲22态分布验证"""
import sys, io, csv, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict
import datetime as dt

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
datadir = '昭明算展/谕组日'
files = sorted(os.listdir(datadir))[:200]

def 是继鼎(zp):
    return zp.startswith('升.尾')

counts = defaultdict(int)

for fname in files:
    try:
        rows = []
        with open(os.path.join(datadir, fname), 'r', encoding='gbk') as f:
            for row in csv.DictReader(f):
                dxab = str(row.get('DXAB','')).strip()
                za_s = row.get('日ZA','').strip()
                ret_s = row.get('涨幅','').strip()
                nxt_gf_s = row.get('次日高幅','').strip()
                zp = str(row.get('柱排','')).strip()
                bx = str(row.get('波型','')).strip()
                try: za = float(za_s)
                except: continue
                try: ret = float(ret_s)
                except: ret = 0
                try: nxt_gf = float(nxt_gf_s)
                except: nxt_gf = 0
                hu = HU_MAP.get(dxab[0] if dxab else '', '')
                rows.append({'za':za,'ret':ret,'nxt_gf':nxt_gf,'zp':zp,'hu':hu,'bx':bx})
    except: continue
    if len(rows) < 5: continue

    # H_ 稳态
    for i in range(len(rows)):
        r = rows[i]
        if r['za'] > 0:
            if r['zp'].startswith('升') and 'C' in r['bx']:
                counts['H1_升_日中符C'] += 1
            elif r['zp'].startswith('升') and r['hu'] in ['甲','乙','己']:
                counts['H2_升_护型强'] += 1
            elif r['zp'].startswith('升'):
                counts['H3_升_护型弱'] += 1
            elif r['zp'].startswith('跌'):
                counts['H6_跌_跌排'] += 1
            elif r['za'] <= 3:
                counts['H4_人_ZA3内'] += 1
            else:
                counts['H5_人_ZA3外'] += 1
        elif r['za'] < 0:
            if r['zp'].startswith('升') and r['hu'] in ['丙','丁','戊']:
                counts['T1_升_护型弱'] += 1
            elif r['zp'].startswith('跌'):
                counts['T2_跌_跌排'] += 1
            elif r['za'] >= -3:
                counts['T3_人_ZA3内'] += 1
            else:
                counts['T4_人_ZA3外'] += 1

    # S_/I_ 转折态
    for i in range(1, len(rows)):
        prev = rows[i-1]; curr = rows[i]
        # S_ 正转负
        if prev['za'] > 0 and curr['za'] <= 0:
            pre5 = rows[max(0,i-5):i]
            za_drop = prev['za'] - curr['za']
            dr = curr['ret']
            za_vals = [r['za'] for r in pre5]
            max_za = max(za_vals) if za_vals else 0
            min_za = min(za_vals) if za_vals else 0
            streak_yin = 0
            for j in range(len(rows[max(0,i-10):i])-1,-1,-1):
                if rows[max(0,i-10):i][j]['ret'] < 0: streak_yin += 1
                else: break
            pre3 = [rows[j]['zp'] for j in range(max(0,i-3), i)]
            all_not_die = all(not z.startswith('跌') for z in pre3)
            has_jd = any(是继鼎(r['zp']) for r in pre5)
            hb = False
            if len(pre5) >= 3:
                mi = za_vals.index(min(za_vals))
                am = za_vals[mi:]
                dja = 5 if has_jd else 3
                if len(am) >= 2 and min(za_vals) <= dja and max(am) - am[0] >= 2:
                    hb = True
            if za_drop >= 3 and dr <= -2 and all_not_die:
                p = 'S1_暴跌_大柱下破'
            elif streak_yin >= 3 and max_za >= 2 and dr > -2:
                p = 'S5_碎步_缓步阴跌'
            elif hb:
                p = 'S2_归JA_反弹失败'
            elif min_za <= (5 if has_jd else 3):
                p = 'S3_归JA_直破DJA'
            else:
                p = 'S6_其他_其他跌破'
            if p in ['S3_归JA_直破DJA','S6_其他_其他跌破'] and all(r['za']>=3 for r in pre5):
                for j in range(i+1, min(i+15, len(rows))):
                    if rows[j]['za'] == 1:
                        for k in range(j+1, min(j+10, len(rows))):
                            if rows[k]['za'] <= 0:
                                if k - j <= 5: p = 'S4_双穿_M头逃命'
                                break
                        break
            counts[p] += 1

        # I_ 负转正
        if prev['za'] < 0 and curr['za'] >= 0:
            pre5 = rows[max(0,i-5):i]
            za_rise = curr['za'] - prev['za']
            rr = curr['ret']
            za_vals = [r['za'] for r in pre5]
            min_za = min(za_vals) if za_vals else 0
            max_za = max(za_vals) if za_vals else 0
            streak_yang = 0
            for j in range(len(rows[max(0,i-10):i])-1,-1,-1):
                if rows[max(0,i-10):i][j]['ret'] > 0: streak_yang += 1
                else: break
            has_jd = any(是继鼎(r['zp']) for r in pre5)
            hf = False
            if len(pre5) >= 3:
                mi = za_vals.index(max(za_vals))
                am = za_vals[mi:]
                dja = -5 if has_jd else -3
                if len(am) >= 2 and max(za_vals) >= dja and am[0] - min(am) >= 2:
                    hf = True
            if za_rise >= 3 and rr >= 2:
                p = 'I1_暴涨_大柱上破'
            elif streak_yang >= 3 and min_za <= -2 and rr < 2:
                p = 'I5_碎步_缓步上升'
            elif hf:
                p = 'I2_归JA_回落确认'
            elif max_za >= (-5 if has_jd else -3):
                p = 'I3_归JA_直上DJA'
            else:
                p = 'I6_其他_其他上破'
            if p in ['I3_归JA_直上DJA','I6_其他_其他上破'] and all(r['za']<=-3 for r in pre5):
                for j in range(i+1, min(i+15, len(rows))):
                    if rows[j]['za'] == -1:
                        for k in range(j+1, min(j+10, len(rows))):
                            if rows[k]['za'] >= 0:
                                if k - j <= 5: p = 'I4_双穿_M底加仓'
                                break
                        break
            counts[p] += 1

total = sum(counts.values())
print('日冲22态分布（200只股票子集）')
print('=' * 60)
print('{:>26s} {:>8s} {:>8s}'.format('状态','次数','占比'))
print('-' * 60)
states = ['H1_升_日中符C','H2_升_护型强','H3_升_护型弱','H4_人_ZA3内','H5_人_ZA3外','H6_跌_跌排',
          'T1_升_护型弱','T2_跌_跌排','T3_人_ZA3内','T4_人_ZA3外',
          'I1_暴涨_大柱上破','I2_归JA_回落确认','I3_归JA_直上DJA','I4_双穿_M底加仓','I5_碎步_缓步上升','I6_其他_其他上破',
          'S1_暴跌_大柱下破','S2_归JA_反弹失败','S3_归JA_直破DJA','S4_双穿_M头逃命','S5_碎步_缓步阴跌','S6_其他_其他跌破']
for s in states:
    c = counts.get(s, 0)
    print('{:>26s} {:>8,} {:>7.1f}%'.format(s, c, c/total*100))
print('-' * 60)
print('{:>26s} {:>8,}'.format('合计', total))