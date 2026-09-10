# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 管宽×BSHA + BSHA交叉（修正列：BSHA[19], 管宽[22]）"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
# 真实列（数据按VBA打印顺序）
C_DXAB=9; C_日ZC=14; C_BSHA=19; C_管宽=22; C_次日高幅=26; C_日等型=44
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    agg_kw=defaultdict(lambda:[0,0,0.0])   # (等型,护型,管宽档,BSHA档)
    agg_bs=defaultdict(lambda:[0,0,0.0])   # (护型,BSHA档)
    nfiles=0
    for f in files:
        code=os.path.basename(f).replace('谕组日_','').replace('.csv','')
        if board_map.get(code,'') not in 目标板块: continue
        nfiles+=1
        try: df=pd.read_csv(f,encoding='gbk',header=None,skiprows=1)
        except: continue
        if len(df)<5: continue
        dxab=df[C_DXAB].astype(str).values
        deng=df[C_日等型].astype(str).values
        hr=pd.to_numeric(df[C_次日高幅],errors='coerce').values
        zc=pd.to_numeric(df[C_日ZC],errors='coerce').values
        kw=pd.to_numeric(df[C_管宽],errors='coerce').values
        bs=pd.to_numeric(df[C_BSHA],errors='coerce').values
        hxs=[parse_hx(s) for s in dxab]
        for j in range(len(df)):
            hx=hxs[j]
            if not hx: continue
            if np.isnan(zc[j]) or zc[j]<=0: continue
            h=hr[j]
            if np.isnan(h) or h<-50 or h>50: continue
            dj=deng[j]
            if dj not in ('等1','等2','等3','等5','等6','等7'): continue
            # BSHA交叉
            if not np.isnan(bs[j]):
                b='BSHA5+' if bs[j]>=5 else 'BSHA<5'
                agg_bs[(hx,b)][0]+=1; agg_bs[(hx,b)][1]+=(1 if h>=3 else 0); agg_bs[(hx,b)][2]+=h
            # 管宽×BSHA
            if not np.isnan(kw[j]) and not np.isnan(bs[j]):
                kwb='宽' if kw[j]>=10 else '窄'
                bsb='高' if bs[j]>=8 else '低'
                agg_kw[(dj,hx,kwb,bsb)][0]+=1; agg_kw[(dj,hx,kwb,bsb)][1]+=(1 if h>=3 else 0); agg_kw[(dj,hx,kwb,bsb)][2]+=h
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    # 2.6 等7 管宽×BSHA
    print('\n【2.6 等7 管宽×BSHA】(修正: 管宽[22], BSHA[19])')
    for hx in ['乙','丙','丁']:
        row=[]
        for kwb in ['宽','窄']:
            for bsb in ['高','低']:
                s=agg_kw[('等7',hx,kwb,bsb)]
                row.append(f'{kwb}{bsb}:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{kwb}{bsb}:-')
        print(f'  {hx}: '+' | '.join(row))
    # 2.7 等6 管宽×BSHA
    print('\n【2.7 等6 管宽×BSHA】')
    for hx in ['乙','丙','丁']:
        row=[]
        for kwb in ['宽','窄']:
            for bsb in ['高','低']:
                s=agg_kw[('等6',hx,kwb,bsb)]
                row.append(f'{kwb}{bsb}:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{kwb}{bsb}:-')
        print(f'  {hx}: '+' | '.join(row))
    # 3.6 BSHA交叉
    print('\n【3.6 BSHA交叉关系】(修正: BSHA[19])')
    for hx in ['甲','乙','己','戊']:
        row=[]
        for b in ['BSHA5+','BSHA<5']:
            s=agg_bs[(hx,b)]
            row.append(f'{b}:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{b}:-')
        print(f'  {hx}: '+' | '.join(row))
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)