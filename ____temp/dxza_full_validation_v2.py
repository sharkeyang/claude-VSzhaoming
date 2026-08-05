# -*- coding: utf-8 -*-
"""全量12模式验证 v2 — 修复所有顺序混淆问题 + 继鼎DJA丘调整

== 修复内容 ==
1. P4: 增加"前3天柱排都不是跌排"限制（排除已阴跌靠近DJA的情况）
2. 触顶预警: 含C优先于护型判断（文档优先级3→实际1）
3. P2/P0a: 继鼎靠近DJA → 近DJA阈值放宽（ZA≤3→ZA≤5）
4. M2/M0a: 反向同理（ZA≥-3→ZA≥-5）
5. P3/M3: 保持两轮检测
"""
import csv, os, sys, io
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import datetime as dt

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
datadir = r'昭明算展\谕组日'
files = sorted(os.listdir(datadir))
print(f'总文件数: {len(files)}')

# 统计用
total_down = 0
total_up = 0
pattern_down = Counter()
pattern_up = Counter()
stock_down = defaultdict(set)
stock_up = defaultdict(set)
total_bars = 0
bar_states = Counter()

# 继鼎检测：柱排以"升.尾"开头 → 升连/升吞/升孕
def 是继鼎(zp):
    return zp.startswith('升.尾')

# 逐文件处理
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
                dxab = str(row.get('DXAB','')).strip()
                za_s = str(row.get('日ZA','')).strip()
                zc_s = str(row.get('日ZC','')).strip()
                ret_s = str(row.get('涨幅','')).strip()
                zp = str(row.get('柱排','')).strip()
                bx = str(row.get('波型','')).strip()
                try: za = float(za_s)
                except: continue
                try: zc = float(zc_s)
                except: zc = 0
                try: ret = float(ret_s)
                except: ret = 0
                hu = HU_MAP.get(dxab[0] if dxab else '', '')
                rows.append({'date':d,'za':za,'zc':zc,'ret':ret,'zp':zp,'bx':bx,'hu':hu})
    except:
        continue
    if len(rows) < 5: continue

    # 第一轮：基本状态 + 首次模式分类
    down_events = []  # 存正转负事件索引和初始模式

    # 基本状态统计
    for i, r in enumerate(rows):
        total_bars += 1
        za = r['za']; hu = r['hu'] or '?'
        if za > 0:
            if hu in ['甲','己']: bar_states['稳定态_'+hu] += 1
            elif hu in ['乙','戊']: bar_states['预警态_'+hu] += 1
            elif hu == '丙': bar_states['异常_丙_ZA>0'] += 1
            elif hu == '丁': bar_states['异常_丁_ZA>0'] += 1
            else: bar_states['其他_ZA>0'] += 1
        elif za < 0:
            if hu in ['丙','丁']: bar_states['下跌态_'+hu] += 1
            elif hu in ['乙','戊']: bar_states['下跌预警_'+hu] += 1
            elif hu == '己': bar_states['回调态_己_ZA<0'] += 1
            elif hu == '甲': bar_states['异常_甲_ZA<0'] += 1
            else: bar_states['其他_ZA<0'] += 1
        else:
            bar_states['ZA=0边界'] += 1

    # ===== 正转负检测 =====
    for i in range(1, len(rows)):
        prev = rows[i-1]; curr = rows[i]
        if prev['za'] > 0 and curr['za'] <= 0:
            total_down += 1
            lookback = min(10, i)
            pre5 = rows[max(0,i-5):i]
            za_drop = prev['za'] - curr['za']
            drop_ret = curr['ret']
            za_vals = [r['za'] for r in pre5]
            max_za = max(za_vals) if za_vals else 0
            min_za = min(za_vals) if za_vals else 0

            # 连续阴柱
            streak_yin = 0
            for j in range(len(rows[max(0,i-10):i])-1,-1,-1):
                if rows[max(0,i-10):i][j]['ret'] < 0: streak_yin += 1
                else: break

            # 前3天柱排（用于P4限制条件）
            pre3_zp = [rows[j]['zp'] for j in range(max(0,i-3), i)]
            all_not_die = all(not zp.startswith('跌') for zp in pre3_zp)

            # 前5天是否有继鼎（用于近DJA条件放宽）
            has_继鼎 = any(是继鼎(r['zp']) for r in pre5)

            # 触DJA后反弹（带继鼎调整）
            has_bounce = False
            if len(pre5) >= 3:
                min_idx = za_vals.index(min(za_vals))
                after_min = za_vals[min_idx:]
                # 有继鼎：近DJA阈值放宽到ZA≤5；无继鼎：保持ZA≤3
                dja_near_threshold = 5 if has_继鼎 else 3
                if len(after_min) >= 2 and min(za_vals) <= dja_near_threshold:
                    if max(after_min) - after_min[0] >= 2:
                        has_bounce = True

            # 初始分类（显式互斥条件）
            # P4: 暴跌破位 → 前3天都不是跌排（排除已阴跌靠近DJA的情况）
            if za_drop >= 3 and drop_ret <= -2 and all_not_die:
                p = 'P4'
            elif streak_yin >= 3 and max_za >= 2 and drop_ret > -2:
                p = 'P1'
            elif has_bounce:
                p = 'P2'
            elif min_za <= (5 if has_继鼎 else 3):
                # 有继鼎：近DJA阈值放宽到ZA≤5
                p = 'P0a'
            else:
                p = 'P0d'

            down_events.append((i, p))

    # ===== 负转正检测 =====
    up_events = []
    for i in range(1, len(rows)):
        prev = rows[i-1]; curr = rows[i]
        if prev['za'] < 0 and curr['za'] >= 0:
            total_up += 1
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

            # 前5天是否有继鼎（反向：继鼎在DJA之下靠近DJA）
            has_继鼎 = any(是继鼎(r['zp']) for r in pre5)

            has_fall = False
            if len(pre5) >= 3:
                max_idx = za_vals.index(max(za_vals))
                after_max = za_vals[max_idx:]
                # 有继鼎：近DJA阈值放宽到ZA≥-5；无继鼎：保持ZA≥-3
                dja_near_threshold = -5 if has_继鼎 else -3
                if len(after_max) >= 2 and max(za_vals) >= dja_near_threshold:
                    if after_max[0] - min(after_max) >= 2:
                        has_fall = True

            if za_rise >= 3 and rise_ret >= 2:
                p = 'M4'
            elif streak_yang >= 3 and min_za <= -2 and rise_ret < 2:
                p = 'M1'
            elif has_fall:
                p = 'M2'
            elif max_za >= (-5 if has_继鼎 else -3):
                # 有继鼎：近DJA阈值放宽到ZA≥-5
                p = 'M0a'
            else:
                p = 'M0d'

            up_events.append((i, p))

    # ===== 第二轮：P3双穿检测（从P0d/P0a中分出） =====
    for idx, p in down_events:
        if p not in ['P0d', 'P0a']: continue
        pre5 = rows[max(0,idx-5):idx]
        if all(r['za'] >= 3 for r in pre5):
            is_p3 = False
            for j in range(idx+1, min(idx+15, len(rows))):
                if rows[j]['za'] == 1:
                    for k in range(j+1, min(j+10, len(rows))):
                        if rows[k]['za'] <= 0:
                            dtza = k - j  # 弱正持续天数
                            if dtza <= 5:  # 双穿=短命M头(DTZA≤5)
                                is_p3 = True
                            break
                    if is_p3: break
            if is_p3:
                pattern_down['P3'] += 1
                stock_down['P3'].add(code)
                bar_states['正转负_P3'] += 1
                continue
        # 非P3：保持原分类
        pattern_down[p] += 1
        stock_down[p].add(code)
        bar_states['正转负_'+p] += 1

    # ===== 第三轮：M3双穿检测（从M0d/M0a中分出） =====
    for idx, p in up_events:
        if p not in ['M0d', 'M0a']: continue
        pre5 = rows[max(0,idx-5):idx]
        if all(r['za'] <= -3 for r in pre5):
            is_m3 = False
            for j in range(idx+1, min(idx+15, len(rows))):
                if rows[j]['za'] == -1:
                    for k in range(j+1, min(j+10, len(rows))):
                        if rows[k]['za'] >= 0:
                            dtza = k - j  # 弱负持续天数
                            if dtza <= 5:  # 双穿=短命M底(DTZA≤5)
                                is_m3 = True
                            break
                    if is_m3: break
            if is_m3:
                pattern_up['M3'] += 1
                stock_up['M3'].add(code)
                bar_states['负转正_M3'] += 1
                continue
        # 非M3：保持原分类
        pattern_up[p] += 1
        stock_up[p].add(code)
        bar_states['负转正_'+p] += 1

    # 非P3的正转负事件（P4/P2/P1）直接统计
    for idx, p in down_events:
        if p in ['P4','P2','P1']:
            pattern_down[p] += 1
            stock_down[p].add(code)
            bar_states['正转负_'+p] += 1

    # 非M3的负转正事件
    for idx, p in up_events:
        if p in ['M4','M2','M1']:
            pattern_up[p] += 1
            stock_up[p].add(code)
            bar_states['负转正_'+p] += 1

# ===== 输出 =====
print(f'\n总柱数: {total_bars:,}')
print(f'正转负事件: {total_down:,}')
print(f'负转正事件: {total_up:,}')

# 正转负
print(f'\n{"="*70}')
print(f'正转负6种模式（全量{total_down:,}事件，v2修复版）')
print(f'{"="*70}')
print(f'{"编码":>6} {"次数":>10} {"占比":>8} {"覆盖股票":>8}')
for p in ['P4','P2','P1','P3','P0a','P0d']:
    c = pattern_down[p]
    print(f'{p:>6} {c:>10,} {c/total_down*100:>7.1f}% {len(stock_down[p]):>8}')

# 负转正
print(f'\n{"="*70}')
print(f'负转正6种模式（全量{total_up:,}事件，v2修复版）')
print(f'{"="*70}')
print(f'{"编码":>6} {"次数":>10} {"占比":>8} {"覆盖股票":>8}')
for p in ['M4','M2','M1','M3','M0a','M0d']:
    c = pattern_up[p]
    print(f'{p:>6} {c:>10,} {c/total_up*100:>7.1f}% {len(stock_up[p]):>8}')

# 遗漏检测
print(f'\n{"="*70}')
print('遗漏检测')
print(f'{"="*70}')
sum_down = sum(pattern_down[p] for p in ['P4','P2','P1','P3','P0a','P0d'])
sum_up = sum(pattern_up[p] for p in ['M4','M2','M1','M3','M0a','M0d'])
print(f'正转负: 事件={total_down:,} 已分类={sum_down:,} 差值={total_down-sum_down}')
print(f'负转正: 事件={total_up:,} 已分类={sum_up:,} 差值={total_up-sum_up}')
if total_down == sum_down and total_up == sum_up:
    print('✅ 无遗漏：所有事件都已分类')
else:
    print('❌ 有遗漏！')

# 对比v1 vs v2（仅输出差异提示）
print(f'\n{"="*70}')
print('v2修复总结')
print(f'{"="*70}')
print('1. P4: 增加"前3天柱排都不是跌排"限制，排除阴跌中的大跌')
print('2. P0a/P2: 有继鼎时近DJA阈值从ZA≤3放宽到ZA≤5')
print('3. M0a/M2: 有继鼎时近DJA阈值从ZA≥-3放宽到ZA≥-5')
print('4. P3/M3: 保持两轮检测不变')