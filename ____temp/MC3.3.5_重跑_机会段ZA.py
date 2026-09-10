# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 3.3.1 机会段（护型按ZA拆分，连续同护型且同DXZC>0）"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
C_DXAB=9; C_日ZC=14
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx_za(s, za):
    """护型+ZA: 首字符护型 + 日ZA[13]符号"""
    if not s: return ''
    hx = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
    if not hx: return ''
    if za is not None and za > 0: return f'{hx}(ZA>0)'
    return f'{hx}(ZA<0)'
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    runs=defaultdict(lambda:[0,0])  # 护型 -> [行数, 机会段]
    nfiles=0
    for f in files:
        code=os.path.basename(f).replace('谕组日_','').replace('.csv','')
        if board_map.get(code,'') not in 目标板块: continue
        nfiles+=1
        try: df=pd.read_csv(f,encoding='gbk',header=None,skiprows=1)
        except: continue
        if len(df)<5: continue
        dxab=df[C_DXAB].astype(str).values
        zc=pd.to_numeric(df[C_日ZC],errors='coerce').values
        za=pd.to_numeric(df[13],errors='coerce').values
        hxs=[parse_hx_za(s, za[j]) for j,s in enumerate(dxab)]
        n=len(df)
        prev_key=None
        for j in range(n):
            hx=hxs[j]
            if not hx: continue
            if np.isnan(zc[j]) or zc[j]<=0: continue
            key=(hx,'ZC>0')
            if key!=prev_key:
                runs[hx][1]+=1
                prev_key=key
            runs[hx][0]+=1
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    print('\n【3.3.1 DXZC>0 全护型总表（护型按ZA拆分）】')
    print(f'{"护型":<12} {"个数(行)":>12} {"机会段":>10} {"平均持续":>8} {"行占比":>8} {"段占比":>8}')
    total_rows=sum(v[0] for v in runs.values())
    total_runs=sum(v[1] for v in runs.values())
    for hx in ['甲(ZA>0)','乙(ZA>0)','乙(ZA<0)','丙(ZA<0)','丁(ZA<0)','戊(ZA>0)','戊(ZA<0)','己(ZA>0)']:
        r=runs[hx]
        if r[0]==0: continue
        avg=r[0]/r[1] if r[1] else 0
        print(f'{hx:<12} {r[0]:>12,} {r[1]:>10,} {avg:>7.1f}天 {r[0]/total_rows*100:>7.2f}% {r[1]/total_runs*100:>7.2f}%')
    print(f'{"合计":<12} {total_rows:>12,} {total_runs:>10,}')
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)