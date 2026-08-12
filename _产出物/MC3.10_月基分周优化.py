#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.10_月基分周优化.py
=====================
月基分周（存续分）优化分析，对标 MC3.1 §9。

功能：
1. 波型×柱排 二维交叉表：实际P3 vs 当前查表分 → 数据驱动重算
2. WXAB调节方向：甲/乙/己 vs 丙/丁/戊 实际P3 → 新调节系数
3. 盈提示调节幅度：含高/含宽 实际P3 → 新调节幅度
4. 输出修正后的月基分周调节参数表

VBA当前查表（IQQQ跨码_D据擎2神谕.bas ~3120行）：
- 波型分类优先级：龙猪 > 龙管 > 头正 > 震正 > 震负 > 其他
- 柱排分类：首字='升'→升排, '人'→人排, '跌'→跌排
- 基础分：波型×柱排 二维表（续持率取整/0-100）
- WXAB调节：甲+3, 乙-3, 己-5, 丙丁戊=0
- 盈提示调节：高+4, 高+宽+8, 宽=0

用法：
    python _产出物/MC3.10_月基分周优化.py

输出：
    - 控制台 + _分析输出/MC3.10_月基分周优化.txt
"""

import pandas as pd, os, glob, sys, warnings
from collections import OrderedDict
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 100
os.makedirs(OUTDIR, exist_ok=True)

# ── 加载数据 ──
def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组周_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(wfiles)} 文件...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下周HR'])
    return wk

# ── 波型/柱排分类（与VBA一致） ──
def classify_波型(s):
    """按VBA优先级分类：龙猪 > 龙管 > 头正 > 震正 > 震负 > 其他"""
    if '龙猪' in str(s): return '龙猪'
    if '龙管' in str(s): return '龙管'
    if '头正' in str(s): return '头正'
    if '震正' in str(s): return '震正'
    if '震负' in str(s): return '震负'
    return '其他'

def classify_柱排(s):
    """按VBA分类：首字=升/人/跌 → 升排/人排/跌排"""
    s = str(s)
    if not s: return '其他'
    c = s[0]
    if c == '升': return '升排'
    if c == '人': return '人排'
    if c == '跌': return '跌排'
    return '其他'

def classify_WXAB(s):
    """提取WXAB核心分类"""
    s = str(s)
    for ab in ['甲','乙','丙','丁','戊','己']:
        if ab in s: return ab
    return '其他'

def classify_盈提示(s):
    """分类：高+宽, 高, 宽, 空, 其他"""
    s = str(s)
    if '高' in s and '宽' in s: return '高+宽'
    if '高' in s: return '高(不含宽)'
    if '宽' in s: return '宽(不含高)'
    if not s or s == '': return '空'
    return '其他'

# ── 主程序 ──
print('=' * 80)
print('MC3.10 月基分周优化分析')
print('=' * 80)
print()
wk = load_all()

# 计算基线
baseline = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P3 = {baseline:.1f}%')
print()

output = []

# ════════════════════════════════════════════════════════════
# 1. 波型×柱排 二维交叉表
# ════════════════════════════════════════════════════════════
print('─' * 80)
print('1. 波型×柱排 二维交叉表（实际P3 vs 当前查表分）')
print('─' * 80)

# 当前VBA查表
VBA_TABLE = {
    '龙猪': {'升排': 75, '人排': 61, '跌排': 58, '其他': 65},
    '龙管': {'升排': 70, '人排': 58, '跌排': 56, '其他': 61},
    '头正': {'升排': 63, '人排': 58, '跌排': 51, '其他': 57},
    '震正': {'升排': 65, '人排': 56, '跌排': 51, '其他': 57},
    '震负': {'升排': 62, '人排': 58, '跌排': 50, '其他': 57},
    '其他': {'升排': 65, '人排': 57, '跌排': 52, '其他': 58},
}

# 分类
wk['波型类'] = wk['波型'].apply(classify_波型)
wk['柱排类'] = wk['柱排周'].apply(classify_柱排)

# 二维交叉表
波型列表 = ['龙猪', '龙管', '头正', '震正', '震负', '其他']
柱排列表 = ['升排', '人排', '跌排', '其他']

lines = ['\n实际P3表（下周HR≥3%的概率）：']
波柱头 = '波型/柱排'
lines.append(f'{波柱头:>10s}' + ''.join(f'{c:>8s}' for c in 柱排列表) + f'  {"样本":>10s}')
lines.append('-' * 70)

for 波型 in 波型列表:
    row_vals = []
    row_n = []
    for 柱排 in 柱排列表:
        grp = wk[(wk['波型类'] == 波型) & (wk['柱排类'] == 柱排)]
        n = len(grp)
        if n >= MIN_SAMPLE:
            p = (grp['下周HR'] >= 3).mean() * 100
            row_vals.append(f'{p:>6.1f}%')
        else:
            row_vals.append(f'{"-":>7s}')
        row_n.append(f'({n:,d})')
    lines.append(f'{波型:>10s}  {"  ".join(row_vals)}  {row_n}')

lines.append('')
lines.append('当前VBA查表分（续持率取整）：')
lines.append(f'{波柱头:>10s}' + ''.join(f'{c:>8s}' for c in 柱排列表))
lines.append('-' * 60)
for 波型 in 波型列表:
    row_vals = [f'{VBA_TABLE[波型][c]:>7d}' for c in 柱排列表]
    lines.append(f'{波型:>10s}  {"  ".join(row_vals)}')
lines.append('')

# 逐格对比
lines.append('逐格对比（实际P3 → 建议查表分）：')
lines.append(f'{波柱头:>10s}  {"".join(f"{c:>14s}" for c in 柱排列表)}')
lines.append('-' * 80)
for 波型 in 波型列表:
    cells = []
    for 柱排 in 柱排列表:
        grp = wk[(wk['波型类'] == 波型) & (wk['柱排类'] == 柱排)]
        n = len(grp)
        if n >= MIN_SAMPLE:
            p = (grp['下周HR'] >= 3).mean() * 100
            vba = VBA_TABLE[波型][柱排]
            diff = p - vba
            # 建议分 = 实际P3缩放（按当前基线比例）
            # 当前查表是续持率(0-100), 实际P3是百分比。用P3作为新查表分
            suggested = round(p, 1)
            cells.append(f'{suggested:>5.1f}(原{vba},差{diff:>+4.1f})')
        else:
            cells.append(f'{"-":>14s}')
    lines.append(f'{波型:>10s}  {"  ".join(cells)}')
lines.append('')

# 建议新查表（将P3映射到0-100）
lines.append('建议新查表分（P3映射到0-100，保留原分布）：')
lines.append(f'{波柱头:>10s}' + ''.join(f'{c:>8s}' for c in 柱排列表))
lines.append('-' * 60)
for 波型 in 波型列表:
    row_vals = []
    for 柱排 in 柱排列表:
        grp = wk[(wk['波型类'] == 波型) & (wk['柱排类'] == 柱排)]
        n = len(grp)
        if n >= MIN_SAMPLE:
            p = (grp['下周HR'] >= 3).mean() * 100
            # 缩放：当前基线约46%，目标基线约75。缩放因子 = 75/46
            # 但更合理的做法：直接用P3作为新分，因为VBA查表是0-100
            suggested = round(p, 1)
            row_vals.append(f'{suggested:>7.1f}')
        else:
            row_vals.append(f'{"-":>7s}')
    lines.append(f'{波型:>10s}  {"  ".join(row_vals)}')
lines.append('')

out = '\n'.join(lines)
print(out)
output.append(out)

# ════════════════════════════════════════════════════════════
# 2. WXAB调节方向
# ════════════════════════════════════════════════════════════
print('─' * 80)
print('2. WXAB调节方向（实际P3 vs 基线 + 当前调节系数）')
print('─' * 80)

wk['WXAB类'] = wk['WXAB'].apply(classify_WXAB)

# 当前VBA调节
VBA_WXAB_ADJ = {'甲': 3, '乙': -3, '己': -5, '丙': 0, '丁': 0, '戊': 0}

lines = ['\nWXAB各等级实际P3：',
         f'{"WXAB":>6s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>8s}  {"当前调节":>8s}  {"建议调节":>8s}  {"说明"}',
         '-' * 70]
for ab in ['甲','乙','丙','丁','戊','己']:
    grp = wk[wk['WXAB类'] == ab]
    n = len(grp)
    if n >= MIN_SAMPLE:
        p = (grp['下周HR'] >= 3).mean() * 100
        diff = p - baseline
        current = VBA_WXAB_ADJ.get(ab, 0)
        # 建议调节：diff/5 取整（每5pp对应1分）
        suggested = round(diff / 5) * 5  # 最接近的5的倍数
        if suggested == 0 and abs(diff) > 3:
            suggested = 5 if diff > 0 else -5
        note = ''
        if current > 0 and diff < 0:
            note = '⚠️ 方向反了'
        elif current < 0 and diff > 0:
            note = '⚠️ 方向反了'
        elif abs(diff) > 5 and abs(current) < abs(suggested):
            note = '调节不足'
        elif abs(diff) < 2 and abs(current) > 0:
            note = '无需调节'
        lines.append(f'{ab:>6s}  {n:>8,d}  {p:>6.1f}%  {diff:>+7.1f}pp  {current:>+7d}    {suggested:>+6d}    {note}')
out = '\n'.join(lines)
print(out)
output.append(out)

# ════════════════════════════════════════════════════════════
# 3. 盈提示调节幅度
# ════════════════════════════════════════════════════════════
print('─' * 80)
print('3. 盈提示调节幅度（实际P3 vs 基线 + 当前调节系数）')
print('─' * 80)

wk['盈提示类'] = wk['盈提示'].apply(classify_盈提示)

# 当前VBA调节
VBA_YT_ADJ = {'高+宽': 8, '高(不含宽)': 4, '宽(不含高)': 0, '空': 0, '其他': 0}

lines = ['\n盈提示各等级实际P3：',
         f'{"盈提示":>14s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>8s}  {"当前调节":>8s}  {"建议调节":>8s}  {"说明"}',
         '-' * 70]
for yt in ['高+宽', '高(不含宽)', '宽(不含高)', '空', '其他']:
    grp = wk[wk['盈提示类'] == yt]
    n = len(grp)
    if n >= MIN_SAMPLE:
        p = (grp['下周HR'] >= 3).mean() * 100
        diff = p - baseline
        current = VBA_YT_ADJ.get(yt, 0)
        # 建议调节：diff/5 取整
        suggested = round(diff / 5) * 5
        if suggested == 0 and abs(diff) > 2:
            suggested = 5 if diff > 0 else -5
        note = ''
        if abs(diff) > 10 and abs(current) < 4:
            note = '大幅调节不足'
        elif abs(diff) > 5 and abs(current) < abs(suggested):
            note = '调节不足'
        lines.append(f'{yt:>14s}  {n:>8,d}  {p:>6.1f}%  {diff:>+7.1f}pp  {current:>+7d}    {suggested:>+6d}    {note}')
out = '\n'.join(lines)
print(out)
output.append(out)

# 盈提示内部细分：宽高等级
print('\n盈提示含"高"的细分等级：')
lines = ['\n盈提示含"高"的细分等级：',
         f'{"盈提示":>14s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>8s}',
         '-' * 50]
for yt in sorted(wk['盈提示'].dropna().unique()):
    if '高' in str(yt):
        grp = wk[wk['盈提示'] == yt]
        n = len(grp)
        if n >= MIN_SAMPLE:
            p = (grp['下周HR'] >= 3).mean() * 100
            diff = p - baseline
            lines.append(f'{yt:>14s}  {n:>8,d}  {p:>6.1f}%  {diff:>+7.1f}pp')
out = '\n'.join(lines)
print(out)
output.append(out)

# ════════════════════════════════════════════════════════════
# 4. 综合建议
# ════════════════════════════════════════════════════════════
print('─' * 80)
print('4. 综合建议')
print('─' * 80)

lines = ['\n综合建议：',
         '=' * 60]

# 建议1：基础分表
lines.append('\n【基础分表】建议新值（P3直接作为查表分，0-100）：')
lines.append(f'{波柱头:>10s}' + ''.join(f'{c:>8s}' for c in 柱排列表))
lines.append('-' * 60)
for 波型 in 波型列表:
    row_vals = []
    for 柱排 in 柱排列表:
        grp = wk[(wk['波型类'] == 波型) & (wk['柱排类'] == 柱排)]
        n = len(grp)
        if n >= MIN_SAMPLE:
            p = (grp['下周HR'] >= 3).mean() * 100
            row_vals.append(f'{round(p,1):>7.1f}')
        else:
            row_vals.append(f'{"-":>7s}')
    lines.append(f'{波型:>10s}  {"  ".join(row_vals)}')

# 建议2：WXAB调节
lines.append('\n【WXAB调节】建议新系数：')
for ab in ['甲','乙','丙','丁','戊','己']:
    grp = wk[wk['WXAB类'] == ab]
    n = len(grp)
    if n >= MIN_SAMPLE:
        p = (grp['下周HR'] >= 3).mean() * 100
        diff = p - baseline
        suggested = round(diff / 5) * 5
        if suggested == 0 and abs(diff) > 3:
            suggested = 5 if diff > 0 else -5
        current = VBA_WXAB_ADJ.get(ab, 0)
        lines.append(f'  WXAB={ab}: 当前{current:+d} → 建议{suggested:+d} (实际P3={p:.1f}%, vs基线={diff:+.1f}pp)')

# 建议3：盈提示调节
lines.append('\n【盈提示调节】建议新系数：')
for yt in ['高+宽', '高(不含宽)', '宽(不含高)']:
    grp = wk[wk['盈提示类'] == yt]
    n = len(grp)
    if n >= MIN_SAMPLE:
        p = (grp['下周HR'] >= 3).mean() * 100
        diff = p - baseline
        suggested = round(diff / 5) * 5
        if suggested == 0 and abs(diff) > 2:
            suggested = 5 if diff > 0 else -5
        current = VBA_YT_ADJ.get(yt, 0)
        lines.append(f'  {yt}: 当前{current:+d} → 建议{suggested:+d} (实际P3={p:.1f}%, vs基线={diff:+.1f}pp)')

# 建议4：盈提示含高细分（选择最佳分级）
lines.append('\n【盈提示含高】细分对比（决定是否分级调节）：')
high_groups = wk[wk['盈提示类'].str.contains('高', na=False)].groupby('盈提示')
for yt, grp in sorted(high_groups):
    n = len(grp)
    if n >= MIN_SAMPLE:
        p = (grp['下周HR'] >= 3).mean() * 100
        diff = p - baseline
        lines.append(f'  {yt:<14s}  n={n:>6,d}  P3={p:>5.1f}%  vs基线={diff:>+5.1f}pp')

lines.append('')
out = '\n'.join(lines)
print(out)
output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.10_月基分周优化.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')