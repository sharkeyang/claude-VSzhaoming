# -*- coding: utf-8 -*-
"""升管(DXZA>0)下 管宽分类 全量验证（用户纠正口径 2026-09-20）
升管基本条件 = DXZA>0；触哼→入管→分窄/扩/平
窄管 = 0 < 管宽哼JA < 5
扩管 = 管宽哼JA>=5 且 推高顶(触顶+升排)
平管 = 管宽哼JA>=5 且 非推高顶
列映射(实际数据验证,勿信表头)：
col10=护型DXAB, col11=柱排, col14=日ZA, col22=管宽哼JA,
col27=次日高幅, col31=上符串(触顶A), col43=等型(BT连阳)
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
import random
LIMIT = int(os.environ.get('FILE_LIMIT', '0'))
if LIMIT:
    random.seed(1)
    files = random.sample(files, LIMIT)
print(f'共 {len(files)} 个文件', flush=True)

def zhupai_class(zp):
    if zp.startswith('升.'):
        if '尾连' in zp: return '升连'
        elif '尾吞' in zp: return '升吞'
        elif '尾反孕' in zp: return '升孕'
        else: return '升排其他'
    elif zp.startswith('跌.'):
        if '尾连' in zp: return '跌连'
        elif '尾吞' in zp: return '跌吞'
        elif '尾反孕' in zp: return '跌孕'
        else: return '跌排其他'
    elif zp.startswith('('):
        return '人排'
    else:
        return '其他'

stats = defaultdict(lambda: {'n':0,'p3':0,'sum_nh':0})
def add(label, nh):
    st = stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1
    st['sum_nh']+=nh
def report(label):
    st = stats[label]
    if st['n']==0: return
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%', flush=True)

def parse_row(row):
    if len(row) < 44: return None
    try:
        return {'ab': row[9], 'zp': row[10], 'za': float(row[13]), 'gk': row[21].strip(),
                'nh': float(row[26]), 'sf': row[30], 'deng': row[42].strip()}
    except:
        return None

def classify(gkv, touch, shengpai):
    """返回 窄/扩/平"""
    if 0 < gkv < 5:
        return '窄管'
    elif gkv >= 5:
        return '扩管' if (touch and shengpai) else '平管'
    else:
        return '管宽<=0'

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            r = parse_row(line.strip().split(','))
            if r is None: continue
            hx = r['ab'][0] if r['ab'] else ''
            nh = r['nh']
            touch = 'A' in r['sf']
            shengpai = r['zp'].startswith('升.')
            zpc = zhupai_class(r['zp'])
            # 等型映射
            try:
                dv = int(r['deng'])
            except:
                dv = None
            if dv is None: deng = '等其他'
            elif dv == 1: deng = '等1'
            elif dv == 2: deng = '等2'
            elif dv >= 3: deng = '等3'
            elif dv == -1: deng = '等5'
            elif dv == -2: deng = '等6'
            elif dv <= -3: deng = '等7'
            else: deng = '等其他'

            if r['za'] > 0 and hx in ('a','b','r'):  # 升管 = 甲乙己 + DXZA>0（用户确认：只有甲乙己才能定义升管）
                add('升管_基线', nh)
                if r['gk'] == '':
                    add('升管_管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    cls = classify(gkv, touch, shengpai)
                    add(f'升管_{cls}', nh)
                    add(f'升管_{cls}_{deng}', nh)
                    add(f'升管_{cls}_{zpc}', nh)
            elif r['za'] < 0 and hx in ('c','z','y'):  # 跌管 = 丙丁戊 + DXZA<0 对照
                add('跌管_基线', nh)
                if r['gk'] != '':
                    gkv = float(r['gk'])
                    cls = classify(gkv, touch, shengpai)
                    add(f'跌管_{cls}', nh)

print('\n=== 升管(DXZA>0) 管宽分类 全量 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('升管_') and '_等' not in label and '_升' not in label and '_跌' not in label and '_人' not in label:
        report(label)

print('\n=== 升管 管宽分类 × 等型 ===', flush=True)
for label in sorted(stats.keys()):
    if '_等' in label:
        report(label)

print('\n=== 升管 管宽分类 × 柱排 ===', flush=True)
for label in sorted(stats.keys()):
    if ('_升' in label or '_跌' in label or '_人' in label) and '_等' not in label:
        report(label)

print('\n=== 跌管(DXZA<0) 管宽分类 对照 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('跌管_'):
        report(label)