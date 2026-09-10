# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 3.1 转负概率（用DXAB数值BTAB，对比报告）"""
import re, pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
C_DXAB=9
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
def extract_btab(s):
    m = re.search(r'([↗↘→→]?[上忐忠中下忑]?)(-?\d+)\.', s)
    if m: return int(m.group(2))
    return None
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    # 转负: (护型, N天) -> [n_正交, 转负数]
    zhuanfu=defaultdict(lambda:[0,0])
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
        btabs=[extract_btab(s) for s in dxab]
        n=len(df)
        for j in range(n):
            hx=hxs[j]
            if not hx: continue
            b=btabs[j]
            if b is None or b<=0: continue  # 只从正交(BTAB>0)开始
            # 前向找转负(BTAB<0)
            zf_day=None
            for k in range(j+1, min(j+11, n)):
                if btabs[k] is not None and btabs[k]<0:
                    zf_day=k-j
                    break
            for N in ['1','3','5','10']:
                zhuanfu[(hx,N)][0]+=1
                if zf_day is not None and zf_day<=int(N):
                    zhuanfu[(hx,N)][1]+=1
            if zf_day is not None:
                avg_days[hx][0]+=1; avg_days[hx][1]+=zf_day
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    print('\n【3.1 DXAB正交后转负概率】(用DXAB数值BTAB)')
    print(f'{"护型":<6} {"1天":>10} {"3天":>10} {"5天":>10} {"10天":>10} {"平均转负天数":>12}')
    for hx in ['甲','乙','丙','己','戊']:
        s1=zhuanfu[(hx,'1')]
        if s1[0]<MIN_SAMPLE: continue
        s3=zhuanfu[(hx,'3')]; s5=zhuanfu[(hx,'5')]; s10=zhuanfu[(hx,'10')]
        ad=avg_days[hx]
        avg=ad[1]/ad[0] if ad[0] else 0
        print(f'{hx:<6} {s1[1]/s1[0]*100:>9.2f}% {s3[1]/s3[0]*100:>9.2f}% {s5[1]/s5[0]*100:>9.2f}% {s10[1]/s10[0]*100:>9.2f}% {avg:>11.2f}天')
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)