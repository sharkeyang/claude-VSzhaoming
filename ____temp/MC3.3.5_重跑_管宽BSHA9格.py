# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 2.6/2.7 管宽×BSHA（正确列[22]管宽, [19]BSHA，按报告9格格式）"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
C_DXAB=9; C_日ZC=14; C_BSHA=19; C_管宽=22; C_次日高幅=26; C_日等型=44
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
def za_sign(s):
    if not s: return ''
    if 'A' in s: return '+'
    if 'Z' in s: return '-'
    return ''
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    agg=defaultdict(lambda:[0,0,0.0])  # (等型,护型,管宽档,BSHA档)
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
        zas=[za_sign(s) for s in dxab]
        for j in range(len(df)):
            hx=hxs[j]
            if not hx: continue
            if np.isnan(zc[j]) or zc[j]<=0: continue
            h=hr[j]
            if np.isnan(h) or h<-50 or h>50: continue
            dj=deng[j]
            if dj not in ('等6','等7'): continue
            if not np.isnan(kw[j]) and not np.isnan(bs[j]):
                kwb='<0' if kw[j]<0 else ('0-10' if kw[j]<10 else '>=10')
                bsb='<3' if bs[j]<3 else ('3-8' if bs[j]<8 else '>=8')
                agg[(dj,hx,kwb,bsb)][0]+=1; agg[(dj,hx,kwb,bsb)][1]+=(1 if h>=3 else 0); agg[(dj,hx,kwb,bsb)][2]+=h
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    for deng in ['等7','等6']:
        print(f'\n【{deng} 管宽×BSHA】(正确列: 管宽[22], BSHA[19])')
        for hx in ['乙','丙']:
            print(f'  {hx}:')
            for kwb in ['<0','0-10','>=10']:
                row=[]
                for bsb in ['<3','3-8','>=8']:
                    s=agg[(deng,hx,kwb,bsb)]
                    row.append(f'{bsb}:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{bsb}:-({s[0]:,})')
                print(f'    管宽{kwb}: '+' | '.join(row))
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)