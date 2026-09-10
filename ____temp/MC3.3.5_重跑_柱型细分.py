# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - 柱型细分（正确柱型[27]，等1/等2/等3/等5）"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
C_DXAB=9; C_日ZC=14; C_次日高幅=26; C_柱型=27; C_日等型=44
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
def classify_zx(zx):
    """真实柱型[27]分类（按VBA生成代码）：
    阳柱：含'升'（升冲/升连/升待）或 枝贯/根贯的'连待/单待'（末位升连=连阳，否则单阳）
    阴柱：含'跌'（跌冲/跌待）或'线下四'或'踩警'
    """
    s=str(zx).strip()
    if '升' in s: return '阳柱'
    if '连待' in s: return '连阳'   # 枝贯连待/根贯连待 = 末位升连 = 连阳
    if '单待' in s: return '单阳'   # 枝贯单待/根贯单待 = 末位非升连 = 单阳
    if '跌' in s or '线下' in s or '踩警' in s: return '阴柱'
    return '其他'
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    agg=defaultdict(lambda:[0,0,0.0])  # (等型,护型,柱型细分)
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
        zx=df[C_柱型].astype(str).values
        hxs=[parse_hx(s) for s in dxab]
        for j in range(len(df)):
            hx=hxs[j]
            if not hx: continue
            if np.isnan(zc[j]) or zc[j]<=0: continue
            h=hr[j]
            if np.isnan(h) or h<-50 or h>50: continue
            dj=deng[j]
            if dj not in ('等1','等2','等3','等5'): continue
            zxc=classify_zx(zx[j])
            agg[(dj,hx,zxc)][0]+=1; agg[(dj,hx,zxc)][1]+=(1 if h>=3 else 0); agg[(dj,hx,zxc)][2]+=h
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    for deng in ['等1','等2','等3','等5']:
        print(f'\n【{deng} 柱型细分】(正确柱型[27])')
        for hx in ['甲','乙','己','戊']:
            row=[]
            for zxc in ['连阳','单阳','阳柱','阴柱','其他']:
                s=agg[(deng,hx,zxc)]
                row.append(f'{zxc}:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{zxc}:-')
            print(f'  {hx}: '+' | '.join(row))
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)