# -*- coding: utf-8 -*-
"""
周级别：WXZC>0 + WXAB存续期 条件分析
====================================================
用户问题：周级别分析是否添加 WXZC>0？还有其他条件？WXAB存续期呢？

说明：
- WXZC = ZC周[16]，我此前已用 ZC周>0（即 WXZC>0）
- WXAB存续期 = WXAB字符串[4]中护级后的数字（如"a甲↗上3.B3"→存续期3周）

输出：
  ① 操作区域内 P(HR≥3%) 按 WXAB存续期 分组
  ② 是否添加 WXAB存续期 条件能提升胜率
  ③ WXZC>0 与 WXCD 的关系（确认 WXZC>0 是否已隐含）

周CSV列序：3=HR, 4=WXAB, 13=WXCD, 14=ZA周, 16=ZC周
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

def extract_duration(wxab):
    """从WXAB字符串提取存续期：护级(上/忐/忠/中/忑/下)后的数字"""
    m = re.search(r'[上忐忠中忑下]\s*(-?\d+)', wxab)
    if m: return int(m.group(1))
    return None

# 操作区域内，按存续期分组: dur -> [n, hr3, sum_hr]
dur_stats = defaultdict(lambda: [0, 0, 0.0])
# 操作区域内各护型（含存续期）
hx_stats = defaultdict(lambda: [0, 0, 0.0])
# WXZC>0 与 WXCD 关系
wxcd_zc = defaultdict(lambda: [0, 0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组周')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组周_sz') or fname.startswith('谕组周_sh')): continue
    code = fname.replace('谕组周_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组周', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 16: continue
                wxab = row[4].strip()
                wxcd = row[13].strip()
                za = to_f(row[14])
                zc = to_f(row[16])
                hr = to_f(row[3])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(wxab[0], '') if wxab else ''
                if not hx: continue
                # WXZC>0 与 WXCD 关系
                if zc is not None:
                    wxcd_zc[wxcd][0 if zc > 0 else 1] += 1
                # 操作区域：WXZC>0 + 甲/乙ZA>0/己/乙ZA<0
                if zc > 0 and hx in ('甲', '乙', '己'):
                    dur = extract_duration(wxab)
                    if dur is not None:
                        dur_stats[dur][0]+=1; dur_stats[dur][1]+= (1 if hr>=3 else 0); dur_stats[dur][2]+=hr
                    hx_stats[hx][0]+=1; hx_stats[hx][1]+= (1 if hr>=3 else 0); hx_stats[hx][2]+=hr
    except Exception:
        pass

print(f'周级别高波池文件: {files_core}')
print()

print('=' * 70)
print('① 操作区域内 P(HR≥3%) 按 WXAB存续期 分组')
print('=' * 70)
print(f'{"存续期(周)":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
for dur in sorted(dur_stats.keys()):
    s = dur_stats[dur]
    if s[0] < 100: continue
    print(f'{dur:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 70)
print('② 操作区域内各护型 P(HR≥3%)（含WXZC>0）')
print('=' * 70)
print(f'{"护型":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
for hx in ['甲', '乙', '己']:
    s = hx_stats[hx]
    if s[0] == 0: continue
    print(f'{hx:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 70)
print('③ WXZC>0 与 WXCD 关系（确认WXZC>0是否已隐含）')
print('=' * 70)
print(f'{"WXCD":<12} {"ZC>0":>8} {"ZC<=0":>8} {"ZC>0占比":>8}')
print('-' * 45)
for wxcd, (pos, neg) in sorted(wxcd_zc.items(), key=lambda x: -x[1][0]):
    tot = pos + neg
    if tot < 100: continue
    print(f'{wxcd:<12} {pos:>8,} {neg:>8,} {pos/tot*100:>7.1f}%')
