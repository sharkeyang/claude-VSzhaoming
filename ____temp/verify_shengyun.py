# -*- coding: utf-8 -*-
import csv, glob
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 修正判定: 末位C(鼎正) + 柱排含"孕" = 升孕
# 对比旧判定: startswith('升')且含孕
r = defaultdict(lambda:[0,0,0])  # (护型, 判定法, 类别) -> [样本, 下破, 冲高]

def zhu_dir_class(zhu):
    if zhu.startswith('升'):
        return '升排'
    if zhu.startswith('跌'):
        if '吞' in zhu:
            return '跌吞'
        return '跌排'
    if zhu.startswith('(升)'):
        return '(升)人'
    if zhu.startswith('(跌)'):
        return '(跌)人'
    if zhu.startswith('(人)'):
        return '(人)人'
    return '其他:'+zhu[:4]

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        nxt = rows[i+1]
        cur_hx = row[9][0]
        deng = row[44]
        if cur_hx in ('a','b','r') and deng == '等2':
            zhong = row[33]
            mo = zhong[-1] if zhong else '?'
            zhu = row[10]
            if mo != 'C': continue
            try:
                next_hr_f = float(nxt[26])
                next_za = int(nxt[13])
            except:
                continue
            # 宽判定: 含孕
            wide = '孕' in zhu
            # 窄判定(旧): 以升开头且含孕
            narrow = '孕' in zhu and zhu.startswith('升')
            # 柱排类
            zc = zhu_dir_class(zhu)
            for meth, flag in [('宽', wide), ('窄', narrow)]:
                cat = '升孕' if flag else '非升孕'
                r[(cur_hx, meth, cat)][0] += 1
                if next_za < 0: r[(cur_hx, meth, cat)][1] += 1
                if next_hr_f > 3: r[(cur_hx, meth, cat)][2] += 1
            # 记录柱排构成
            r[(cur_hx, '柱排构成', zc)][0] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己'}
print('总文件:', n)
print('\n=== 等2+末位C: 宽判定(含孕) vs 窄判定(升开头含孕) ===')
for hx in ['a','b','r']:
    print(f'--- {HX[hx]} ---')
    for meth in ['宽','窄']:
        for cat in ['升孕','非升孕']:
            tot, brk, hit = r[(hx,meth,cat)]
            if tot == 0: continue
            print(f"  {meth}判定 {cat:<4}: 样本{tot:>8} 下破{brk:>7} P={brk/tot*100:.2f}% 冲高{hit:>7} P={hit/tot*100:.2f}%")

print('\n=== 等2+末位C 的柱排构成 ===')
for hx in ['a','b','r']:
    print(f'--- {HX[hx]} ---')
    for zc, (tot, brk, hit) in sorted(r[(hx,'柱排构成','')].items() if False else []) :
        pass
# 重新打印柱排构成
for hx in ['a','b','r']:
    print(f'--- {HX[hx]} ---')
    items = [(k[2], v) for k, v in r.items() if k[0]==hx and k[1]=='柱排构成']
    for zc, (tot, brk, hit) in sorted(items, key=lambda x:-x[1][0]):
        print(f"  {zc:<14}: 样本{tot:>8}")
