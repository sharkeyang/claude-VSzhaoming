# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 3.3 DXZC>0区域内DXAB交叉次数（用DXAB数值BTAB）"""
import re, pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
C_DXAB=9; C_日ZC=14; C_DXCD=8
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def extract_btab(s):
    m = re.search(r'([↗↘→→]?[上忐忠中下忑]?)(-?\d+)\.', s)
    if m: return int(m.group(2))
    return None
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    # 交叉次数分布: 交叉次数 -> [区域数, 总天数]
    cross=defaultdict(lambda:[0,0])
    # DXCD交叉: DXCD -> [区域数, 总交叉]
    cd_cross=defaultdict(lambda:[0,0])
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
        cd=df[C_DXCD].astype(str).values
        btabs=[extract_btab(s) for s in dxab]
        n=len(df)
        # 找DXZC>0连续区域
        i=0
        while i<n:
            if np.isnan(zc[i]) or zc[i]<=0: i+=1; continue
            j=i
            while j<n and not np.isnan(zc[j]) and zc[j]>0: j+=1
            # 区域[i,j)，统计DXAB交叉次数
            region_len=j-i
            # 区域内DXAB正负交叉次数
            cnt=0
            prev_sign=None
            dcd_set=set()
            for k in range(i,j):
                b=btabs[k]
                dcd_set.add(cd[k].strip())
                if b is None or b==0: continue
                sign='+' if b>0 else '-'
                if prev_sign is not None and sign!=prev_sign:
                    cnt+=1
                prev_sign=sign
            cross[min(cnt,6)][0]+=1
            cross[min(cnt,6)][1]+=region_len
            # DXCD交叉
            for dcd in dcd_set:
                cd_cross[dcd][0]+=1
                cd_cross[dcd][1]+=cnt
            i=j
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    print('\n【3.3 DXZC>0区域内DXAB交叉次数分布】')
    print(f'{"交叉次数":<8} {"区域数":>10} {"占比":>8} {"平均天数":>10}')
    total=sum(v[0] for v in cross.values())
    for c in [0,1,2,3,4,5,6]:
        s=cross[c]
        if s[0]>0:
            avg=s[1]/s[0] if s[0] else 0
            print(f'{c}次{"(6+)" if c==6 else ""}: {s[0]:>10,} {s[0]/total*100:>7.2f}% {avg:>9.2f}天')
    print('\n【DXZC>0区域内DXAB交叉次数 × DXCD】')
    print(f'{"DXCD":<6} {"区域数":>10} {"平均交叉/区域":>14}')
    for dcd in ['上','忐','忠']:
        s=cd_cross[dcd]
        if s[0]>0:
            avg=s[1]/s[0] if s[0] else 0
            print(f'{dcd:<6} {s[0]:>10,} {avg:>13.2f}次')
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)