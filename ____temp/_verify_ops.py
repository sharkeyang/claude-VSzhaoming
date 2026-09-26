import pandas as pd, numpy as np, sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_parquet('____temp/_day_data.parquet')
print('TOTAL ROWS:', len(df))

def get_hx(s):
    if not isinstance(s,str) or len(s)<2: return '?'
    return s[1]
df['护型'] = df['DXAB'].apply(get_hx)
df['阴柱'] = (df['PR'] < 0).astype(int)
df['ZC_pos'] = (df['ZC'] > 0).astype(int)

# 主战场 = DXZC>0 且 DXCD=上/忐
main = df[(df['ZC']>0) & (df['DXCD'].isin(['上','忐']))].copy()
print('主战场(DXZC>0+CD上忐)样本:', len(main))

# ===== 命题1: 升势判定 (DXAB>0且DXZB>0)=甲乙 =====
print('\n=== 1. 主战场内 升势(甲乙) vs 其他 ===')
sheng = main[main['护型'].isin(['甲','乙'])]
qita = main[~main['护型'].isin(['甲','乙'])]
print(f'升势(甲乙): n={len(sheng)}, P3={sheng["次日P3"].mean()*100:.2f}%, ret10={sheng["ret10"].mean():.2f}%, ret20={sheng["ret20"].mean():.2f}%')
print(f'其他: n={len(qita)}, P3={qita["次日P3"].mean()*100:.2f}%, ret10={qita["ret10"].mean():.2f}%, ret20={qita["ret20"].mean():.2f}%')

# ===== 命题2: DJA入口 (乙(DXZA<0)变乙(DXZA>0)) =====
print('\n=== 2. DJA入口: 乙(ZA<0) vs 乙(ZA>0) ===')
yi = main[main['护型']=='乙']
yi_neg = yi[yi['ZA']<0]
yi_pos = yi[yi['ZA']>=0]
print(f'乙(ZA<0): n={len(yi_neg)}, P3={yi_neg["次日P3"].mean()*100:.2f}%, ret10={yi_neg["ret10"].mean():.2f}%')
print(f'乙(ZA>=0): n={len(yi_pos)}, P3={yi_pos["次日P3"].mean()*100:.2f}%, ret10={yi_pos["ret10"].mean():.2f}%')

# ===== 命题3: 跌势判定 DXZC>0时丙丁戊 =====
print('\n=== 3. 主战场内 丙丁戊 (不应被利用非下跌) ===')
bing_ding_wu = main[main['护型'].isin(['丙','丁','戊'])]
print(f'主战场内丙丁戊: n={len(bing_ding_wu)}, P3={bing_ding_wu["次日P3"].mean()*100:.2f}%, ret10={bing_ding_wu["ret10"].mean():.2f}%')
# 对比全市场丙丁戊
all_bdw = df[df['护型'].isin(['丙','丁','戊'])]
print(f'全市场丙丁戊: n={len(all_bdw)}, P3={all_bdw["次日P3"].mean()*100:.2f}%, ret10={all_bdw["ret10"].mean():.2f}%')

# ===== 命题4: 阴柱介入 (DXZC>0每个阴柱) =====
print('\n=== 4. 主战场内 阴柱 vs 阳柱 ===')
yin = main[main['阴柱']==1]
yang = main[main['阴柱']==0]
print(f'阴柱: n={len(yin)}, P3={yin["次日P3"].mean()*100:.2f}%, ret5={yin["ret5"].mean():.2f}%, ret10={yin["ret10"].mean():.2f}%')
print(f'阳柱: n={len(yang)}, P3={yang["次日P3"].mean()*100:.2f}%, ret5={yang["ret5"].mean():.2f}%, ret10={yang["ret10"].mean():.2f}%')

# 阴柱细分: 升势内阴柱 vs 非升势内阴柱
yin_sheng = yin[yin['护型'].isin(['甲','乙'])]
yin_qita = yin[~yin['护型'].isin(['甲','乙'])]
print(f'阴柱+升势(甲乙): n={len(yin_sheng)}, P3={yin_sheng["次日P3"].mean()*100:.2f}%, ret5={yin_sheng["ret5"].mean():.2f}%')
print(f'阴柱+其他: n={len(yin_qita)}, P3={yin_qita["次日P3"].mean()*100:.2f}%, ret5={yin_qita["ret5"].mean():.2f}%')

# ===== 命题5: DJB入口 (前柱丙丁戊, 上破DJB = 护型从丙丁戊变甲乙己) =====
print('\n=== 5. DJB入口: 前柱丙丁戊 -> 现柱甲乙己 ===')
df['前护型'] = df.groupby('fid')['护型'].shift(1)
df['前阴柱'] = df.groupby('fid')['阴柱'].shift(1)
# 上破DJB = 前柱丙丁戊, 现柱甲乙己(从跌破DJB到站上DJB)
djb_in = df[(df['前护型'].isin(['丙','丁','戊'])) & (df['护型'].isin(['甲','乙','己']))]
djb_in_main = djb_in[(djb_in['ZC']>0) & (djb_in['DXCD'].isin(['上','忐']))]
print(f'上破DJB(全部): n={len(djb_in)}, P3={djb_in["次日P3"].mean()*100:.2f}%')
print(f'上破DJB(主战场): n={len(djb_in_main)}, P3={djb_in_main["次日P3"].mean()*100:.2f}%')

# ===== 命题6: DJC入口 (DXZC>0且DXCD=上) =====
print('\n=== 6. DJC入口: 主战场内 DXCD=上 vs 忐 ===')
main_shang = main[main['DXCD']=='上']
main_tan = main[main['DXCD']=='忐']
print(f'CD上: n={len(main_shang)}, P3={main_shang["次日P3"].mean()*100:.2f}%, ret10={main_shang["ret10"].mean():.2f}%')
print(f'CD忐: n={len(main_tan)}, P3={main_tan["次日P3"].mean()*100:.2f}%, ret10={main_tan["ret10"].mean():.2f}%')

# ===== 命题7: 正交后第一次下跌DJB (甲乙己->丙丁戊) =====
print('\n=== 7. 正交后转丙丁戊 是否反弹 ===')
zhuan = df[(df['前护型'].isin(['甲','乙','己'])) & (df['护型'].isin(['丙','丁','戊']))]
zhuan_main = zhuan[(zhuan['ZC']>0) & (zhuan['DXCD'].isin(['上','忐']))]
print(f'甲乙己->丙丁戊(全部): n={len(zhuan)}, P3={zhuan["次日P3"].mean()*100:.2f}%, ret10={zhuan["ret10"].mean():.2f}%')
print(f'甲乙己->丙丁戊(主战场): n={len(zhuan_main)}, P3={zhuan_main["次日P3"].mean()*100:.2f}%, ret10={zhuan_main["ret10"].mean():.2f}%')

print('\n=== DONE ===')
