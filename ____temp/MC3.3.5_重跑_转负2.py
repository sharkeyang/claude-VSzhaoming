# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 转负概率(修正: 前向N天DXAB变负)"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
C_DXAB=9; C_次日高幅=26
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
def is_pos(s):
    """DXAB>0 = 含A"""
    return 'A' in s
def is_neg(s):
    """DXAB<0 = 含Z"""
    return 'Z' in s
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    # 转负: (护型, N天) -> [n_正交, 转负数]
    zhuanfu=defaultdict(lambda:[0,0])
    # 平均转负天数: (护型) -> [n, 天数sum]
    avg_days=defaultdict(lambda:[0,0.0])
    nfiles=0
    for f in files:
        code=os.path.basename(f).replace('谕组日_','').replace('.csv','')
        if board_map.get(code,'') not in 目标板块: continue
        nfiles+=1
        try: df=pd.read_csv(f,encoding='gbk',header=None,skiprows=1)
        except: continue
        if len(df)<5: continue
        dxab=df[C_DXAB].astype(str).values
        hxs=[parse_hx(s) for s in dxab]
        poss=[is_pos(s) for s in dxab]
        negs=[is_neg(s) for s in dxab]
        n=len(df)
        for j in range(n):
            hx=hxs[j]
            if not hx: continue
            if not poss[j]: continue  # 只从正交(DXAB>0)开始
            # 前向找转负
            zf_day=None
            for k in range(j+1, min(j+11, n)):
                if negs[k]:
                    zf_day=k-j
                    break
            if zf_day is not None:
                zhuanfu[(hx,'1')][0]+=1
                if zf_day<=1: zhuanfu[(hx,'1')][1]+=1
                zhuanfu[(hx,'3')][0]+=1
                if zf_day<=3: zhuanfu[(hx,'3')][1]+=1
                zhuanfu[(hx,'5')][0]+=1
                if zf_day<=5: zhuanfu[(hx,'5')][1]+=1
                zhuanfu[(hx,'10')][0]+=1
                if zf_day<=10: zhuanfu[(hx,'10')][1]+=1
                avg_days[hx][0]+=1; avg_days[hx][1]+=zf_day
            else:
                # 10天内未转负
                zhuanfu[(hx,'1')][0]+=1
                zhuanfu[(hx,'3')][0]+=1
                zhuanfu[(hx,'5')][0]+=1
                zhuanfu[(hx,'10')][0]+=1
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    print('\n【3.1 DXAB正交后转负概率】(DXAB>0后N天内转负)')
    print(f'{"护型":<6} {"1天":>10} {"3天":>10} {"5天":>10} {"10天":>10} {"平均转负天数":>12}')
    for hx in ['甲','乙','己','戊','丙']:
        s1=zhuanfu[(hx,'1')]
        if s1[0]<MIN_SAMPLE: continue
        s3=zhuanfu[(hx,'3')]; s5=zhuanfu[(hx,'5')]; s10=zhuanfu[(hx,'10')]
        ad=avg_days[hx]
        avg=ad[1]/ad[0] if ad[0] else 0
        print(f'{hx:<6} {s1[1]/s1[0]*100:>9.1f}% {s3[1]/s3[0]*100:>9.1f}% {s5[1]/s5[0]*100:>9.1f}% {s10[1]/s10[0]*100:>9.1f}% {avg:>11.1f}天')
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)