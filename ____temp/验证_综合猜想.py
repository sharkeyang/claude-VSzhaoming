# -*- coding: utf-8 -*-
"""
综合验证用户猜想（DXZC>0口径）：
1. 戊(ZA>0)转戊细分（转戊(ZA>0) vs 转戊(ZA<0)）
2. 甲/乙的层界细分（初/再B/再C/主）样本量和次日冲高率
3. 5.7.1/5.7.2条件最强预测（柱排/地型/盈提示/等型/顶型对甲/乙转坏）
4. 第六章微观指标（管宽/BSHA/等高线）对甲/乙/己/戊(ZA>0)转坏的预测

磁盘CSV列序：9=DXAB, 10=柱排, 11=波型, 12=盈提示, 13=日ZA, 14=日ZC, 21=BSHA, 24=宽哼JC, 26=次日高幅, 28=日层界, 46=日等型, 45=顶型
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return 护型映射.get(dxab[0],'')

def parse_lj(lj):
    if not lj: return ''
    if lj.startswith('储'): return '储'
    if lj.startswith('破'): return '破'
    if lj.startswith('主'): return '主'
    if lj.startswith('初'): return '初'
    if lj.startswith('再'):
        return '再'+lj[2] if len(lj)>=3 else '再'
    if lj.startswith('_主'): return '_主'
    if lj.startswith('_初'): return '_初'
    if lj.startswith('_再'):
        return '_再'+lj[3] if len(lj)>=4 else '_再'
    return lj[:2]

# 1. 戊(ZA>0)转戊细分: (当前戊ZA>0) -> {次日戊ZA符号: n}
wu_trans = defaultdict(int)
# 2. 层界细分: (护型, 层类) -> [n, hr3]
lj_stats = defaultdict(lambda: [0,0])
# 3. 甲/乙转坏率按微观指标: (护型, 指标, 值) -> [n, 转坏n]
zhuanhuai = defaultdict(lambda: [0,0])
# 4. 第六章指标对转坏: (护型, 指标, 值) -> [n, 转坏n]
ch6 = defaultdict(lambda: [0,0])

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
            for i,row in enumerate(rows):
                if len(row) <= 46: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                hr = to_f(row[26])
                lj = row[28].strip()
                if za is None or zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                if zc <= 0: continue
                hx = parse_hx(dxab)
                if not hx: continue
                # 次日护型和ZA
                nxt_hx = ''
                nxt_za = None
                if i+1 < len(rows):
                    nrow = rows[i+1]
                    if len(nrow) > 13:
                        nxt_hx = parse_hx(nrow[9].strip())
                        nxt_za = to_f(nrow[13])
                # 1. 戊(ZA>0)转戊细分
                if hx=='戊' and za>0 and nxt_hx=='戊':
                    if nxt_za is not None:
                        wu_trans['戊(ZA>0)' if nxt_za>0 else '戊(ZA<0)'] += 1
                # 2. 层界细分
                lj_key = parse_lj(lj)
                if lj_key:
                    lj_stats[(hx, lj_key)][0]+=1
                    lj_stats[(hx, lj_key)][1]+= (1 if hr>=3 else 0)
                # 3. 甲/乙转坏率（转坏=次日非甲/非乙(ZA>0)）
                if hx in ('甲','乙') and za>0:
                    zhuanhuai_flag = 0
                    if hx=='甲':
                        zhuanhuai_flag = 1 if nxt_hx!='甲' else 0
                    elif hx=='乙':
                        zhuanhuai_flag = 1 if not (nxt_hx=='乙' and nxt_za is not None and nxt_za>0) else 0
                    # 柱排
                    zpaip = row[10].strip()
                    if '跌' in zpaip: zp='跌排'
                    elif '升' in zpaip: zp='升排'
                    else: zp='非升非跌'
                    zhuanhuai[(hx,'柱排',zp)][0]+=1; zhuanhuai[(hx,'柱排',zp)][1]+=zhuanhuai_flag
                    # 盈提示
                    ying = row[12].strip()
                    if '偏' in ying or '宽' in ying: yk='偏/宽'
                    elif ying=='a' or ying=='雀': yk='a系/雀'
                    else: yk='其他'
                    zhuanhuai[(hx,'盈提示',yk)][0]+=1; zhuanhuai[(hx,'盈提示',yk)][1]+=zhuanhuai_flag
                    # 日等型
                    deng = row[46].strip()
                    try: dv = int(deng)
                    except: dv = -1
                    if dv>=8: dk='高等等型(≥8)'
                    else: dk='低等等型(<8)'
                    zhuanhuai[(hx,'日等型',dk)][0]+=1; zhuanhuai[(hx,'日等型',dk)][1]+=zhuanhuai_flag
                    # 顶型
                    ding = row[45].strip()
                    if '上b' in ding: dk2='上b'
                    else: dk2='其他'
                    zhuanhuai[(hx,'顶型',dk2)][0]+=1; zhuanhuai[(hx,'顶型',dk2)][1]+=zhuanhuai_flag
                    # 4. 第六章指标
                    bsha = to_f(row[21])
                    kw = to_f(row[24])
                    if bsha is not None:
                        if bsha>=8: bk='BSHA≥8'
                        elif bsha>=3: bk='BSHA3-8'
                        else: bk='BSHA<3'
                        ch6[(hx,'BSHA',bk)][0]+=1; ch6[(hx,'BSHA',bk)][1]+=zhuanhuai_flag
                    if kw is not None:
                        if kw>=10: kk='管宽≥10'
                        else: kk='管宽<10'
                        ch6[(hx,'管宽',kk)][0]+=1; ch6[(hx,'管宽',kk)][1]+=zhuanhuai_flag
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('='*70)
print('1. 戊(ZA>0)转戊细分（DXZC>0）')
print('='*70)
total_wu = sum(wu_trans.values())
for k,v in wu_trans.items():
    print(f'  戊(ZA>0)→{k}: {v:,} ({v/total_wu*100:.1f}%)')

print()
print('='*70)
print('2. 甲/乙层界细分（DXZC>0，次日冲高率）')
print('='*70)
for hx in ['甲','乙']:
    print(f'--- {hx} ---')
    for lj_key in ['初','再B','再C','再D','主','储','破']:
        key = (hx, lj_key)
        if key in lj_stats:
            s = lj_stats[key]
            if s[0] >= 100:
                print(f'  {lj_key}: n={s[0]:,} P(≥3%)={s[1]/s[0]*100:.2f}%')

print()
print('='*70)
print('3. 甲/乙转坏率按微观指标（DXZC>0）')
print('='*70)
for hx in ['甲','乙']:
    print(f'--- {hx} ---')
    for ind in ['柱排','盈提示','日等型','顶型']:
        for val in sorted(set(k[2] for k in zhuanhuai if k[0]==hx and k[1]==ind)):
            key = (hx,ind,val)
            if key in zhuanhuai:
                s = zhuanhuai[key]
                if s[0] >= 500:
                    print(f'  {ind}={val}: n={s[0]:,} 转坏率={s[1]/s[0]*100:.2f}%')

print()
print('='*70)
print('4. 第六章指标对甲/乙转坏预测（DXZC>0）')
print('='*70)
for hx in ['甲','乙']:
    print(f'--- {hx} ---')
    for ind in ['BSHA','管宽']:
        for val in sorted(set(k[2] for k in ch6 if k[0]==hx and k[1]==ind)):
            key = (hx,ind,val)
            if key in ch6:
                s = ch6[key]
                if s[0] >= 500:
                    print(f'  {ind}={val}: n={s[0]:,} 转坏率={s[1]/s[0]*100:.2f}%')
