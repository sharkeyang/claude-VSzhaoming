# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, glob, os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
t0=time.time()
DATA_DIR = '昭明算展/谕组日'

# 花册市板映射
hc = pd.read_excel('D:/zdata/昭明花册.xlsx', sheet_name='花天', engine='openpyxl')
board_map = dict(zip(hc['CIDL'].astype(str).str.strip(), hc['市板']))
board_map = {k: ('Qimit' if v in ('Qim','Qit') else v) for k,v in board_map.items()}

files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'总文件: {len(files)}', flush=True)

# 向量化等高线分类
def classify_vec(za_ser, mid_ser):
    za = pd.to_numeric(za_ser, errors='coerce')
    m = mid_ser.astype(str)
    last = m.str[-1]
    out = []
    for z, l in zip(za, last):
        if pd.isna(z): out.append('NA'); continue
        z = float(z)
        if z > 0:
            if z == 1: out.append('上1')
            elif z > 3 and l in 'CDEF': out.append('上4')
            elif z >= 2 and l in 'CDEF': out.append('上2')
            elif z >= 2 and l in 'AB': out.append('上3')
            else: out.append('上0')
        else:
            if z == -1: out.append('下1')
            elif z >= -3 and l in 'ABCD': out.append('下2')
            elif z <= -2 and l in 'EF': out.append('下3')
            elif z < -3 and l in 'ABCD': out.append('下4')
            else: out.append('下0')
    return out

frames = []
for i, f in enumerate(files):
    try:
        code = os.path.basename(f).replace('谕组日_','').replace('.csv','').strip()
        board = board_map.get(code)
        if board is None:
            continue
        df = pd.read_csv(f, encoding='gbk')
        df['市板'] = board
        df['等高线'] = classify_vec(df['日ZA'], df['中符串'])
        df['B3'] = df['BSHA'] > 3
        df['B5'] = df['BSHA'] > 5
        df['连阳'] = df['BT连阳'] > 0
        df['层主'] = df['层界'].astype(str).str.startswith('主')
        df['升排'] = df['柱排'].astype(str).str.startswith('升')
        df['周门'] = (df['日ZC'] > 0) & (df['DXCD']=='上')
        frames.append(df[['市板','等高线','B3','B5','连阳','层主','升排','周门','次日高幅']])
    except Exception as e:
        pass
    if (i+1) % 1000 == 0:
        print(f'  已处理 {i+1}/{len(files)} ({time.time()-t0:.0f}s)', flush=True)

data = pd.concat(frames, ignore_index=True)
print(f'总样本: {len(data):,} 行, {time.time()-t0:.0f}s', flush=True)

# 策略
strategies = []
for 等 in ['上1','上2','上3','上4','下1','下4']:
    for bname, bcol in [('BSHA3','B3'), ('BSHA5','B5')]:
        strategies.append((f'{等}+{bname}', (data['等高线']==等) & data[bcol]))
        strategies.append((f'{等}+{bname}+连阳', (data['等高线']==等) & data[bcol] & data['连阳']))
        strategies.append((f'{等}+{bname}+周门', (data['等高线']==等) & data[bcol] & data['周门']))
        strategies.append((f'{等}+{bname}+连阳+周门', (data['等高线']==等) & data[bcol] & data['连阳'] & data['周门']))
    strategies.append((f'{等}+连阳', (data['等高线']==等) & data['连阳']))
    strategies.append((f'{等}+层主', (data['等高线']==等) & data['层主']))
    strategies.append((f'{等}+层主+升排', (data['等高线']==等) & data['层主'] & data['升排']))

boards = ['Qd','Qe','Qif','Qic','Qimit','Qin','Qst']
results = []
for name, cond in strategies:
    sub = data[cond]
    n_total = len(sub)
    if n_total < 50: continue
    row = {'策略': name, '全量': n_total, '全量pct': (sub['次日高幅']>2).mean()}
    for b in boards:
        sb = sub[sub['市板']==b]
        row[f'{b}n'] = len(sb)
        row[f'{b}pct'] = (sb['次日高幅']>2).mean() if len(sb)>=20 else np.nan
    results.append(row)

for b in boards:
    sb = data[data['市板']==b]
    results.append({'策略': f'基准-{b}', '全量': len(sb), '全量pct': (sb['次日高幅']>2).mean()})
results.append({'策略': '基准-全样本', '全量': len(data), '全量pct': (data['次日高幅']>2).mean()})

df_res = pd.DataFrame(results).sort_values('全量pct', ascending=False)
df_res.to_csv('____temp/日冲策略_市板大表_全量.csv', index=False, encoding='utf-8-sig')
print(f'保存: ____temp/日冲策略_市板大表_全量.csv ({len(df_res)}策略)', flush=True)
print(f'总耗时: {time.time()-t0:.0f}s', flush=True)
