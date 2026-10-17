# -*- coding: utf-8 -*-
"""
退出条件框架验证（2026-10-15 新数据 63列）
====================================================
用户框架（WXZC>0 主要操作范围）：
  退出条件三类：
    ①下破WXZC<0 = 强制退出（形成禁土+跌连高发，难退出）
    ②WXZC>0形成虎 = 提前退出（即将下破WXZC<0）
    ③WXZC>0雀+沿WJA跌连 = 截断亏损
  禁止操作条件 = 下破WXZB<0才考虑退出
  不应是：WJA之上跌连、下破WJA、下破WJA两柱（不是必须退出，可能下周冲高）

列索引：主期[0] 周涨[1] HR[3] 护型[4] ZB周[17] ZC周[18] AB周[22] 并符串周[51]
护级(index3)：上=收盘价>WJA, 中=收盘价>WJB, 下=其他, 忐=收盘价>WJB(AB<0), 忠=收盘价>WJA(AB<0), 忑=其他(AB<0)
"""
import csv, glob, io, sys, os, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_退出条件验证_result.txt'

C_周涨, C_HR, C_HX, C_ZB, C_ZC, C_AB, C_并符, C_主期 = 1, 3, 4, 17, 18, 22, 51, 0

def 四波(ab, zb):
    if ab > 0 and zb > 0: return '龙'
    if ab < 0 and zb > 0: return '武'
    if ab < 0 and zb < 0: return '虎'
    if ab > 0 and zb < 0: return '雀'
    return '?'

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

# 逐股加载
by_code = defaultdict(list)
files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

for fi, fp in enumerate(files):
    code = fp.split('_')[-1].replace('.csv', '')
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) <= C_并符: continue
            try:
                涨 = float(row[C_周涨].strip() or 0)
                hr = float(row[C_HR].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            hx = row[C_HX].strip()
            护级 = hx[3] if len(hx) >= 4 else '?'
            tail = row[C_并符].strip()[-1] if row[C_并符].strip() else ''
            by_code[code].append({
                'date': parse_date(row[C_主期].strip()),
                '涨': 涨, 'hr': hr, 'zb': zb, 'zc': zc, 'ab': ab,
                '护级': 护级, 'tail': tail,
            })
    if fi % 1000 == 0 and fi > 0:
        print(f'  已加载 {fi}/{len(files)}', flush=True)

# 分析函数：对满足条件的柱，统计未来1/2/4周累计涨幅 + 下周冲高率
def 分析(条件名, 条件函数):
    """条件函数(rows, i) -> bool，判断第i柱是否满足条件"""
    stats = {'n': 0, 'fut1': [], 'fut2': [], 'fut4': [], 'next_ge3': 0, 'next_gt0': 0}
    for code, lst in by_code.items():
        lst.sort(key=lambda x: x['date'])
        for i in range(len(lst)):
            if 条件函数(lst, i):
                stats['n'] += 1
                if i+1 < len(lst):
                    stats['fut1'].append(lst[i+1]['涨'])
                    if lst[i+1]['hr'] >= 3.0: stats['next_ge3'] += 1
                    if lst[i+1]['涨'] > 0: stats['next_gt0'] += 1
                if i+2 < len(lst):
                    stats['fut2'].append(lst[i+1]['涨'] + lst[i+2]['涨'])
                if i+4 < len(lst):
                    stats['fut4'].append(sum(lst[i+1+j]['涨'] for j in range(4)))
    return stats

def 打印(名, s):
    n = s['n']
    if n == 0:
        lines.append(f'  {名:<28} n=0')
        return
    f1 = sum(s['fut1'])/len(s['fut1']) if s['fut1'] else 0
    f2 = sum(s['fut2'])/len(s['fut2']) if s['fut2'] else 0
    f4 = sum(s['fut4'])/len(s['fut4']) if s['fut4'] else 0
    nxt3 = s['next_ge3']/n*100
    nxt0 = s['next_gt0']/n*100
    lines.append(f'  {名:<28} n={n:>8,}  下周均涨={f1:+.3f}%  2周={f2:+.3f}%  4周={f4:+.3f}%  下周≥3%={nxt3:5.1f}%  下周涨>0={nxt0:5.1f}%')

lines = []
lines.append('=' * 80)
lines.append('退出条件框架验证（2026-10-15 新数据 3449文件）')
lines.append('=' * 80)
lines.append('')

# ============ 1. 三类退出条件 ============
lines.append('=' * 80)
lines.append('1. 三类退出条件（WXZC>0 主要操作范围）')
lines.append('=' * 80)
lines.append('')

# ① 下破WXZC<0（强制退出）：本周ZC>0，下周ZC<0
def 下破ZC(lst, i):
    return i+1 < len(lst) and lst[i]['zc'] > 0 and lst[i+1]['zc'] < 0
s = 分析('①下破WXZC<0', 下破ZC)
打印('①下破WXZC<0(强制退出)', s)
lines.append('')

# ② WXZC>0形成虎（提前退出）：本周ZC>0且四波=虎
def 形成虎(lst, i):
    return lst[i]['zc'] > 0 and 四波(lst[i]['ab'], lst[i]['zb']) == '虎'
s = 分析('②ZC>0形成虎(提前退出)', 形成虎)
打印('②ZC>0形成虎(提前退出)', s)
lines.append('')

# ③ WXZC>0雀+跌连（截断亏损）：本周ZC>0且四波=雀且跌连
def 雀跌连(lst, i):
    return lst[i]['zc'] > 0 and 四波(lst[i]['ab'], lst[i]['zb']) == '雀' and lst[i]['tail'] == 'W'
s = 分析('③ZC>0雀+跌连(截断亏损)', 雀跌连)
打印('③ZC>0雀+跌连(截断亏损)', s)
lines.append('')

# ============ 2. 对比：不应作为禁止操作的条件 ============
lines.append('=' * 80)
lines.append('2. 对比：不应作为禁止操作的条件（可能下周冲高）')
lines.append('=' * 80)
lines.append('')

# WJA之上跌连：护级=上 且 跌连
def WJA上跌连(lst, i):
    return lst[i]['护级'] == '上' and lst[i]['tail'] == 'W'
s = 分析('WJA之上跌连', WJA上跌连)
打印('WJA之上跌连', s)
lines.append('')

# 下破WJA：护级从'上'变为非'上'
def 下破WJA(lst, i):
    return i > 0 and lst[i-1]['护级'] == '上' and lst[i]['护级'] != '上'
s = 分析('下破WJA', 下破WJA)
打印('下破WJA', s)
lines.append('')

# 下破WJA两柱：连续两柱护级非'上'
def 下破WJA两柱(lst, i):
    return i > 0 and lst[i-1]['护级'] != '上' and lst[i]['护级'] != '上'
s = 分析('下破WJA两柱', 下破WJA两柱)
打印('下破WJA两柱', s)
lines.append('')

# ============ 3. 参考：WXZC>0 龙/武 正常持有 ============
lines.append('=' * 80)
lines.append('3. 参考：WXZC>0 龙/武 正常持有')
lines.append('=' * 80)
lines.append('')
def ZC0龙(lst, i):
    return lst[i]['zc'] > 0 and 四波(lst[i]['ab'], lst[i]['zb']) == '龙'
s = 分析('ZC>0龙(正常持有)', ZC0龙)
打印('ZC>0龙(正常持有)', s)
lines.append('')
def ZC0武(lst, i):
    return lst[i]['zc'] > 0 and 四波(lst[i]['ab'], lst[i]['zb']) == '武'
s = 分析('ZC>0武(正常持有)', ZC0武)
打印('ZC>0武(正常持有)', s)
lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)