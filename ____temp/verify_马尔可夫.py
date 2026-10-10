# -*- coding: utf-8 -*-
"""马尔可夫链分析：护型转移矩阵、稳态分布、首达时间
数据：谕组周 CSV，GBK编码
列：护型[4](a甲/b乙/c丙/z丁/y戊/r己)
"""
import sys, csv, glob
from collections import defaultdict
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

def huxing(hx):
    if not hx: return '?'
    c = hx[0]
    m = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
    return m.get(c, '?')

# 护型转移计数
trans = defaultdict(lambda: defaultdict(int))
huxing_cnt = defaultdict(int)
n = 0

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)-1):
        cur = huxing(rows[i][4])
        nxt = huxing(rows[i+1][4])
        if cur in '甲乙丙丁戊己' and nxt in '甲乙丙丁戊己':
            trans[cur][nxt] += 1
            huxing_cnt[cur] += 1
            n += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

states = ['甲','乙','丙','丁','戊','己']
print(f'\n=== 样本数: {n} ===')

# 转移概率矩阵 P
print(f'\n=== 护型转移概率矩阵 P（行=当前，列=下周）===')
print('当前\\下周'.ljust(6) + ''.join(f'{s:>8}' for s in states))
P = np.zeros((6,6))
for i, cur in enumerate(states):
    row = []
    for j, nxt in enumerate(states):
        p = trans[cur][nxt] / huxing_cnt[cur] if huxing_cnt[cur] else 0
        P[i][j] = p
        row.append(f'{p*100:>7.1f}%')
    print(f'{cur:<6}' + ''.join(row))

# 稳态分布：π = πP，即 P^T 的特征向量（特征值1）
print(f'\n=== 稳态分布（长期各护型占比）===')
eigvals, eigvecs = np.linalg.eig(P.T)
idx = np.argmin(np.abs(eigvals - 1))
pi = np.real(eigvecs[:, idx])
pi = pi / pi.sum()
for i, s in enumerate(states):
    print(f'  {s}: {pi[i]*100:.2f}%')

# 首达时间：从各状态到"甲"的期望周数
# 用吸收马尔可夫链：把"甲"作为吸收态
print(f'\n=== 首达时间（从各护型到"甲"的期望周数）===')
# 去掉甲，构建 Q（非吸收态间转移）
non_absorb = ['乙','丙','丁','戊','己']
Q = np.zeros((5,5))
for i, cur in enumerate(non_absorb):
    for j, nxt in enumerate(non_absorb):
        Q[i][j] = P[states.index(cur)][states.index(nxt)]
# 基本矩阵 N = (I-Q)^-1
N = np.linalg.inv(np.eye(5) - Q)
# 首达时间 = N @ 1（从各非吸收态到吸收态甲的期望步数）
t = N @ np.ones(5)
for i, s in enumerate(non_absorb):
    print(f'  {s} → 甲: {t[i]:.2f} 周')

# 吸收概率：从各状态最终到甲的概率
print(f'\n=== 吸收概率（从各护型最终到"甲"的概率）===')
# R = 非吸收态到吸收态(甲)的转移
R = np.zeros((5,1))
for i, cur in enumerate(non_absorb):
    R[i][0] = P[states.index(cur)][states.index('甲')]
B = N @ R  # 吸收概率
for i, s in enumerate(non_absorb):
    print(f'  {s} → 甲: {B[i][0]*100:.2f}%')