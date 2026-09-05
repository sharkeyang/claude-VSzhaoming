# -*- coding: utf-8 -*-
"""MC3.3.3 第二部分：连阳叠加、护型区分度、位置决策表、策略赛马、柱型交叉、增强过滤、触顶、BSHA提前介入"""
import csv, os
from collections import defaultdict

COL = {'DXCD':8,'DXAB':9,'日ZA':13,'日ZC':14,'日ZE':15,'BSHA':19,'次日高幅':26,
       '柱型':27,'层界':28,'上符串':30,'BT鼎':40,'BTZA':41,'BT连阳':42,'顶型':43,'日等型':44}
HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

def sf(v):
    try: return float(v)
    except: return None
def si(v):
    try: return int(float(v))
    except: return None

# 1.3.4 连阳叠加: (等型,ZC,护型) -> {BSHA5:[n,h2], BSHA5+连:[n,h2]}
lian = defaultdict(lambda: {'b5':[0,0],'b5l':[0,0]})
# 1.3.5 护型区分度: (等型,ZC) -> {护型:[n,h2]} 仅BSHA5
hx_bsha5 = defaultdict(lambda: defaultdict(lambda: [0,0]))
# 1.4.1 位置决策表: (等型,ZC,护型) -> [n,h2,h3] 基准 + BSHA5 + BSHA5+连
pos_full = defaultdict(lambda: {'base':[0,0,0],'b5':[0,0],'b5l':[0,0]})
# 1.4.2 策略赛马: 策略名 -> [n,h1,h2,h3]
race = defaultdict(lambda: [0,0,0,0])
# 1.4.3 柱型: 柱型 -> [n,h2,h3,sum,dn]
zx = defaultdict(lambda: [0,0,0,0.0,0])
# 1.5.5 操作区域限定: 等型 -> {全量:[n,h2], 操作区域:[n,h2]}
opzone = defaultdict(lambda: {'all':[0,0],'op':[0,0]})
# 1.5.5.6 触顶: 等型 -> {触顶:[n,h2], 不触顶:[n,h2]}
chuding = defaultdict(lambda: {'top':[0,0],'notop':[0,0]})
# 1.5.5.7 BSHA梯度: 等型 -> {BSHA2/3/4/5:[n,h2]}
bsha_grad = defaultdict(lambda: defaultdict(lambda: [0,0]))

files = sorted(os.listdir('昭明算展/谕组日'))
high_files = [f for f in files if f.endswith('.csv') and f.replace('谕组日_','').replace('.csv','') in high]
print(f'高波池文件: {len(high_files)}', flush=True)

processed = 0
for fname in high_files:
    fpath = os.path.join('昭明算展/谕组日', fname)
    try:
        with open(fpath, encoding='gbk') as f:
            reader = csv.reader(f); next(reader)
            for row in reader:
                if len(row) <= 44: continue
                etc = row[44].strip()
                if not etc.startswith('等'): continue
                dxab = row[9].strip()
                if not dxab: continue
                hx = HX_MAP.get(dxab[0], '?')
                zc = si(row[14])
                if zc is None: continue
                zc_sym = 'ZC>0' if zc>0 else 'ZC<0'
                bsha = sf(row[19])
                nxt = sf(row[26])
                if nxt is None: continue
                h2 = 1 if nxt>=2 else 0
                h3 = 1 if nxt>=3 else 0
                h1 = 1 if nxt>=1 else 0
                lian_v = si(row[42]) or 0
                ding_v = si(row[40]) or 0
                # 位置决策表
                pk = (etc, zc_sym, hx)
                pos_full[pk]['base'][0]+=1; pos_full[pk]['base'][1]+=h2; pos_full[pk]['base'][2]+=h3
                if bsha is not None and bsha>5:
                    pos_full[pk]['b5'][0]+=1; pos_full[pk]['b5'][1]+=h2
                    hx_bsha5[(etc,zc_sym)][hx][0]+=1; hx_bsha5[(etc,zc_sym)][hx][1]+=h2
                    if lian_v>0:
                        pos_full[pk]['b5l'][0]+=1; pos_full[pk]['b5l'][1]+=h2
                        lian[(etc,zc_sym,hx)]['b5l'][0]+=1; lian[(etc,zc_sym,hx)]['b5l'][1]+=h2
                    lian[(etc,zc_sym,hx)]['b5'][0]+=1; lian[(etc,zc_sym,hx)]['b5'][1]+=h2
                # 策略赛马
                if bsha is not None and bsha>5:
                    if zc>0 and hx in ('甲','乙','己'):
                        race['ZC>0+甲乙己+BSHA5|'+etc][0]+=1; race['ZC>0+甲乙己+BSHA5|'+etc][1]+=h1; race['ZC>0+甲乙己+BSHA5|'+etc][2]+=h2; race['ZC>0+甲乙己+BSHA5|'+etc][3]+=h3
                    if zc>0:
                        race['ZC>0+BSHA5|'+etc][0]+=1; race['ZC>0+BSHA5|'+etc][1]+=h1; race['ZC>0+BSHA5|'+etc][2]+=h2; race['ZC>0+BSHA5|'+etc][3]+=h3
                    race['BSHA5|'+etc][0]+=1; race['BSHA5|'+etc][1]+=h1; race['BSHA5|'+etc][2]+=h2; race['BSHA5|'+etc][3]+=h3
                # 柱型
                zxv = row[27].strip()
                if zxv:
                    zx[zxv][0]+=1; zx[zxv][1]+=h2; zx[zxv][2]+=h3; zx[zxv][3]+=nxt
                    if nxt>0: zx[zxv][4]+=1
                # 操作区域限定
                opzone[etc]['all'][0]+=1; opzone[etc]['all'][1]+=h2
                if zc>0 or (zc<=0 and hx in ('甲','乙','己')):
                    opzone[etc]['op'][0]+=1; opzone[etc]['op'][1]+=h2
                # 触顶 (上符串含v)
                sfch = row[30]
                if 'v' in sfch:
                    chuding[etc]['top'][0]+=1; chuding[etc]['top'][1]+=h2
                else:
                    chuding[etc]['notop'][0]+=1; chuding[etc]['notop'][1]+=h2
                # BSHA梯度
                if bsha is not None:
                    for th in [2,3,4,5]:
                        if bsha>th:
                            bsha_grad[etc][th][0]+=1; bsha_grad[etc][th][1]+=h2
    except Exception as e:
        print(f'错误 {fname}: {e}', flush=True)
    processed += 1
    if processed % 500 == 0:
        print(f'已处理 {processed}/{len(high_files)}', flush=True)

out = []
out.append('=== 1.3.4 连阳叠加 (BSHA5 -> BSHA5+连) ===')
for etc in ['等1','等2','等3','等5','等6','等7']:
    for zc_sym in ['ZC>0','ZC<0']:
        for hx in ['甲','乙','己']:
            key=(etc,zc_sym,hx)
            if key in lian and lian[key]['b5'][0]>0:
                b5=lian[key]['b5']; b5l=lian[key]['b5l']
                b5ls=f'{b5l[1]/b5l[0]*100:.1f}%(n={b5l[0]})' if b5l[0]>0 else '-'
                out.append(f'{etc}+{zc_sym}+{hx}: BSHA5={b5[1]/b5[0]*100:.1f}%(n={b5[0]}) -> +连={b5ls}')
out.append('')
out.append('=== 1.3.5 护型区分度 (BSHA5时) ===')
for etc in ['等1','等2','等3']:
    for zc_sym in ['ZC>0']:
        key=(etc,zc_sym)
        if key in hx_bsha5:
            s=f'{etc}+{zc_sym}: '
            for hx in ['甲','乙','己']:
                if hx in hx_bsha5[key]:
                    n,h2=hx_bsha5[key][hx]
                    s+=f'{hx}={h2/n*100:.1f}%(n={n}) '
            out.append(s)
out.append('')
out.append('=== 1.4.1 位置决策表 (基准/BSHA5/BSHA5+连) ===')
for etc in ['等1','等2','等3','等5','等6','等7']:
    for zc_sym in ['ZC>0','ZC<0']:
        for hx in ['甲','乙','丙','丁','戊','己']:
            key=(etc,zc_sym,hx)
            if key in pos_full and pos_full[key]['base'][0]>0:
                b=pos_full[key]['base']; b5=pos_full[key]['b5']; b5l=pos_full[key]['b5l']
                b5s=f'{b5[1]/b5[0]*100:.1f}%(n={b5[0]})' if b5[0]>0 else '-'
                b5ls=f'{b5l[1]/b5l[0]*100:.1f}%(n={b5l[0]})' if b5l[0]>0 else '-'
                out.append(f'{etc}+{zc_sym}+{hx}: 基准={b[1]/b[0]*100:.1f}%(n={b[0]}) BSHA5={b5s} +连={b5ls}')
out.append('')
out.append('=== 1.4.2 策略赛马 (BSHA5相关) ===')
for k,v in sorted(race.items(), key=lambda x:-x[1][2]/x[1][0] if x[1][0] else 0):
    n,h1,h2,h3=v
    if n>0:
        out.append(f'{k}: n={n}, H1={h1/n*100:.1f}%, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%')
out.append('')
out.append('=== 1.5.5.1 操作区域限定 ===')
for etc in ['等1','等2','等3','等5','等6','等7']:
    a=opzone[etc]['all']; o=opzone[etc]['op']
    out.append(f'{etc}: 全量={a[1]/a[0]*100:.1f}%(n={a[0]}) 操作区域={o[1]/o[0]*100:.1f}%(n={o[0]}) 提升={o[1]/o[0]*100-a[1]/a[0]*100:+.1f}pp')
out.append('')
out.append('=== 1.5.5.6 触顶 ===')
for etc in ['等1','等2','等3','等6']:
    t=chuding[etc]['top']; nt=chuding[etc]['notop']
    out.append(f'{etc}: 触顶={t[1]/t[0]*100:.1f}%(n={t[0]}) 不触顶={nt[1]/nt[0]*100:.1f}%(n={nt[0]}) 差异={t[1]/t[0]*100-nt[1]/nt[0]*100:+.1f}pp')
out.append('')
out.append('=== 1.5.5.7 BSHA梯度 ===')
for etc in ['等1','等2','等3','等6']:
    s=f'{etc}: '
    for th in [2,3,4,5]:
        if th in bsha_grad[etc] and bsha_grad[etc][th][0]>0:
            n,h2=bsha_grad[etc][th]
            s+=f'BSHA{th}={h2/n*100:.1f}%(n={n}) '
    out.append(s)

with open('____temp/mc333_results2.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('完成，写入 ____temp/mc333_results2.txt')
