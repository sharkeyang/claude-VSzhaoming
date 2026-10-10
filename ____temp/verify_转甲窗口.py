# -*- coding: utf-8 -*-
"""有限时间窗口转甲概率：从各护型在N周内转甲的概率
数据：谕组周 CSV，GBK编码
列：护型[4](a甲/b乙/c丙/z丁/y戊/r己)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def huxing(hx):
    if not hx: return '?'
    c = hx[0]
    m = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
    return m.get(c, '?')

# 统计：从各护型在N周内(1/3/5/10周)转甲的概率
# 对每个样本，看未来N周内是否出现甲
stats = defaultdict(lambda: {'n':0, 'w1':0, 'w3':0, 'w5':0, 'w10':0})

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)):
        cur = huxing(rows[i][4])
        if cur not in '甲乙丙丁戊己': continue
        s = stats[cur]
        s['n'] += 1
        # 未来1/3/5/10周内是否出现甲
        for w, key in [(1,'w1'),(3,'w3'),(5,'w5'),(10,'w10')]:
            for j in range(i+1, min(i+1+w, len(rows))):
                if huxing(rows[j][4]) == '甲':
                    s[key] += 1
                    break
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 有限时间窗口转甲概率（从各护型在N周内转甲）===')
print(f'{"护型":<4}{"n":>10}{"1周内":>10}{"3周内":>10}{"5周内":>10}{"10周内":>10}')
for cur in '甲乙丙丁戊己':
    s = stats[cur]
    if s['n'] == 0: continue
    w1 = s['w1']/s['n']*100
    w3 = s['w3']/s['n']*100
    w5 = s['w5']/s['n']*100
    w10 = s['w10']/s['n']*100
    print(f'{cur:<4}{s["n"]:>10}{w1:>9.1f}%{w3:>9.1f}%{w5:>9.1f}%{w10:>9.1f}%')