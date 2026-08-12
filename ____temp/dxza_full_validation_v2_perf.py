# -*- coding: utf-8 -*-
"""v2全量验证 + 性能指标计算（均涨%/涨率%/明高率%/明涨率%）"""
import csv, os, sys, io
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import datetime as dt

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
datadir = r'昭明算展\谕组日'
files = sorted(os.listdir(datadir))
print(f'总文件数: {len(files)}')

# 统计用
pattern_down = Counter()
pattern_up = Counter()
# 指标用：{状态: [涨幅, 明高, 明涨]}
perf_down = defaultdict(list)
perf_up = defaultdict(list)

def 是继鼎(zp):
    return zp.startswith('升.尾')

for fname in files:
    code = fname.replace('谕组日_','').replace('.csv','')
    try:
        rows = []
        with open(os.path.join(datadir, fname), 'r', encoding='gbk') as f:
            for row in csv.DictReader(f):
                date_s = str(row.get('日期','')).strip()
                if not date_s: continue
                try: d = dt.datetime.strptime(date_s, '%Y/%m/%d')
                except: continue
                za_s = str(row.get('日ZA','')).strip()
                ret_s = str(row.get('涨幅','')).strip()
                gf_s = str(row.get('高幅','')).strip()
                nxt_gf_s = str(row.get('次日高幅','')).strip()
                zp = str(row.get('柱排','')).strip()
                try: za = float(za_s)
                except: continue
                try: ret = float(ret_s)
                except: ret = 0
                try: gf = float(gf_s)
                except: gf = 0
                try: nxt_gf = float(nxt_gf_s)
                except: nxt_gf = 0
                rows.append({'za':za,'ret':ret,'gf':gf,'nxt_gf':nxt_gf,'zp':zp})
    except:
        continue
    if len(rows) < 5: continue

    # 正转负检测
    for i in range(1, len(rows)):
        prev = rows[i-1]; curr = rows[i]
        if prev['za'] > 0 and curr['za'] <= 0:
            pre5 = rows[max(0,i-5):i]
            za_drop = prev['za'] - curr['za']
            drop_ret = curr['ret']
            za_vals = [r['za'] for r in pre5]
            max_za = max(za_vals) if za_vals else 0
            min_za = min(za_vals) if za_vals else 0

            streak_yin = 0
            for j in range(len(rows[max(0,i-10):i])-1,-1,-1):
                if rows[max(0,i-10):i][j]['ret'] < 0: streak_yin += 1
                else: break

            pre3_zp = [rows[j]['zp'] for j in range(max(0,i-3), i)]
            all_not_die = all(not zp.startswith('跌') for zp in pre3_zp)

            has_继鼎 = any(是继鼎(r['zp']) for r in pre5)
            has_bounce = False
            if len(pre5) >= 3:
                min_idx = za_vals.index(min(za_vals))
                after_min = za_vals[min_idx:]
                dja_near = 5 if has_继鼎 else 3
                if len(after_min) >= 2 and min(za_vals) <= dja_near:
                    if max(after_min) - after_min[0] >= 2:
                        has_bounce = True

            if za_drop >= 3 and drop_ret <= -2 and all_not_die:
                p = 'P4'
            elif streak_yin >= 3 and max_za >= 2 and drop_ret > -2:
                p = 'P1'
            elif has_bounce:
                p = 'P2'
            elif min_za <= (5 if has_继鼎 else 3):
                p = 'P0a'
            else:
                p = 'P0d'

            # 第二轮：P3检测
            if p in ['P0d', 'P0a']:
                pre5_all = rows[max(0,i-5):i]
                if all(r['za'] >= 3 for r in pre5_all):
                    is_p3 = False
                    for j in range(i+1, min(i+15, len(rows))):
                        if rows[j]['za'] == 1:
                            for k in range(j+1, min(j+10, len(rows))):
                                if rows[k]['za'] <= 0:
                                    dtza = k - j
                                    if dtza <= 5:
                                        is_p3 = True
                                    break
                            if is_p3: break
                    if is_p3:
                        p = 'P3'

            pattern_down[p] += 1
            # 性能指标：当前涨幅 + 次日高幅 + 次日涨幅
            ret_val = curr['ret']
            nxt_gf = curr['nxt_gf']
            nxt_ret = rows[i+1]['ret'] if i+1 < len(rows) else 0
            perf_down[p].append((ret_val, nxt_gf, nxt_ret))

    # 负转正检测
    for i in range(1, len(rows)):
        prev = rows[i-1]; curr = rows[i]
        if prev['za'] < 0 and curr['za'] >= 0:
            pre5 = rows[max(0,i-5):i]
            za_rise = curr['za'] - prev['za']
            rise_ret = curr['ret']
            za_vals = [r['za'] for r in pre5]
            min_za = min(za_vals) if za_vals else 0
            max_za = max(za_vals) if za_vals else 0

            streak_yang = 0
            for j in range(len(rows[max(0,i-10):i])-1,-1,-1):
                if rows[max(0,i-10):i][j]['ret'] > 0: streak_yang += 1
                else: break

            has_继鼎 = any(是继鼎(r['zp']) for r in pre5)
            has_fall = False
            if len(pre5) >= 3:
                max_idx = za_vals.index(max(za_vals))
                after_max = za_vals[max_idx:]
                dja_near = -5 if has_继鼎 else -3
                if len(after_max) >= 2 and max(za_vals) >= dja_near:
                    if after_max[0] - min(after_max) >= 2:
                        has_fall = True

            if za_rise >= 3 and rise_ret >= 2:
                p = 'M4'
            elif streak_yang >= 3 and min_za <= -2 and rise_ret < 2:
                p = 'M1'
            elif has_fall:
                p = 'M2'
            elif max_za >= (-5 if has_继鼎 else -3):
                p = 'M0a'
            else:
                p = 'M0d'

            # 第二轮：M3检测
            if p in ['M0d', 'M0a']:
                pre5_all = rows[max(0,i-5):i]
                if all(r['za'] <= -3 for r in pre5_all):
                    is_m3 = False
                    for j in range(i+1, min(i+15, len(rows))):
                        if rows[j]['za'] == -1:
                            for k in range(j+1, min(j+10, len(rows))):
                                if rows[k]['za'] >= 0:
                                    dtza = k - j
                                    if dtza <= 5:
                                        is_m3 = True
                                    break
                            if is_m3: break
                    if is_m3:
                        p = 'M3'

            pattern_up[p] += 1
            ret_val = curr['ret']
            nxt_gf = curr['nxt_gf']
            nxt_ret = rows[i+1]['ret'] if i+1 < len(rows) else 0
            perf_up[p].append((ret_val, nxt_gf, nxt_ret))

# ===== 输出 =====
def calc_perf(perf_dict):
    """计算性能指标: 均涨%, 涨率%, 明高率%, 明涨率%"""
    result = {}
    for p, data in perf_dict.items():
        n = len(data)
        if n == 0:
            result[p] = (0, 0, 0, 0)
            continue
        avg_ret = sum(d[0] for d in data) / n
        win_rate = sum(1 for d in data if d[0] > 0) / n * 100
        mingao = sum(1 for d in data if d[1] > 0) / n * 100
        ming_zhang = sum(1 for d in data if d[2] > 0) / n * 100
        result[p] = (avg_ret, win_rate, mingao, ming_zhang)
    return result

total_down = sum(pattern_down.values())
total_up = sum(pattern_up.values())
perf_d = calc_perf(perf_down)
perf_u = calc_perf(perf_up)

print(f'\n总柱数: 20,039,849')
print(f'正转负事件: {total_down:,}')
print(f'负转正事件: {total_up:,}')

print(f'\n{"="*100}')
print(f'正转负6种模式 — v2全量（{total_down:,}事件，含性能指标）')
print(f'{"="*100}')
print(f'{"编码":>6} {"次数":>10} {"占比":>8} {"均涨%":>8} {"涨率%":>6} {"明高率%":>8} {"明涨率%":>8}')
print(f'{"-"*100}')
for p in ['P4','P2','P1','P3','P0a','P0d']:
    c = pattern_down[p]
    avg, wr, mg, mz = perf_d.get(p, (0,0,0,0))
    print(f'{p:>6} {c:>10,} {c/total_down*100:>7.1f}% {avg:>+7.2f}% {wr:>5.1f}% {mg:>7.1f}% {mz:>7.1f}%')

print(f'\n{"="*100}')
print(f'负转正6种模式 — v2全量（{total_up:,}事件，含性能指标）')
print(f'{"="*100}')
print(f'{"编码":>6} {"次数":>10} {"占比":>8} {"均涨%":>8} {"涨率%":>6} {"明高率%":>8} {"明涨率%":>8}')
print(f'{"-"*100}')
for p in ['M4','M2','M1','M3','M0a','M0d']:
    c = pattern_up[p]
    avg, wr, mg, mz = perf_u.get(p, (0,0,0,0))
    print(f'{p:>6} {c:>10,} {c/total_up*100:>7.1f}% {avg:>+7.2f}% {wr:>5.1f}% {mg:>7.1f}% {mz:>7.1f}%')

# 遗漏检测
sum_down = sum(pattern_down[p] for p in ['P4','P2','P1','P3','P0a','P0d'])
sum_up = sum(pattern_up[p] for p in ['M4','M2','M1','M3','M0a','M0d'])
print(f'\n遗漏检测: 正转负={total_down-sum_down} 负转正={total_up-sum_up}')
print(f'{"✅ 无遗漏" if total_down == sum_down and total_up == sum_up else "❌ 有遗漏！"}')

# 对比v1性能指标
print(f'\n{"="*100}')
print(f'v1 vs v2 性能指标对比')
print(f'{"="*100}')
v1_perf = {
    'P4': (-4.19, 0.0, 87.2, 51.7),
    'P2': (-1.75, 1.4, 84.5, 45.8),
    'P1': (-0.83, 7.1, 87.5, 50.1),
    'P3': (-1.00, 5.0, 87.7, 51.6),
    'P0a': (-5.60, 0.0, 72.7, 41.6),
    'P0d': (-1.02, 4.5, 84.3, 41.0),
    'M4': (4.43, 100.0, 85.3, 48.8),
    'M2': (2.01, 97.1, 84.5, 48.9),
    'M1': (0.84, 89.3, 85.7, 49.4),
    'M3': (1.00, 92.0, 81.1, 44.0),
    'M0a': (10.01, 99.6, 82.7, 52.5),
    'M0d': (1.03, 92.7, 85.3, 52.3),
}
print(f'{"编码":>6} {"指标":>6} {"v1":>8} {"v2":>8} {"变化":>8}')
for p in ['P4','P2','P3','P0d','M2','M3','M0d']:
    v1d = v1_perf[p]
    v2d = perf_d.get(p) if p in perf_d else perf_u.get(p, (0,0,0,0))
    for idx, label in enumerate(['均涨%','涨率%','明高率%','明涨率%']):
        diff = v2d[idx] - v1d[idx]
        if abs(diff) > 0.05:
            print(f'{p:>6} {label:>6} {v1d[idx]:>+7.2f}% {v2d[idx]:>+7.2f}% {diff:>+7.2f}pp')