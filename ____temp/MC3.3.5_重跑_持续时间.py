# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 3.2 DXAB持续时间 × DXCD（用DXAB数值BTAB）"""
import re, pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
C_DXAB=9; C_DXCD=8
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def extract_btab(s):
    m = re.search(r'([↗↘→→]?[上忐忠中下忑]?)(-?\d+)\.', s)
    if m: return int(m.group(2))
    return None
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    # (DXCD, 符号) -> [总天数, 段数]
    dur=defaultdict(lambda:[0,0])
    nfiles=0
    for f in files:
        code=os.path.basename(f).replace('谕组日_','').replace('.csv','')
        if board_map.get(code,'') not in 目标板块: continue
        nfiles+=1
        try: df=pd.read_csv(f,encoding='gbk',header=None,skiprows=1)
        except: continue
        if len(df)<5: continue
        dxab=df[C_DXAB].astype(str).values
        cd=df[C_DXCD].astype(str).values
        btabs=[extract_btab(s) for s in dxab]
        n=len(df)
        # 连续DXAB>0或<0且DXCD相同的段
        i=0
        while i<n:
            b=btabs[i]
            if b is None or b==0: i+=1; continue
            sign='+' if b>0 else '-'
            dcd=cd[i].strip()
            j=i
            while j<n and btabs[j] is not None and btabs[j]!=0 and (btabs[j]>0)==(b>0) and cd[j].strip()==dcd:
                j+=1
            length=j-i
            dur[(dcd,sign)][0]+=length
            dur[(dcd,sign)][1]+=1
            i=j
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    print('\n【3.2 DXAB>0/<0 持续时间 × DXCD】')
    print(f'{"DXCD":<6} {"正>0平均天数":>14} {"负<0平均天数":>14}')
    for dcd in ['上','忐','忠','中','忑','下']:
        pos=dur[(dcd,'+')]; neg=dur[(dcd,'-')]
        pos_avg=pos[0]/pos[1] if pos[1] else 0
        neg_avg=neg[0]/neg[1] if neg[1] else 0
        print(f'{dcd:<6} {pos_avg:>13.2f}天 {neg_avg:>13.2f}天')
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)