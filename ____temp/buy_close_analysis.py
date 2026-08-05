# -*- coding: utf-8 -*-
"""收盘买入→次日分析"""
import sys, io, csv, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
datadir = '昭明算展/谕组日'
files = sorted(os.listdir(datadir))[:100]

def 是继鼎(zp):
    return zp.startswith('升.尾')

perf = defaultdict(list)

# H_/T_稳态
for fname in files:
    try:
        rows = []
        with open(os.path.join(datadir, fname), 'r', encoding='gbk') as f:
            for row in csv.DictReader(f):
                dxab = str(row.get('DXAB','')).strip()
                za_s = row.get('日ZA','').strip()
                nxt_gf_s = row.get('次日高幅','').strip()
                ret_s = row.get('涨幅','').strip()
                zp = str(row.get('柱排','')).strip()
                bx = str(row.get('波型','')).strip()
                try: za = float(za_s)
                except: continue
                try: nxt_gf = float(nxt_gf_s)
                except: nxt_gf = 0
                try: ret = float(ret_s)
                except: ret = 0
                hu = HU_MAP.get(dxab[0] if dxab else '', '')
                rows.append({'za':za,'nxt_gf':nxt_gf,'ret':ret,'zp':zp,'hu':hu,'bx':bx})
    except: continue
    if len(rows) < 5: continue
    for i in range(len(rows)):
        r = rows[i]
        nxt_gf = r['nxt_gf']
        nxt_ret = rows[i+1]['ret'] if i+1 < len(rows) else 0
        if r['za'] > 0:
            if r['zp'].startswith('升') and 'C' in r['bx']:
                perf['H1_升_触顶预警'].append((nxt_gf, nxt_ret))
            elif r['zp'].startswith('升') and r['hu'] in ['甲','己']:
                perf['H2_升_甲己强势'].append((nxt_gf, nxt_ret))
            elif r['zp'].startswith('升'):
                perf['H3_升_乙戊普通'].append((nxt_gf, nxt_ret))
            elif r['zp'].startswith('跌'):
                perf['H6_跌_高位回落'].append((nxt_gf, nxt_ret))
            elif r['za'] <= 3:
                perf['H4_人_近DJA'].append((nxt_gf, nxt_ret))
            else:
                perf['H5_人_盘整中'].append((nxt_gf, nxt_ret))
        elif r['za'] < 0:
            if r['zp'].startswith('升') and r['hu'] in ['乙','戊','丙','丁']:
                perf['T1_升_乙戊反弹'].append((nxt_gf, nxt_ret))
            elif r['zp'].startswith('跌'):
                perf['T2_跌_跌势持续'].append((nxt_gf, nxt_ret))
            elif r['za'] >= -3:
                perf['T3_人_近DJA'].append((nxt_gf, nxt_ret))
            else:
                perf['T4_人_深跌中'].append((nxt_gf, nxt_ret))

# S_/I_转折态
for fname in files:
    try:
        rows = []
        with open(os.path.join(datadir, fname), 'r', encoding='gbk') as f:
            for row in csv.DictReader(f):
                za_s = row.get('日ZA','').strip()
                ret_s = row.get('涨幅','').strip()
                nxt_gf_s = row.get('次日高幅','').strip()
                zp = str(row.get('柱排','')).strip()
                try: za = float(za_s)
                except: continue
                try: ret = float(ret_s)
                except: ret = 0
                try: nxt_gf = float(nxt_gf_s)
                except: nxt_gf = 0
                rows.append({'za':za,'ret':ret,'nxt_gf':nxt_gf,'zp':zp})
    except: continue
    if len(rows) < 20: continue
    for i in range(1, len(rows)):
        prev = rows[i-1]; curr = rows[i]
        if prev['za'] > 0 and curr['za'] <= 0:
            pre5 = rows[max(0,i-5):i]
            za_vals = [r['za'] for r in pre5]
            max_za = max(za_vals) if za_vals else 0
            min_za = min(za_vals) if za_vals else 0
            za_drop = prev['za'] - curr['za']
            dr = curr['ret']
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
                p = 'S1_暴跌_暴跌破位'
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
            nxt_gf = curr['nxt_gf']
            nxt_ret = rows[i+1]['ret'] if i+1 < len(rows) else 0
            perf[p].append((nxt_gf, nxt_ret))
        if prev['za'] < 0 and curr['za'] >= 0:
            pre5 = rows[max(0,i-5):i]
            za_vals = [r['za'] for r in pre5]
            min_za = min(za_vals) if za_vals else 0
            max_za = max(za_vals) if za_vals else 0
            za_rise = curr['za'] - prev['za']
            rr = curr['ret']
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
                p = 'I1_暴涨_暴涨突破'
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
            nxt_gf = curr['nxt_gf']
            nxt_ret = rows[i+1]['ret'] if i+1 < len(rows) else 0
            perf[p].append((nxt_gf, nxt_ret))

print('收盘买入->次日分析 (按P(>=3%)=吃大肉概率降序)')
print('='*105)
print('{:>26s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}'.format(
    '状态','样本','明高率','P(>=3%)','P(>=2%)','P(>=1%)','均高%','均涨%'))
print('-'*105)
results = []
for state, data in perf.items():
    n = len(data)
    if n < 100: continue
    mg = sum(1 for d in data if d[0] > 0) / n * 100
    p3 = sum(1 for d in data if d[0] >= 3) / n * 100
    p2 = sum(1 for d in data if d[0] >= 2) / n * 100
    p1 = sum(1 for d in data if d[0] >= 1) / n * 100
    avg_gf = sum(d[0] for d in data) / n
    avg_ret = sum(d[1] for d in data) / n
    results.append((state, n, mg, p3, p2, p1, avg_gf, avg_ret))
results.sort(key=lambda x: x[3], reverse=True)
for state, n, mg, p3, p2, p1, avg_gf, avg_ret in results:
    print('{:>26s} {:>8,} {:>7.1f}% {:>7.1f}% {:>7.1f}% {:>7.1f}% {:>+7.2f}% {:>+7.2f}%'.format(
        state, n, mg, p3, p2, p1, avg_gf, avg_ret))
print()
print('明高率=次日冲高>0%  P(>=3%)=次日冲高>=3%  P(>=2%)=次日冲高>=2%')
print('P(>=1%)=次日冲高>=1%  均高%=次日平均冲高幅度  均涨%=次日收盘涨跌')