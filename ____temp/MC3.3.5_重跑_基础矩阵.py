# -*- coding: utf-8 -*-
"""
MC3.3.5 重跑 - 基础矩阵 + 各护型介入点
========================================
对高波池(Qic+Qim+Qit)和低波池(Qd+Qe+Qif)分别计算：
  1.2 基础矩阵：护型×日等型 P(≥3%)（DXZC>0）
  2.1 各护型介入点（转移概率）
  3.3.1 各护型 个数/机会段/比例

【关键】谕组日CSV数据列序与表头错位，必须用真实列位置（VBA代码打印顺序）：
  [8] DXCD, [9] DXAB护型, [10] 柱排, [13] 日ZA, [14] 日ZC, [15] 日ZE
  [21] BSHA, [24] 宽哼JC管宽, [26] 上身=次日高幅, [27] 柱型(位谕of日层柱型)
  [30] 上符串(触顶/哼/哈/底), [43] 顶型(基顶型a龙), [44] 日等型(等1/2/3)
  [45] 顶型(触顶:无/上b), [55] 日龟顶触
"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100

# 真实列位置
C_DXCD = 8
C_DXAB = 9
C_柱排 = 10
C_日ZA = 13
C_日ZC = 14
C_日ZE = 15
C_BSHA = 21
C_管宽 = 24
C_次日高幅 = 26
C_柱型 = 27
C_上符串 = 30
C_顶型基 = 43
C_日等型 = 44
C_顶型触 = 45
C_日龟顶触 = 55

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_hx(dxab_str):
    """DXAB第1字符：a=甲, b=乙, c=丙, z=丁, y=戊, r=己"""
    if not dxab_str: return ''
    c = dxab_str[0]
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(c, '')

def to_f(v):
    try: return float(v)
    except: return None

def classify_zp(zp):
    """柱排分类"""
    s = str(zp).strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

def run_pool(pool_name, 目标板块):
    """对指定池计算所有指标"""
    # 聚合: (护型, 等型) -> [n, hr3, sum_hr]
    agg = defaultdict(lambda: [0,0,0.0])
    agg_hx = defaultdict(lambda: [0,0,0.0])
    agg_等 = defaultdict(lambda: [0,0,0.0])
    # 转移概率: (护型, 次日护型) -> [n]
    trans = defaultdict(lambda: [0,0,0.0])
    # 机会段: 护型 -> [行数, 段数]
    runs = defaultdict(lambda: [0,0])
    # 护型基线(全样本)
    agg_hx_all = defaultdict(lambda: [0,0,0.0])
    # 护型次日转移(全样本)
    trans_all = defaultdict(lambda: [0,0,0.0])

    nfiles = 0
    for i, f in enumerate(files):
        code = os.path.basename(f).replace('谕组日_','').replace('.csv','')
        board = board_map.get(code, '')
        if board not in 目标板块: continue
        nfiles += 1
        try:
            df = pd.read_csv(f, encoding='gbk', header=None, skiprows=1)
        except Exception:
            continue
        if len(df) < 5: continue
        # 提取列
        dxab = df[C_DXAB].astype(str).values
        deng = df[C_日等型].astype(str).values
        hr = pd.to_numeric(df[C_次日高幅], errors='coerce').values
        zc = pd.to_numeric(df[C_日ZC], errors='coerce').values
        za = pd.to_numeric(df[C_日ZA], errors='coerce').values
        # 护型
        hxs = [parse_hx(s) for s in dxab]
        # 次日护型(下一行)
        nxt_hx = hxs[1:] + ['']
        # 机会段: 连续同护型且同DXZC>0
        prev_key = None
        for j in range(len(df)):
            hx = hxs[j]
            if not hx: continue
            # 全样本护型基线
            h = hr[j]
            if not np.isnan(h) and -50 <= h <= 50:
                agg_hx_all[hx][0]+=1; agg_hx_all[hx][1]+= (1 if h>=3 else 0); agg_hx_all[hx][2]+=h
                if nxt_hx[j]:
                    trans_all[(hx, nxt_hx[j])][0]+=1
            # DXZC>0 限定
            if np.isnan(zc[j]) or zc[j] <= 0: continue
            if np.isnan(h) or h < -50 or h > 50: continue
            deng_j = deng[j]
            if deng_j not in ('等1','等2','等3','等5','等6','等7'): continue
            agg[(hx, deng_j)][0]+=1; agg[(hx, deng_j)][1]+= (1 if h>=3 else 0); agg[(hx, deng_j)][2]+=h
            agg_hx[hx][0]+=1; agg_hx[hx][1]+= (1 if h>=3 else 0); agg_hx[hx][2]+=h
            agg_等[deng_j][0]+=1; agg_等[deng_j][1]+= (1 if h>=3 else 0); agg_等[deng_j][2]+=h
            # 转移(DXZC>0)
            if nxt_hx[j]:
                trans[(hx, nxt_hx[j])][0]+=1
            # 机会段
            key = (hx, 'ZC>0')
            if key != prev_key:
                runs[hx][1] += 1
                prev_key = key
            runs[hx][0] += 1

    print()
    print('='*90)
    print(f'【{pool_name}】文件数: {nfiles}')
    print('='*90)

    # ===== 1.2 基础矩阵 =====
    print()
    print('【1.2 基础矩阵】护型×日等型 P(≥3%)（DXZC>0）')
    print(f'{"护型":<6} {"等1":>14} {"等2":>14} {"等3":>14} {"等5":>14} {"等6":>14} {"等7":>14} {"基线":>14}')
    for hx in ['甲','乙','己','戊','丙','丁']:
        row = []
        for deng in ['等1','等2','等3','等5','等6','等7']:
            s = agg[(hx, deng)]
            if s[0] >= MIN_SAMPLE:
                row.append(f'{s[1]/s[0]*100:.1f}%({s[0]:,})')
            else:
                row.append('-')
        s = agg_hx[hx]
        row.append(f'{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else '-')
        print(f'{hx:<6} ' + ' '.join(f'{x:>14}' for x in row))

    # ===== 各护型基线(全样本) =====
    print()
    print('【各护型基线(全样本)】')
    for hx in ['甲','乙','己','戊','丙','丁']:
        s = agg_hx_all[hx]
        if s[0] >= MIN_SAMPLE:
            print(f'  {hx}: P(≥3%)={s[1]/s[0]*100:.1f}%  均高幅={s[2]/s[0]:.2f}%  n={s[0]:,}')

    # ===== 3.3.1 各护型 个数/机会段/比例 =====
    print()
    print('【3.3.1 各护型 个数/机会段/比例】(DXZC>0)')
    print(f'{"护型":<8} {"个数(行)":>12} {"机会段":>12} {"平均持续":>10} {"行占比":>8} {"段占比":>8}')
    total_rows = sum(v[0] for v in runs.values())
    total_runs = sum(v[1] for v in runs.values())
    for hx in ['甲','乙','己','戊','丙','丁']:
        r = runs[hx]
        if r[0] == 0: continue
        avg = r[0]/r[1] if r[1] else 0
        print(f'{hx:<8} {r[0]:>12,} {r[1]:>12,} {avg:>9.1f}天 {r[0]/total_rows*100:>7.2f}% {r[1]/total_runs*100:>7.2f}%')

    # ===== 2.1 各护型转移概率 =====
    print()
    print('【2.1 各护型转移概率】(DXZC>0)')
    for hx in ['甲','乙','己','戊','丙','丁']:
        total = sum(v[0] for k,v in trans.items() if k[0]==hx)
        if total < MIN_SAMPLE: continue
        # 按次日护型聚合
        nxt = defaultdict(int)
        for (h0, h1), v in trans.items():
            if h0 == hx: nxt[h1] += v[0]
        top = sorted(nxt.items(), key=lambda x:-x[1])[:5]
        s = ', '.join(f'→{k} {v/total*100:.1f}%' for k,v in top)
        print(f'  {hx}: {s}')

    return agg, agg_hx, agg_等, trans, runs

# 运行两个池
高波池 = {'Qic', 'Qim', 'Qit'}
低波池 = {'Qd', 'Qe', 'Qif'}

print('########## 高波池 ##########')
run_pool('高波池', 高波池)
print()
print('########## 低波池 ##########')
run_pool('低波池', 低波池)
