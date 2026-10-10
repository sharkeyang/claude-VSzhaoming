# -*- coding: utf-8 -*-
"""齐次性验证：护型转移概率是否随持续天数变化？
数据：谕组周 CSV，GBK编码
列：护型[4](a甲/b乙/c丙/z丁/y戊/r己)
持续天数：从数据序列计算（连续相同护型的周数），非护型字符串中的BTZC值
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def huxing(hx):
    if not hx: return '?'
    c = hx[0]
    m = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
    return m.get(c, '?')

# 按持续天数分层统计转移计数
# layer: 1-2周 / 3-5周 / 6-10周 / 11+周
trans_layer = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
huxing_cnt_layer = defaultdict(lambda: defaultdict(int))

def layer(d):
    if d <= 2: return '1-2周'
    if d <= 5: return '3-5周'
    if d <= 10: return '6-10周'
    return '11+周'

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    # 计算每行护型持续天数（连续相同护型的周数）
    for i in range(len(rows)):
        cur = huxing(rows[i][4])
        dur = 1
        j = i - 1
        while j >= 0 and huxing(rows[j][4]) == cur:
            dur += 1
            j -= 1
        rows[i] = rows[i] + [dur]
    for i in range(len(rows)-1):
        cur = huxing(rows[i][4])
        nxt = huxing(rows[i+1][4])
        if cur not in '甲乙丙丁戊己' or nxt not in '甲乙丙丁戊己': continue
        d = rows[i][-1]
        trans_layer[layer(d)][cur][nxt] += 1
        huxing_cnt_layer[layer(d)][cur] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

states = ['甲','乙','丙','丁','戊','己']
print(f'\n=== 持续天数分层的护型转移矩阵（行=当前，列=下周）===')
print(f'{"层":<8}{"当前":<4}' + ''.join(f'{s:>8}' for s in states))
for L in ['1-2周','3-5周','6-10周','11+周']:
    for cur in states:
        total = huxing_cnt_layer[L][cur]
        if total == 0: continue
        row = []
        for nxt in states:
            p = trans_layer[L][cur][nxt]/total*100 if total else 0
            row.append(f'{p:>7.1f}%')
        print(f'{L:<8}{cur:<4}' + ''.join(row))
    print()
