# -*- coding: utf-8 -*-
"""
DXZC>25 未触顶→再次触顶入管的调整模式 综合细分
====================================================
细分维度：
1. 调整模式 × 再次触顶后P3（次日高幅≥3%）
2. 调整模式 × 护型（甲/乙/己/戊/丙/丁）
3. 调整期长度分布（下破DJB后几柱再触顶）
4. 调整模式 × 调整期柱排（跌孕/跌吞/跌连/阴阳阴/升排）
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def to_f(v):
    try: return float(v)
    except: return None

def ema12(prices):
    if not prices: return []
    k = 2/13
    ema = [prices[0]]
    for p in prices[1:]:
        ema.append(p*k + ema[-1]*(1-k))
    return ema

def classify_adj(rows, emas, i, retouch_idx):
    """分类调整模式，返回 (mode, adj_len, adj_zp_list)"""
    adj_len = retouch_idx - i - 1
    if adj_len == 0:
        return '0柱(次日直接触顶)', 0, []
    broke_dja = False
    broke_djb = False
    adj_zp = []
    for j in range(i+1, retouch_idx):
        za = to_f(rows[j][13]) if len(rows[j])>13 else None
        close = to_f(rows[j][1]) if len(rows[j])>1 else None
        zp = rows[j][10].strip() if len(rows[j])>10 else ''
        adj_zp.append(zp)
        if za is not None and za < 0: broke_dja = True
        if close is not None and emas[j] is not None and close < emas[j]: broke_djb = True
    if broke_djb:
        mode = '下破DJB调整'
    elif broke_dja:
        mode = '下破DJA调整'
    elif adj_len == 1:
        mode = 'DJA之上单柱调整'
    else:
        mode = 'DJA之上多柱调整'
    return mode, adj_len, adj_zp

def zp_class(zp):
    """柱排分类"""
    if not zp: return '空'
    if '跌孕' in zp: return '跌孕'
    if '跌吞' in zp: return '跌吞'
    if '跌连' in zp: return '跌连'
    if '阴阳阴' in zp or '人' in zp: return '阴阳阴'
    if zp.startswith('升') or zp.startswith('(升)'): return '升排'
    return '其他'

# 统计容器
# 1. 模式 -> [n, p3_cnt]
mode_p3 = defaultdict(lambda: [0,0])
# 2. 模式 -> 护型计数
mode_hx = defaultdict(lambda: defaultdict(int))
# 3. 模式 -> 调整期长度分布
mode_len = defaultdict(lambda: defaultdict(int))
# 4. 模式 -> 调整期柱排分布
mode_zp = defaultdict(lambda: defaultdict(int))
# 5. 模式 -> 再次触顶后是否延续（触顶后次日仍触顶）
mode_cont = defaultdict(lambda: [0,0])

LOOKAHEAD = 10
files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    prices = []
    for row in rows:
        p = to_f(row[1]) if len(row)>1 else None
        prices.append(p if p is not None else 0)
    emas = ema12(prices)

    for i in range(n):
        row = rows[i]
        if len(row) < 31: continue
        zc = to_f(row[14])
        if zc is None or zc <= 25: continue
        sf = row[30].strip()
        if not sf or sf[-1] == 'A': continue
        # 找未来LOOKAHEAD天内再次触顶
        retouch_idx = None
        for j in range(i+1, min(i+1+LOOKAHEAD, n)):
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A':
                retouch_idx = j
                break
        if retouch_idx is None: continue

        mode, adj_len, adj_zp = classify_adj(rows, emas, i, retouch_idx)
        # 护型
        dxab = row[9].strip() if len(row)>9 else ''
        hx = parse_hx(dxab)
        # 再次触顶后P3（次日高幅）
        nxt = to_f(rows[retouch_idx][26]) if len(rows[retouch_idx])>26 else None
        mode_p3[mode][0] += 1
        if nxt is not None and nxt >= 3: mode_p3[mode][1] += 1
        # 护型
        if hx: mode_hx[mode][hx] += 1
        # 调整期长度
        mode_len[mode][adj_len] += 1
        # 调整期柱排（取调整期最后一柱）
        if adj_zp:
            mode_zp[mode][zp_class(adj_zp[-1])] += 1
        # 再次触顶后是否延续（触顶日次日仍触顶）
        if retouch_idx+1 < n:
            sf_next = rows[retouch_idx+1][30].strip() if len(rows[retouch_idx+1])>30 else ''
            mode_cont[mode][0] += 1
            if sf_next and sf_next[-1] == 'A': mode_cont[mode][1] += 1

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【1】调整模式 × 再次触顶后P3（次日高幅≥3%）')
print('='*70)
print(f'{"模式":<20}{"n":>10}{"P3":>8}')
for mode, (n, p3) in sorted(mode_p3.items(), key=lambda x: -x[1][0]):
    print(f'{mode:<20}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【2】调整模式 × 护型')
print('='*70)
print(f'{"模式":<20}{"甲":>8}{"乙":>8}{"己":>8}{"戊":>8}{"丙":>8}{"丁":>8}')
for mode, hxc in sorted(mode_hx.items(), key=lambda x: -sum(x[1].values())):
    total = sum(hxc.values())
    if total == 0: continue
    print(f'{mode:<20}{hxc.get("甲",0)/total*100:>7.1f}%{hxc.get("乙",0)/total*100:>7.1f}%{hxc.get("己",0)/total*100:>7.1f}%{hxc.get("戊",0)/total*100:>7.1f}%{hxc.get("丙",0)/total*100:>7.1f}%{hxc.get("丁",0)/total*100:>7.1f}%')

print()
print('='*70)
print('【3】调整模式 × 调整期长度')
print('='*70)
print(f'{"模式":<20}{"0柱":>6}{"1柱":>6}{"2柱":>6}{"3柱":>6}{"4柱":>6}{"5柱+":>6}')
for mode, lenc in sorted(mode_len.items(), key=lambda x: -sum(x[1].values())):
    total = sum(lenc.values())
    if total == 0: continue
    print(f'{mode:<20}{lenc.get(0,0):>6,}{lenc.get(1,0):>6,}{lenc.get(2,0):>6,}{lenc.get(3,0):>6,}{lenc.get(4,0):>6,}{sum(v for k,v in lenc.items() if k>=5):>6,}')

print()
print('='*70)
print('【4】调整模式 × 调整期最后一柱柱排')
print('='*70)
print(f'{"模式":<20}{"跌孕":>8}{"跌吞":>8}{"跌连":>8}{"阴阳阴":>8}{"升排":>8}{"其他":>8}')
for mode, zpc in sorted(mode_zp.items(), key=lambda x: -sum(x[1].values())):
    total = sum(zpc.values())
    if total == 0: continue
    print(f'{mode:<20}{zpc.get("跌孕",0)/total*100:>7.1f}%{zpc.get("跌吞",0)/total*100:>7.1f}%{zpc.get("跌连",0)/total*100:>7.1f}%{zpc.get("阴阳阴",0)/total*100:>7.1f}%{zpc.get("升排",0)/total*100:>7.1f}%{zpc.get("其他",0)/total*100:>7.1f}%')

print()
print('='*70)
print('【5】调整模式 × 再次触顶后延续（触顶日次日仍触顶）')
print('='*70)
print(f'{"模式":<20}{"n":>10}{"延续率":>8}')
for mode, (n, cont) in sorted(mode_cont.items(), key=lambda x: -x[1][0]):
    if n == 0: continue
    print(f'{mode:<20}{n:>10,}{cont/n*100:>7.1f}%')
