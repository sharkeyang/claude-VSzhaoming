# -*- coding: utf-8 -*-
"""
四波×四土 最佳机会证明 + 升连集中性研究（2026-10-15 新数据 63列）
====================================================
数据源：昭明算展/谕组周/（3449文件，GBK编码）
权威元数据：_产出物/_工具/元数据_vba数据映射_周类.md（63列）

列索引（新63列）：
    主期[0] 周涨[1] PR[2] HR[3] 护型[4] 地型[5] 等周[6] 波型[7] 柱排周[8] 大局[9]
    ZA周[16] ZB周[17] ZC周[18] ZD周[19] ZE周[20] ZF周[21]
    AB周[22] AC周[23] BC周[24] AD周[25] BD周[26] CD周[27]
    并符串周[51]（升连=尾字符Q）

四波（WXAB×WXZB，C7 §8.6.2）：
    升主(龙)=AB>0且ZB>0, 降转(武)=AB<0且ZB>0, 降主(虎)=AB<0且ZB<0, 升转(雀)=AB>0且ZB<0
四土（WXZC×WXAB护级，C7 §6.2.1.9.1）：
    沃土=ZC>0+护级上/忐, 鸡肋土=ZC<0+忠, 执念土=ZC>0+中/下/忑, 禁土=ZC<0+下/忑
升连：并符串周[51] 尾字符=Q
"""
import csv, glob, io, sys, os, collections
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四波四土升连_result.txt'

# 列索引
C_HR, C_HX, C_ZB, C_ZC, C_AB = 3, 4, 17, 18, 22
C_并符 = 51

def 四波(ab, zb):
    if ab > 0 and zb > 0: return '升主(龙)'
    if ab < 0 and zb > 0: return '降转(武)'
    if ab < 0 and zb < 0: return '降主(虎)'
    if ab > 0 and zb < 0: return '升转(雀)'
    return '?'

def 四土(zc, 护级):
    # 周类四类区域全集划分（C7 §6.2.1.9，2026-10-07 用户定稿）
    # 沃土(2格): ZC>0 + 上/忐
    # 执念土(4格): (中,无论ZC) + (ZC>0 + 下/忑)
    # 鸡肋土(4格): (忠,无论ZC) + (ZC<0 + 上/忐)
    # 禁土(2格): ZC<0 + 下/忑
    if 护级 == '忠': return '鸡肋土'          # 忠无论ZC
    if 护级 == '中': return '执念土'          # 中无论ZC
    if 护级 in ('上', '忐'):
        return '沃土' if zc > 0 else '鸡肋土'  # 上/忐: ZC>0=沃土, ZC<0=鸡肋土
    if 护级 in ('下', '忑'):
        return '禁土' if zc < 0 else '执念土'  # 下/忑: ZC<0=禁土, ZC>0=执念土
    return '?'

def 是升连(并符):
    return 并符 and 并符[-1] == 'Q'

# 统计：{四土×四波: {n, ge3, sum_hr, gt0, 升连数}}
stats = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'gt0': 0, '升连': 0})
# 全局升连总数（用于分布比例）
全局升连 = 0

files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

for fi, fp in enumerate(files):
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) <= C_并符: continue
            try:
                hr = float(row[C_HR].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            hx = row[C_HX].strip()
            护级 = hx[3] if len(hx) >= 4 else '?'  # 护型格式 a甲↗上2.A4，护级在第4字符(index3)
            sibo = 四波(ab, zb)
            tu = 四土(zc, 护级)
            key = f'{tu}×{sibo}'
            s = stats[key]
            s['n'] += 1
            s['sum_hr'] += hr
            if hr >= 3.0: s['ge3'] += 1
            if hr > 0: s['gt0'] += 1
            if 是升连(row[C_并符].strip()):
                s['升连'] += 1
                全局升连 += 1
    if fi % 1000 == 0 and fi > 0:
        print(f'  已处理 {fi}/{len(files)}', flush=True)

lines = []
lines.append('=' * 78)
lines.append('四波×四土 最佳机会证明 + 升连集中性研究（2026-10-15 新数据 3449文件）')
lines.append('=' * 78)
lines.append('')
lines.append('四波 = WXAB×WXZB：升主(龙)=AB>0且ZB>0, 降转(武)=AB<0且ZB>0, 降主(虎)=AB<0且ZB<0, 升转(雀)=AB>0且ZB<0')
lines.append('四土 = WXZC×WXAB护级：沃土=ZC>0+上/忐, 鸡肋土=ZC<0+忠, 执念土=ZC>0+中/下/忑, 禁土=ZC<0+下/忑')
lines.append('升连 = 并符串周尾字符Q')
lines.append('')

# ============ 第一部分：四波×四土 最佳机会证明 ============
lines.append('=' * 78)
lines.append('第一部分：四波×四土 最佳机会证明')
lines.append('=' * 78)
lines.append('')

def fmt(key, s):
    n = s['n']
    if n == 0: return f'{key:<22} n=0'
    return (f'{key:<22} n={n:>9,}  P(≥3%)={s["ge3"]/n*100:6.2f}%  '
            f'P(>0)={s["gt0"]/n*100:6.2f}%  均高幅={s["sum_hr"]/n:6.3f}%')

# 全量基线
全量 = {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'gt0': 0}
for s in stats.values():
    for k in ('n', 'ge3', 'gt0'):
        全量[k] += s[k]
    全量['sum_hr'] += s['sum_hr']
lines.append(fmt('全量基线', 全量))
lines.append('')

# 四土单独
lines.append('--- 四土单独（下周获利口径）---')
土汇总 = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'gt0': 0})
for key, s in stats.items():
    tu = key.split('×')[0]
    for k in ('n', 'ge3', 'gt0'):
        土汇总[tu][k] += s[k]
    土汇总[tu]['sum_hr'] += s['sum_hr']
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    lines.append(fmt(tu, 土汇总[tu]))
lines.append('')

# 四波单独
lines.append('--- 四波单独（下周获利口径）---')
波汇总 = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'gt0': 0})
for key, s in stats.items():
    sibo = key.split('×')[1]
    for k in ('n', 'ge3', 'gt0'):
        波汇总[sibo][k] += s[k]
    波汇总[sibo]['sum_hr'] += s['sum_hr']
for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
    lines.append(fmt(sibo, 波汇总[sibo]))
lines.append('')

# 四土×四波 交叉表（下周获利 + P(≥3%)）
lines.append('--- 四土×四波 交叉表（下周获利均高幅%）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["sum_hr"]/s["n"] if s["n"] else 0:>11.3f}%'
    lines.append(row)
lines.append('')

lines.append('--- 四土×四波 交叉表（P(≥3%)）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["ge3"]/s["n"]*100 if s["n"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

# 关键对比
lines.append('--- 关键对比 ---')
def p(key):
    s = stats[key]
    return s['ge3']/s['n']*100 if s['n'] else 0
def avg(key):
    s = stats[key]
    return s['sum_hr']/s['n'] if s['n'] else 0
lines.append(f'沃土×升主(龙): P(≥3%)={p("沃土×升主(龙)"):.2f}%  均高幅={avg("沃土×升主(龙)"):.3f}%  n={stats["沃土×升主(龙)"]["n"]:,}')
lines.append(f'沃土×降转(武): P(≥3%)={p("沃土×降转(武)"):.2f}%  均高幅={avg("沃土×降转(武)"):.3f}%  n={stats["沃土×降转(武)"]["n"]:,}')
lines.append(f'全量基线:      P(≥3%)={p("沃土×升主(龙)") if False else 全量["ge3"]/全量["n"]*100:.2f}%  均高幅={全量["sum_hr"]/全量["n"]:.3f}%')
lines.append('')

# ============ 第二部分：升连集中性研究 ============
lines.append('=' * 78)
lines.append('第二部分：升连在四波×四土区域的集中性')
lines.append('=' * 78)
lines.append('')
lines.append(f'全局升连总数: {全局升连:,}')
lines.append('')

# ① 升连存在比例（每格升连数/每格总样本）
lines.append('--- ① 升连存在比例（升连数/该格总样本）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        rate = s['升连']/s['n']*100 if s['n'] else 0
        row += f' {rate:>11.2f}%'
    lines.append(row)
lines.append('')

# ② 升连分布比例（每格升连数/全局升连总数）
lines.append('--- ② 升连分布比例（该格升连数/全局升连总数）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        rate = s['升连']/全局升连*100 if 全局升连 else 0
        row += f' {rate:>11.2f}%'
    lines.append(row)
lines.append('')

# ③ 升连在沃土×升主 的集中度（富集系数）
lines.append('--- ③ 升连富集系数（该格升连占比 / 该格样本占比）---')
lines.append('富集系数>1 = 升连在该格比平均更集中')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        if s['n'] and 全局升连:
            enrich = (s['升连']/全局升连) / (s['n']/全量['n'])
        else:
            enrich = 0
        row += f' {enrich:>11.2f}'
    lines.append(row)
lines.append('')

# ④ 沃土×升主 内部：升连 vs 非升连 的获利对比
lines.append('--- ④ 沃土×升主(龙) 内部：升连 vs 非升连 获利对比 ---')
for key in ['沃土×升主(龙)', '沃土×降转(武)']:
    s = stats[key]
    lines.append(f'{key}: 总样本={s["n"]:,}, 升连={s["升连"]:,} ({s["升连"]/s["n"]*100:.2f}%)')
lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)
