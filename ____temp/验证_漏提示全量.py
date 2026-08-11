# -*- coding: utf-8 -*-
"""全算展文件验证漏提示 - 只读需要的列"""
import pandas as pd, numpy as np, os, glob, time, warnings
warnings.filterwarnings('ignore')
BASE = r'昭明算展/算展0724'
files = sorted(glob.glob(os.path.join(BASE, '算展.*.xlsx')))
print(f'共 {len(files)} 个文件')

全部数据 = []
t0 = time.time()
for fi, f in enumerate(files):
    try:
        # 只读需要的列：漏提示、HR、日机警、日周联动、护型DXAB
        df = pd.read_excel(f, sheet_name=0, usecols=['漏提示（金+甲乙）', 'HR', '日机警', '日周联动', '护型DXAB'])
        df['file'] = os.path.basename(f)
        全部数据.append(df)
    except Exception as e:
        print(f'  {f}: {e}')
    if (fi+1) % 10 == 0:
        print(f'  已处理 {fi+1}/{len(files)} ({time.time()-t0:.0f}s)', flush=True)

data = pd.concat(全部数据, ignore_index=True)
print(f'\n总行数: {len(data):,}, 耗时 {time.time()-t0:.0f}s')

# 漏提示有值判断
data['有漏'] = data['漏提示（金+甲乙）'].notna() & (data['漏提示（金+甲乙）'] != '')
data['HR'] = pd.to_numeric(data['HR'], errors='coerce')

# ========== 1. 有漏 vs 无漏 总览 ==========
print('\n' + '='*70)
print('一、有漏 vs 无漏 总体对比')
print('='*70)
有漏 = data[data['有漏']]
无漏 = data[~data['有漏']]
hr_有 = 有漏['HR'].dropna(); hr_无 = 无漏['HR'].dropna()
print(f'有漏: n={len(有漏):,} P(HR>2)={(hr_有>2).mean():.1%} P(HR>3)={(hr_有>3).mean():.1%} 均HR={hr_有.mean():.2f}%')
print(f'无漏: n={len(无漏):,} P(HR>2)={(hr_无>2).mean():.1%} P(HR>3)={(hr_无>3).mean():.1%} 均HR={hr_无.mean():.2f}%')
print(f'差异: P(HR>2)={ (hr_有>2).mean()-(hr_无>2).mean():+.1%}  P(HR>3)={(hr_有>3).mean()-(hr_无>3).mean():+.1%}')

# ========== 2. 按文件名（股票）稳定性 ==========
print('\n' + '='*70)
print('二、按文件（股票）验证区分度稳定性')
print('='*70)
rows = []
for fid, g in data.groupby('file'):
    if len(g) < 200: continue
    g_有 = g[g['有漏']]; g_无 = g[~g['有漏']]
    if len(g_有) < 30 or len(g_无) < 30: continue
    hr_有 = g_有['HR'].dropna(); hr_无 = g_无['HR'].dropna()
    diff = (hr_有 > 2).mean() - (hr_无 > 2).mean()
    rows.append((fid, len(g_有), len(g_无), (hr_有>2).mean(), (hr_无>2).mean(), diff))
# 排序
rows.sort(key=lambda x: -x[5])
正提升 = sum(1 for r in rows if r[5] > 0)
print(f'覆盖 {len(rows)} 个文件, 其中 {正提升} 个有漏比无漏P(HR>2)高 ({正提升/len(rows)*100:.0f}%)')
print(f'{"文件":<20} | {"有漏n":>6} | {"无漏n":>6} | {"有漏P(>2)":>8} | {"无漏P(>2)":>8} | {"差异":>8}')
for r in rows[:8]: print(f'{r[0]:<20} | {r[1]:>6,} | {r[2]:>6,} | {r[3]:>7.1%} | {r[4]:>7.1%} | {r[5]:>+7.1%}')
print('...')
for r in rows[-3:]: print(f'{r[0]:<20} | {r[1]:>6,} | {r[2]:>6,} | {r[3]:>7.1%} | {r[4]:>7.1%} | {r[5]:>+7.1%}')
有漏平均 = np.mean([r[5] for r in rows])
print(f'\n平均差异: {有漏平均:+.1%}')

# ========== 3. 漏提示子类别的HR对比 ==========
print('\n' + '='*70)
print('三、漏提示关键子类别（样本>=50）')
print('='*70)
# 提取子类关键词
def 提取子类(v):
    if not isinstance(v, str): return '无'
    v = v.split('__')[-1].split('.')[-1] if '.' in v else v
    # 取最后一段的状态词
    段 = v.replace('（', '').replace('）','')
    return 段
data['子类'] = data['漏提示（金+甲乙）'].astype(str).str.extract(r'\.([^.]*)$')[0]
# 主要状态词
状态词 = ['上持', '上漏', 'e漏', '首防诱', '被', '丙漏']
print(f'{"状态词":>10} | {"样本":>8} | {"P(HR>2)":>8} | {"P(HR>3)":>8} | {"均HR":>7}')
for 词 in 状态词:
    mask = data['漏提示（金+甲乙）'].astype(str).str.contains(词, na=False)
    sub = data[mask]
    if len(sub) < 50: continue
    hr = sub['HR'].dropna()
    print(f'{词:>10} | {len(sub):>8,} | {(hr>2).mean():>7.1%} | {(hr>3).mean():>7.1%} | {hr.mean():>6.2f}%')

# ========== 4. 上持 vs 上漏 vs e漏 三分类 ==========
print('\n' + '='*70)
print('四、上持/上漏/e漏 三分类（周级门通过后）')
print('='*70)
三分类 = {'上持': data['漏提示（金+甲乙）'].astype(str).str.contains('上持', na=False),
         '上漏': data['漏提示（金+甲乙）'].astype(str).str.contains('上漏', na=False),
         'e漏': data['漏提示（金+甲乙）'].astype(str).str.contains('e漏', na=False),
         '首防诱': data['漏提示（金+甲乙）'].astype(str).str.contains('首防诱', na=False),
         '被': data['漏提示（金+甲乙）'].astype(str).str.contains('被', na=False),
         '丙漏': data['漏提示（金+甲乙）'].astype(str).str.contains('丙漏', na=False)}
print(f'{"分类":>8} | {"样本":>8} | {"P(HR>2)":>8} | {"P(HR>3)":>8} | {"均HR":>7}')
for 名, mask in 三分类.items():
    sub = data[mask]
    if len(sub) < 30: continue
    hr = sub['HR'].dropna()
    print(f'{名:>8} | {len(sub):>8,} | {(hr>2).mean():>7.1%} | {(hr>3).mean():>7.1%} | {hr.mean():>6.2f}%')

print(f'\n耗时 {time.time()-t0:.0f}s')