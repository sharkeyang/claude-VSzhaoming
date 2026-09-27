# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：下破 DJA 后的"恢复质量"——恢复≠没跌
=====================================================
用户质疑：下破 DJA 20日恢复 98%，但恢复过程可能已下跌很多，或拉低 DJA。
所以"恢复"不等于"没亏"。需要看：
1. 下破 DJA 后，恢复过程中的最大回撤（跌了多少才恢复）
2. 恢复所需天数（多久才恢复）
3. 恢复后 vs 下破前的位置（是否回到原位）

列映射：
  [1] 收
  [13] 日ZA
  [14] 日ZC
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_恢复质量.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_close = 1
i_za = 13
i_zc = 14

# 统计：下破 DJA 后
# 1. 最大回撤（下破后未来20日内最低收盘 vs 下破前收盘）
# 2. 恢复天数（重新站上 DJA 所需天数）
# 3. 恢复后位置（恢复当天收盘 vs 下破前收盘）
stats = defaultdict(list)

files_done = 0
for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            header = next(r)
            rows = []
            for row in r:
                if len(row) <= max(i_close, i_za, i_zc):
                    continue
                try:
                    close = float(row[i_close])
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                except (ValueError, IndexError):
                    continue
                rows.append((close, za, zc))

            n = len(rows)
            for i in range(1, n):
                close, za, zc = rows[i]
                prev_close, prev_za, prev_zc = rows[i-1]
                # 首下破 DJA（前一日 ZA>0，今日 ZA<0）
                if prev_za > 0 and za < 0:
                    # 下破前收盘 = prev_close
                    base = prev_close
                    # 未来20日内
                    max_drawdown = 0  # 最大回撤（相对下破前）
                    min_close = base
                    recover_day = None
                    for j in range(i, min(i+21, n)):
                        c = rows[j][0]
                        if c < min_close:
                            min_close = c
                        # 恢复 = 重新站上 DJA（ZA>0）
                        if rows[j][1] > 0 and recover_day is None:
                            recover_day = j - i + 1
                            # 恢复当天收盘
                            recover_close = c
                    # 最大回撤
                    max_drawdown = (min_close - base) / base * 100
                    stats['下破DJA_最大回撤'].append(max_drawdown)
                    if recover_day is not None:
                        stats['下破DJA_恢复天数'].append(recover_day)
                        # 恢复后位置（恢复当天 vs 下破前）
                        recover_pos = (recover_close - base) / base * 100
                        stats['下破DJA_恢复后位置'].append(recover_pos)
                    else:
                        stats['下破DJA_未恢复'].append(1)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('下破 DJA 后的"恢复质量"（恢复≠没跌）')
out('=' * 100)
out('')
out('下破 DJA = 前一日 ZA>0，今日 ZA<0（首下破）')
out('')

# 最大回撤
dd = np.array(stats['下破DJA_最大回撤'])
out(f'下破 DJA 后 20 日内最大回撤（相对下破前收盘）：')
out(f'  样本: {len(dd):,}')
out(f'  平均最大回撤: {np.mean(dd):.2f}%')
out(f'  中位最大回撤: {np.median(dd):.2f}%')
out(f'  P25: {np.percentile(dd,25):.2f}%  P75: {np.percentile(dd,75):.2f}%')
out(f'  最大回撤≥5% 比例: {(dd<=-5).sum()/len(dd)*100:.1f}%')
out(f'  最大回撤≥10% 比例: {(dd<=-10).sum()/len(dd)*100:.1f}%')
out('')

# 恢复天数
rd = np.array(stats['下破DJA_恢复天数'])
out(f'下破 DJA 后恢复（重新站上 DJA）所需天数：')
out(f'  样本: {len(rd):,}')
out(f'  平均恢复天数: {np.mean(rd):.1f} 天')
out(f'  中位恢复天数: {np.median(rd):.0f} 天')
out(f'  1日内恢复: {(rd<=1).sum()/len(rd)*100:.1f}%')
out(f'  3日内恢复: {(rd<=3).sum()/len(rd)*100:.1f}%')
out(f'  5日内恢复: {(rd<=5).sum()/len(rd)*100:.1f}%')
out(f'  10日内恢复: {(rd<=10).sum()/len(rd)*100:.1f}%')
out('')

# 恢复后位置
rp = np.array(stats['下破DJA_恢复后位置'])
out(f'下破 DJA 后恢复当天 vs 下破前收盘：')
out(f'  样本: {len(rp):,}')
out(f'  平均恢复后位置: {np.mean(rp):.2f}%')
out(f'  中位恢复后位置: {np.median(rp):.2f}%')
out(f'  恢复后仍低于下破前(负): {(rp<0).sum()/len(rp)*100:.1f}%')
out(f'  恢复后回到下破前(≥0): {(rp>=0).sum()/len(rp)*100:.1f}%')
out('')

out('=' * 100)
out('关键洞察')
out('=' * 100)
out('')
out('恢复概率 98% 只说明"最终站上 DJA"，但：')
out(f'  平均最大回撤 {np.mean(dd):.2f}%——下破过程可能已跌 {np.mean(dd):.2f}%')
out(f'  平均恢复天数 {np.mean(rd):.1f} 天——需 {np.mean(rd):.1f} 天才恢复')
out(f'  恢复后仍低于下破前 {(rp<0).sum()/len(rp)*100:.1f}%——恢复≠回到原位')
out('')

OUTF.close()
print('Done')