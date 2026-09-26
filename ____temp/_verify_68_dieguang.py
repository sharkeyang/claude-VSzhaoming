# -*- coding: utf-8 -*-
"""跌管（丙丁戊）管宽哼JA 分布验证 + 镜面映射
验证：
1. 丙丁戊 的管宽哼JA 值分布（扩管>60/平管0-60/窄管<0 的占比）
2. 丙丁戊 各管宽分类的次日P3%（看跌管各分类胜率）
3. 丙丁戊 各等型（等5/6/7）的次日P3%
4. 升管（甲乙己）vs 跌管（丙丁戊）的管宽哼JA 分布对比
列映射：col9=DXAB(护型首字符a甲/b乙/r己/y戊/c丙/d丁), col13=日ZA, col23=管宽哼JA, col26=次日高幅
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

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
    if len(row) < 31: return None
    try:
        return {'ab': row[9], 'za': int(row[13]), 'gk': row[23].strip(), 'nh': float(row[26])}
    except:
        return None

# 管宽哼JA 值分布统计
gk_dist = defaultdict(lambda: defaultdict(int))  # 护型 -> 管宽哼JA值区间
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            r = parse_row(line.strip().split(','))
            if r is None: continue
            hx = r['ab'][0] if r['ab'] else ''
            nh = r['nh']
            # 跌管 = 丙丁戊
            if hx in ('c','d','y'):
                add(f'跌管_丙丁戊_基线', nh)
                # 等型
                if r['za'] <= -3: add('跌管_等7(ZA<=-3)', nh)
                elif r['za'] == -2: add('跌管_等6(ZA=-2)', nh)
                elif r['za'] == -1: add('跌管_等5(ZA=-1)', nh)
                elif r['za'] == 1: add('跌管_等1(ZA=1)', nh)
                elif r['za'] == 2: add('跌管_等2(ZA=2)', nh)
                elif r['za'] >= 3: add('跌管_等3(ZA>=3)', nh)
                # 管宽哼JA 分类
                if r['gk'] == '':
                    add(f'跌管_{hx}_管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    if gkv > 60: add(f'跌管_{hx}_扩管>60', nh)
                    elif gkv >= 0: add(f'跌管_{hx}_平管0-60', nh)
                    else: add(f'跌管_{hx}_窄管<0', nh)
                # 管宽哼JA 值分布（分护型）
                if r['gk'] != '':
                    gkv = float(r['gk'])
                    if gkv > 60: gk_dist[hx]['>60'] += 1
                    elif gkv >= 30: gk_dist[hx]['30-60'] += 1
                    elif gkv >= 0: gk_dist[hx]['0-30'] += 1
                    elif gkv >= -30: gk_dist[hx]['-30-0'] += 1
                    else: gk_dist[hx]['<-30'] += 1
            # 升管 = 甲乙己（对比）
            if hx in ('a','b','r'):
                if r['gk'] != '':
                    gkv = float(r['gk'])
                    if gkv > 60: gk_dist['甲乙己']['>60'] += 1
                    elif gkv >= 30: gk_dist['甲乙己']['30-60'] += 1
                    elif gkv >= 0: gk_dist['甲乙己']['0-30'] += 1
                    elif gkv >= -30: gk_dist['甲乙己']['-30-0'] += 1
                    else: gk_dist['甲乙己']['<-30'] += 1

print('\n=== 跌管（丙丁戊）各等型次日P3% ===', flush=True)
for label in ['跌管_丙丁戊_基线','跌管_等7(ZA<=-3)','跌管_等6(ZA=-2)','跌管_等5(ZA=-1)','跌管_等1(ZA=1)','跌管_等2(ZA=2)','跌管_等3(ZA>=3)']:
    report(label)

print('\n=== 跌管（丙丁戊）各护型管宽哼JA分类次日P3% ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('跌管_c') or label.startswith('跌管_d') or label.startswith('跌管_y'):
        report(label)

print('\n=== 管宽哼JA 值分布（升管甲乙己 vs 跌管丙丁戊）===', flush=True)
for hx in ['甲乙己','c','d','y']:
    total = sum(gk_dist[hx].values())
    if total == 0: continue
    print(f'{hx} (n={total}):', flush=True)
    for k in ['>60','30-60','0-30','-30-0','<-30']:
        v = gk_dist[hx][k]
        print(f'  {k}: {v} ({v/total*100:.1f}%)', flush=True)
