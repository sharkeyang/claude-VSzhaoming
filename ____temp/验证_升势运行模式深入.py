# -*- coding: utf-8 -*-
"""
升势运行模式深入分析 v2（C6 6.6.4.5 展开）
========================================
模式A：单向连续触顶（合顶≥3）——连续触顶推高顶部
模式B：阶梯上升（前日触DJA→今日触顶）——触顶推高+触下沿平移交替

分析维度：
1. 次日冲高率 + 未来3/5/10天累计收益（持续性）
2. 未来N天仍触顶率（升势延续性）
3. 触发条件：进入模式前的状态（护型/管宽/BSHA/柱排）
4. 结束信号：什么信号预示升势结束

列序（旧列序）：[1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [9]DXAB [10]柱排 [13]日ZA [19]BSHA [23]脸哼JA [26]次日高幅 [30]上符串
"""
import csv, os, sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}
HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

def to_f(v):
    try: return float(v)
    except: return None
def is_touch(sfs):
    s = sfs.strip()
    return bool(s) and s[-1]=='A'
def is_sheng(zp): return '升' in zp
def is_die(zp): return '跌' in zp

stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr
touch_stats = defaultdict(lambda: [0,0])
def add_touch(key, is_t):
    touch_stats[key][0]+=1; touch_stats[key][1]+=(1 if is_t else 0)

def report(title, keys):
    print(f'\n{"="*84}')
    print(title)
    print('='*84)
    print(f'{"条件":<52} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*80)
    for k in keys:
        if k in stats:
            s = stats[k]
            print(f'{k:<52} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
        elif k in touch_stats:
            s = touch_stats[k]
            print(f'{k:<52} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')

files_core = 0
for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 30: continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                zpa = to_f(row[13]); bsha = to_f(row[19]); lian = to_f(row[23])
                if zpa is None: continue
                sfs = row[30].strip(); zp = row[10].strip()
                dxab = row[9].strip()
                hx = HX_MAP.get(dxab[0]) if dxab else None
                touch = is_touch(sfs)
                hetop = 0
                if touch:
                    for ch in reversed(sfs):
                        if ch=='A': hetop+=1
                        else: break
                prev = rows[i-1] if i>0 else None
                prev_za = to_f(prev[13]) if prev else None
                prev_sfs = prev[30].strip() if prev else ''
                prev_touch = is_touch(prev_sfs) if prev else False
                prev_zp = prev[10].strip() if prev else ''

                # 模式A：单向连续触顶（合顶≥3）
                modeA = touch and hetop>=3
                # 模式B：阶梯上升（前日触DJA→今日触顶）
                modeB = touch and prev_za is not None and 0 < prev_za <= 2

                def future_ret(n):
                    if i+n < len(rows):
                        c0 = to_f(row[1]); cn = to_f(rows[i+n][1])
                        if c0 and cn and c0>0: return (cn/c0-1)*100
                    return None
                def future_touch(n):
                    if i+n < len(rows):
                        return is_touch(rows[i+n][30].strip())
                    return None

                if modeA:
                    add('A 次日冲高', hr)
                    for n in [3,5,10]:
                        fr = future_ret(n)
                        if fr is not None: add(f'A 未来{n}天累计收益', fr)
                    for n in [1,3,5]:
                        ft = future_touch(n)
                        if ft is not None: add_touch(f'A 未来{n}天仍触顶', ft)
                    # 触发条件：护型
                    if hx: add(f'A 触发-护型{hx}', hr)
                    # 管宽
                    if lian is not None:
                        if lian>=5: add('A 触发-管宽≥5', hr)
                        else: add('A 触发-管宽<5', hr)
                    # BSHA
                    if bsha is not None:
                        if bsha>=5: add('A 触发-BSHA≥5', hr)
                        else: add('A 触发-BSHA<5', hr)
                if modeB:
                    add('B 次日冲高', hr)
                    for n in [3,5,10]:
                        fr = future_ret(n)
                        if fr is not None: add(f'B 未来{n}天累计收益', fr)
                    for n in [1,3,5]:
                        ft = future_touch(n)
                        if ft is not None: add_touch(f'B 未来{n}天仍触顶', ft)
                    # 触发条件：护型
                    if hx: add(f'B 触发-护型{hx}', hr)
                    # 管宽
                    if lian is not None:
                        if lian>=5: add('B 触发-管宽≥5', hr)
                        else: add('B 触发-管宽<5', hr)
                    # BSHA
                    if bsha is not None:
                        if bsha>=5: add('B 触发-BSHA≥5', hr)
                        else: add('B 触发-BSHA<5', hr)
                    # 前日状态
                    if prev_touch: add('B 触发-前日已触顶', hr)
                    else: add('B 触发-前日未触顶', hr)
                    if is_sheng(prev_zp): add('B 触发-前日升排', hr)
                    elif is_die(prev_zp): add('B 触发-前日跌排', hr)
                    else: add('B 触发-前日非升非跌', hr)

                # 结束信号
                if modeA or modeB:
                    tag = 'A' if modeA else 'B'
                    nxt = rows[i+1] if i+1 < len(rows) else None
                    if nxt:
                        nza = to_f(nxt[13]); nzp = nxt[10].strip()
                        if nza is not None and nza <= 0:
                            add(f'{tag} 结束-次日跌破DJA', hr)
                        if is_die(nzp):
                            add(f'{tag} 结束-次日跌排', hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')

report('模式A 单向连续触顶（合顶≥3）', [
    'A 次日冲高','A 未来3天累计收益','A 未来5天累计收益','A 未来10天累计收益',
    'A 未来1天仍触顶','A 未来3天仍触顶','A 未来5天仍触顶',
    'A 触发-护型甲','A 触发-护型乙','A 触发-护型丙','A 触发-护型丁','A 触发-护型戊','A 触发-护型己',
    'A 触发-管宽≥5','A 触发-管宽<5','A 触发-BSHA≥5','A 触发-BSHA<5',
    'A 结束-次日跌破DJA','A 结束-次日跌排',
])
report('模式B 阶梯上升（前日触DJA→今日触顶）', [
    'B 次日冲高','B 未来3天累计收益','B 未来5天累计收益','B 未来10天累计收益',
    'B 未来1天仍触顶','B 未来3天仍触顶','B 未来5天仍触顶',
    'B 触发-护型甲','B 触发-护型乙','B 触发-护型丙','B 触发-护型丁','B 触发-护型戊','B 触发-护型己',
    'B 触发-管宽≥5','B 触发-管宽<5','B 触发-BSHA≥5','B 触发-BSHA<5',
    'B 触发-前日已触顶','B 触发-前日未触顶','B 触发-前日升排','B 触发-前日跌排','B 触发-前日非升非跌',
    'B 结束-次日跌破DJA','B 结束-次日跌排',
])
