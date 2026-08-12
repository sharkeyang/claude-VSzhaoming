#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9_全量周微观指标P3.py
=====================
全量周微观指标下周P3(HR≥3%)验证，对标 MC3.1 §1.1/§3.1/§6.8。

功能：
1. 周波型全量P3
2. 周柱排全量P3
3. 周柱型全量P3
4. WXCD全量P3
5. WXAB全量P3
6. 盈提示全量P3
7. 最后一柱形态全量P3（§6.8全量重审）

用法：
    python _产出物/MC3.9_全量周微观指标P3.py

输出：
    - 控制台 + _分析输出/MC3.9_周微观指标P3.txt
"""

import pandas as pd, os, glob, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 100
os.makedirs(OUTDIR, exist_ok=True)

def load_all():
    """加载所有周CSV为一个DataFrame，附加下周HR"""
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组周_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(wfiles)} 文件...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) >= 2:
                df['fid'] = i  # 每只股票一个ID，用于groupby
                dfs.append(df)
        except:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    # 下周HR = 同股票下一条周线的HR（shift(-1) per group）
    wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
    # 上周数据（shift(1) per group）
    wk['上周PR'] = wk.groupby('fid')['PR'].shift(1)
    wk['上周ZA'] = wk.groupby('fid')['ZA周'].shift(1)
    wk['下周柱排周'] = wk.groupby('fid')['柱排周'].shift(-1)
    # 去掉最后一行（无下周HR）
    wk = wk.dropna(subset=['下周HR'])
    print(f'  [加载] 完成: {len(wfiles)} 文件, {len(wk)} 行, {len(wk[wk.fid != wk.fid.shift(1)]) + 1} 只股票', flush=True)
    return wk

def rep(name, mask, n_min=MIN_SAMPLE):
    """计算符合条件的下周P3"""
    g = wk[mask]
    n = len(g)
    if n < n_min:
        return None, n, 0
    nh3 = (g['下周HR'] >= 3).mean() * 100
    return nh3, n, sum(g['下周HR'] >= 3)

def print_table(title, items, label_width=24):
    """打印格式化表：条件|样本|P3%|vs基线|说明"""
    lines = [f'\n{"=" * 80}', f'{title}', f'{"=" * 80}']
    header = f'{"条件":<{label_width}s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>7s}  {"说明"}'
    lines.append(header)
    lines.append('-' * (label_width + 8 + 7 + 7 + 20))
    for name, cond_fn, note in items:
        p, n, s = rep(name, cond_fn)
        if p is None:
            lines.append(f'{name:<{label_width}s}  {n:>8,d}  {"-":>7s}  {"-":>7s}  (样本不足)')
        else:
            diff = p - baseline
            lines.append(f'{name:<{label_width}s}  {n:>8,d}  {p:>6.1f}%  {diff:>+7.1f}pp  {note}')
    lines.append('')
    return '\n'.join(lines)

# ============================================================
# 主程序
# ============================================================
print('=' * 80)
print('MC3.9 全量周微观指标P3验证')
print('=' * 80)
print()
wk = load_all()

baseline = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n{"=" * 80}')
print(f'全样本: {total} 行, 基线下周P3 = {baseline:.1f}%')
print(f'{"=" * 80}')

output = []

# ── 1. 周波型 ──
items = [
    ('Aa龙猪', wk['波型'].str.contains('Aa龙猪', na=False), ''),
    ('Be龙管根', wk['波型'].str.contains('Be龙管根', na=False), ''),
    ('Bc龙管栅', wk['波型'].str.contains('Bc龙管栅', na=False), ''),
    ('Bd龙管杂', wk['波型'].str.contains('Bd龙管杂', na=False), ''),
    ('Fa震正〇', wk['波型'].str.contains('Fa震正〇', na=False), ''),
    ('Fd震正芽', wk['波型'].str.contains('Fd震正芽', na=False), ''),
    ('Fe震正根', wk['波型'].str.contains('Fe震正根', na=False), ''),
    ('Ff震负', wk['波型'].str.contains('Ff震负', na=False), ''),
    ('头正', wk['波型'].str.contains('头正', na=False), ''),
    ('震正', wk['波型'].str.contains('震正', na=False), ''),
    ('震负', wk['波型'].str.contains('震负', na=False), ''),
    ('龙猪', wk['波型'].str.contains('龙猪', na=False), 'Aa龙猪'),
    ('龙管', wk['波型'].str.contains('龙管', na=False), 'Be/Bc/Bd龙管'),
]
out = print_table('1. 周波型全量P3', items)
print(out)
output.append(out)

# ── 2. 周柱排 ──
items = [
    ('升.尾连', wk['柱排周'].str.contains('升.尾连', na=False), ''),
    ('升.尾反孕', wk['柱排周'].str.contains('升.尾反孕', na=False), ''),
    ('升.尾吞', wk['柱排周'].str.contains('升.尾吞', na=False), ''),
    ('跌.尾连', wk['柱排周'].str.contains('跌.尾连', na=False), ''),
    ('跌.尾反孕', wk['柱排周'].str.contains('跌.尾反孕', na=False), ''),
    ('跌.尾吞', wk['柱排周'].str.contains('跌.尾吞', na=False), ''),
    ('(升)人.*', wk['柱排周'].str.contains(r'\(升\)人', na=False), ''),
    ('(跌)人.*', wk['柱排周'].str.contains(r'\(跌\)人', na=False), ''),
    ('(人)人.吞吞', wk['柱排周'].str.contains(r'\(人\)人.*吞吞', na=False), ''),
    ('(人)人.孕孕', wk['柱排周'].str.contains(r'\(人\)人.*孕孕', na=False), ''),
    ('升.尾反孕(细分)', wk['柱排周'].str.contains('升.尾反孕Qv', na=False), '核心反孕'),
    ('升.尾反孕(细分2)', wk['柱排周'].str.contains('升.尾反孕vOv', na=False), '变体'),
]
out = print_table('2. 周柱排全量P3', items)
print(out)
output.append(out)

# ── 3. 周柱型 ──
items = [
    ('.01梯升连冲Q', wk['柱型周'] == '.01梯升连冲Q', '梯升连冲'),
    ('.02梯升孕冲Qv', wk['柱型周'] == '.02梯升孕冲Qv', '梯升孕冲'),
    ('.03梯升调待Qvo', wk['柱型周'] == '.03梯升调待Qvo', '梯升调待'),
    ('.04梯交调待vO', wk['柱型周'] == '.04梯交调待vO', '梯交调待'),
    ('.05梯交跌警vOv', wk['柱型周'] == '.05梯交跌警vOv', '梯交跌警'),
    ('.11栏调吞待QVO', wk['柱型周'] == '.11栏调吞待QVO', '栏调吞待'),
    ('.12栏调孕待QVo', wk['柱型周'] == '.12栏调孕待QVo', '栏调孕待'),
    ('.15栏调跌警QV', wk['柱型周'] == '.15栏调跌警QV', '栏调跌警'),
    ('.21栅调吞待', wk['柱型周'].str.contains('.21栅调吞待', na=False), '栅调吞待'),
    ('.22栅调孕待', wk['柱型周'].str.contains('.22栅调孕待', na=False), '栅调孕待'),
    ('.25栅调跌警', wk['柱型周'].str.contains('.25栅调跌警', na=False), '栅调跌警'),
    ('.35杂调升待', wk['柱型周'] == '.35杂调升待', '杂调升待'),
    ('.36杂调人待', wk['柱型周'] == '.36杂调人待', '杂调人待'),
    ('.37杂调跌待', wk['柱型周'] == '.37杂调跌待', '杂调跌待'),
    ('.41枝启升冲', wk['柱型周'] == '.41枝启升冲', '枝启升冲'),
    ('.42枝启踩警', wk['柱型周'] == '.42枝启踩警', '枝启踩警'),
    ('.44枝贯单待A', wk['柱型周'] == '.44枝贯单待A', '枝贯单待'),
    ('.44枝贯连待X', wk['柱型周'] == '.44枝贯连待X', '枝贯连待'),
    ('.51根启跌冲', wk['柱型周'] == '.51根启跌冲', '根启跌冲'),
    ('.52根启踩警', wk['柱型周'] == '.52根启踩警', '根启踩警'),
    ('.55根贯单待A', wk['柱型周'] == '.55根贯单待A', '根贯单待'),
    ('.55根贯连待X', wk['柱型周'] == '.55根贯连待X', '根贯连待'),
    ('.99线下四', wk['柱型周'] == '.99线下四', '线下四'),
]
out = print_table('3. 周柱型全量P3', items, label_width=22)
print(out)
output.append(out)

# ── 4. WXCD ──
items = [
    ('金升', wk['WXCD'].str.contains('金升', na=False), ''),
    ('银升', wk['WXCD'].str.contains('银升', na=False), ''),
    ('唏待', wk['WXCD'].str.contains('唏', na=False), ''),
    ('嘘降', wk['WXCD'].str.contains('嘘', na=False), ''),
    ('尿降', wk['WXCD'].str.contains('尿', na=False), ''),
    ('屎降', wk['WXCD'].str.contains('屎', na=False), ''),
    ('金升+银升', wk['WXCD'].str.contains('金|银', na=False), '金+银合并'),
    ('唏+嘘+尿+屎', ~wk['WXCD'].str.contains('金|银', na=False), '非金非银合并'),
]
out = print_table('4. WXCD全量P3', items)
print(out)
output.append(out)

# ── 5. WXAB ──
items = [
    ('甲', wk['WXAB'].str.contains('甲', na=False), ''),
    ('乙', wk['WXAB'].str.contains('乙', na=False), ''),
    ('丙', wk['WXAB'].str.contains('丙', na=False), ''),
    ('丁', wk['WXAB'].str.contains('丁', na=False), ''),
    ('戊', wk['WXAB'].str.contains('戊', na=False), ''),
    ('己', wk['WXAB'].str.contains('己', na=False), ''),
    ('甲+乙+己', wk['WXAB'].str.contains('甲|乙|己', na=False), '优秀护型'),
    ('丙+丁+戊', wk['WXAB'].str.contains('丙|丁|戊', na=False), '较差护型'),
]
out = print_table('5. WXAB全量P3', items)
print(out)
output.append(out)

# ── 6. 盈提示 ──
items = [
    ('含高', wk['盈提示'].str.contains('高', na=False), ''),
    ('含宽', wk['盈提示'].str.contains('宽', na=False), ''),
    ('含连3', wk['盈提示'].str.contains('连3', na=False), ''),
    ('含连4', wk['盈提示'].str.contains('连4', na=False), ''),
    ('含连5', wk['盈提示'].str.contains('连5', na=False), ''),
    ('宽高', wk['盈提示'] == '宽高', ''),
    ('宽高连3', wk['盈提示'] == '宽高连3', ''),
    ('宽高连4', wk['盈提示'] == '宽高连4', ''),
    ('宽高连5', wk['盈提示'] == '宽高连5', ''),
    ('空', wk['盈提示'].isna() | (wk['盈提示'] == ''), ''),
    ('宽(含高)', wk['盈提示'].str.contains('宽', na=False) & ~wk['盈提示'].str.contains('高', na=False), '宽不含高'),
]
out = print_table('6. 盈提示全量P3', items, label_width=14)
print(out)
output.append(out)

# ── 7. 最后一柱形态（§6.8全量重审） ──
# 条件定义（与原周最后一柱验证.py一致）
m_ly3 = wk['柱排周'].str.contains('升.尾连', na=False)
m_ly = wk['柱排周'].str.contains('升', na=False)
m_giant10 = wk['HR'] >= 10
m_giant20 = wk['HR'] >= 20
m_small = (wk['PR'].abs() < 2) & (wk['HR'] > 3)
m_cross = (wk['PR'].abs() < 0.5) & (wk['HR'] > 1)
m_long_shadow = (wk['HR'] - wk['PR'].abs()) > 3
m_lz = wk['波型'].str.contains('Aa龙猪|Fe震正|Fd震正', na=False)
m_shrink = m_ly3 & (wk['PR'] < wk['上周PR']) & (wk['PR'] > 0)
m_za_down = m_lz & (wk['ZA周'] < wk['上周ZA'])
m_swallow = wk['柱排周'].str.contains('吞吞', na=False)
m_ly3toD = m_ly3 & wk['下周柱排周'].str.contains('跌', na=False)

items = [
    ('连阳3+巨阳>20%', m_ly3 & m_giant20, '§6.8最强信号'),
    ('连阳3+巨阳>10%', m_ly3 & m_giant10, ''),
    ('连阳+长上影', m_ly & m_long_shadow, ''),
    ('连阳+长下影', m_ly & (wk['PR'] < 0) & (wk['HR'] > 3), ''),
    ('上影线小柱', m_small, ''),
    ('连阳后+上影线小柱', m_small & m_ly3, ''),
    ('连阳逐步缩小', m_shrink, ''),
    ('连阳3+续阳', m_ly3 & ~m_ly3toD, ''),
    ('连阳3+十字星', m_cross & m_ly3, ''),
    ('柱排含吞吞', m_swallow, ''),
    ('柱排含吞吞+跌', m_swallow & wk['柱排周'].str.contains('跌', na=False), ''),
    ('柱排含吞吞+升', m_swallow & wk['柱排周'].str.contains('升', na=False), ''),
    ('升排+长上影', m_lz & m_long_shadow, ''),
    ('升排+柱体缩小', m_lz & (wk['PR'] < wk['上周PR']) & (wk['PR'] > 0), ''),
    ('升排+ZA下降', m_za_down, ''),
]
out = print_table('7. 最后一柱形态全量P3（§6.8全量重审）', items, label_width=26)
print(out)
output.append(out)

# ── 8. 对比汇总（按下周P3降序） ──
all_items = [
    ('连阳3+巨阳>20%', m_ly3 & m_giant20, ''),
    ('连阳3+巨阳>10%', m_ly3 & m_giant10, ''),
    ('连阳+长上影', m_ly & m_long_shadow, ''),
    ('连阳+长下影', m_ly & (wk['PR'] < 0) & (wk['HR'] > 3), ''),
    ('上影线小柱', m_small, ''),
    ('连阳后+上影线小柱', m_small & m_ly3, ''),
    ('连阳逐步缩小', m_shrink, ''),
    ('连阳3+续阳', m_ly3 & ~m_ly3toD, ''),
    ('连阳3+十字星', m_cross & m_ly3, ''),
    ('柱排含吞吞', m_swallow, ''),
    ('Aa龙猪', wk['波型'].str.contains('Aa龙猪', na=False), ''),
    ('Fa震正〇', wk['波型'].str.contains('Fa震正〇', na=False), ''),
    ('升.尾反孕', wk['柱排周'].str.contains('升.尾反孕', na=False), ''),
    ('跌.尾吞', wk['柱排周'].str.contains('跌.尾吞', na=False), ''),
    ('金升', wk['WXCD'].str.contains('金升', na=False), ''),
    ('屎降', wk['WXCD'].str.contains('屎降', na=False), ''),
    ('WXAB=甲', wk['WXAB'].str.contains('甲', na=False), ''),
    ('WXAB=丙', wk['WXAB'].str.contains('丙', na=False), ''),
    ('盈提示含高', wk['盈提示'].str.contains('高', na=False), ''),
    ('盈提示空', wk['盈提示'].isna() | (wk['盈提示'] == ''), ''),
]
results = []
for name, cond, note in all_items:
    p, n, s = rep(name, cond)
    if p is not None:
        results.append((p, name, n))

results.sort(key=lambda x: -x[0])
lines = ['\n' + '=' * 80,
         '8. 对比汇总（按下周P3降序）',
         '=' * 80,
         f'{"排序":>4s}  {"条件":<26s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 60]
for rank, (p, name, n) in enumerate(results, 1):
    diff = p - baseline
    lines.append(f'{rank:>4d}  {name:<26s}  {n:>8,d}  {p:>6.1f}%  {diff:>+7.1f}pp')
lines.append('')
out = '\n'.join(lines)
print(out)
output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9_周微观指标P3.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')