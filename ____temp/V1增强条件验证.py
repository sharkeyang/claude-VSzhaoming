# -*- coding: utf-8 -*-
"""
验证 V1 必赢基础上叠加额外条件的增强效果
===========================================
- 基础条件：ZE>0+ZC>0（V1必赢）
- 增强条件：ZA>0、甲乙己、升排、合顶 及其组合
- 均线价进出，持有到条件不满足
- 高波池 Qic+Qim+Qit
"""
import csv, os, json, io
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_V1增强条件验证.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
好护型 = {'甲','乙','己'}

files_done = 0

# 各策略的持有期收益列表
策略 = {
    '基础(ZE>0+ZC>0)': [],
    '+ZA>0': [],
    '+甲乙己': [],
    '+升排': [],
    '+合顶': [],
    '+ZA+AB': [],
    '+ZA+AB+升排': [],
    '+ZA+AB+合顶': [],
    '全条件': [],
}

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
            idx_close = header.index('收')
            idx_zc = header.index('日ZC')
            idx_ze = header.index('日ZE')
            idx_za = header.index('日ZA')
            idx_dxab = header.index('DXAB')
            idx_柱排 = header.index('柱排')
            idx_顶型 = header.index('顶型')

            prices = []
            zcs = []; zes = []; zas = []
            dxabs = []; 柱排s = []; 顶型s = []
            for row in r:
                if len(row) <= max(idx_close, idx_zc, idx_ze, idx_za, idx_dxab, idx_柱排, idx_顶型):
                    continue
                try:
                    close = float(row[idx_close])
                    zc = float(row[idx_zc])
                    ze = float(row[idx_ze])
                    za = float(row[idx_za])
                except (ValueError, IndexError):
                    continue
                prices.append(close)
                zcs.append(zc); zes.append(ze); zas.append(za)
                dxabs.append(row[idx_dxab])
                柱排s.append(row[idx_柱排])
                顶型s.append(row[idx_顶型])

            if len(prices) < 5:
                continue

            # 逐行判断各条件
            for i in range(len(prices)):
                cond_ze = zes[i] > 0
                cond_zc = zcs[i] > 0
                cond_za = zas[i] > 0
                # 甲乙己
                hx = HX_MAP.get(dxabs[i][0]) if len(dxabs[i]) > 0 else ''
                cond_ab = hx in 好护型
                # 升排
                cond_升排 = 柱排s[i].startswith('升') or '(升' in 柱排s[i]
                # 合顶
                cond_合顶 = 顶型s[i] != '' and 顶型s[i] != '0' and '未赋值' not in 顶型s[i]

                # 基础条件
                if cond_ze and cond_zc:
                    策略['基础(ZE>0+ZC>0)'].append((i, prices[i]))

                # +ZA>0
                if cond_ze and cond_zc and cond_za:
                    策略['+ZA>0'].append((i, prices[i]))

                # +甲乙己
                if cond_ze and cond_zc and cond_ab:
                    策略['+甲乙己'].append((i, prices[i]))

                # +升排
                if cond_ze and cond_zc and cond_升排:
                    策略['+升排'].append((i, prices[i]))

                # +合顶
                if cond_ze and cond_zc and cond_合顶:
                    策略['+合顶'].append((i, prices[i]))

                # +ZA+AB
                if cond_ze and cond_zc and cond_za and cond_ab:
                    策略['+ZA+AB'].append((i, prices[i]))

                # +ZA+AB+升排
                if cond_ze and cond_zc and cond_za and cond_ab and cond_升排:
                    策略['+ZA+AB+升排'].append((i, prices[i]))

                # +ZA+AB+合顶
                if cond_ze and cond_zc and cond_za and cond_ab and cond_合顶:
                    策略['+ZA+AB+合顶'].append((i, prices[i]))

                # 全条件
                if cond_ze and cond_zc and cond_za and cond_ab and cond_升排 and cond_合顶:
                    策略['全条件'].append((i, prices[i]))

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('V1必赢 + 增强条件 样本量统计')
out('=' * 100)
out('')
out(f'| {"条件":<30s} | {"样本数":>10s} | {"占比":>8s} |')
out(f'|{"":->30s}|{"":->10s}:|{"":->8s}:|')
for label in ['基础(ZE>0+ZC>0)', '+ZA>0', '+甲乙己', '+升排', '+合顶', '+ZA+AB', '+ZA+AB+升排', '+ZA+AB+合顶', '全条件']:
    n = len(策略[label])
    base_n = len(策略['基础(ZE>0+ZC>0)'])
    pct = n/base_n*100 if base_n > 0 else 0
    out(f'| {label:<30s} | {n:>10,d} | {pct:>7.1f}% |')

OUTF.close()
print('Done')