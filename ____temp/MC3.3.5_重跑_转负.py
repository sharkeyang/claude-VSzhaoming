# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 转负概率(修正ZA提取)"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
C_DXAB=9; C_日ZC=14; C_次日高幅=26; C_日等型=44
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
def za_sign(s):
    """DXAB含A=ZA>0, 含Z=ZA<0"""
    if not s: return ''
    if 'A' in s: return '+'
    if 'Z' in s: return '-'
    return ''
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    # 转负: (护型) -> [n_ZA>0, 转负数]
    zhuanfu=defaultdict(lambda:[0,0])
    # 转负后次日高幅: (护型) -> [n, hr3, sum]
    zf_hr=defaultdict(lambda:[0,0,0.0])
    # 维持: (护型) -> [n, hr3, sum]
    weichi=defaultdict(lambda:[0,0,0.0])
    nfiles=0
    for f in files:
        code=os.path.basename(f).replace('谕组日_','').replace('.csv','')
        if board_map.get(code,'') not in 目标板块: continue
        nfiles+=1
        try: df=pd.read_csv(f,encoding='gbk',header=None,skiprows=1)
        except: continue
        if len(df)<5: continue
        dxab=df[C_DXAB].astype(str).values
        hr=pd.to_numeric(df[C_次日高幅],errors='coerce').values
        hxs=[parse_hx(s) for s in dxab]
        zas=[za_sign(s) for s in dxab]
        for j in range(len(df)-1):
            hx=hxs[j]
            if not hx: continue
            h=hr[j]
            if np.isnan(h) or h<-50 or h>50: continue
            if zas[j]=='+':
                zhuanfu[hx][0]+=1
                if zas[j+1]=='-':
                    zhuanfu[hx][1]+=1
                    zf_hr[hx][0]+=1; zf_hr[hx][1]+=(1 if h>=3 else 0); zf_hr[hx][2]+=h
                else:
                    weichi[hx][0]+=1; weichi[hx][1]+=(1 if h>=3 else 0); weichi[hx][2]+=h
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    print('\n【3.1 DXAB正交后转负概率】(ZA>0→ZA<0)')
    for hx in ['甲','乙','己','戊']:
        s=zhuanfu[hx]
        if s[0]>=MIN_SAMPLE:
            zf=zf_hr[hx]; wc=weichi[hx]
            print(f'  {hx}: 转负={s[1]/s[0]*100:.1f}% (n={s[0]:,})')
            if zf[0]>=MIN_SAMPLE:
                print(f'      转负后次日P(≥3%)={zf[1]/zf[0]*100:.1f}%({zf[0]:,})  维持={wc[1]/wc[0]*100:.1f}%({wc[0]:,})')
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)