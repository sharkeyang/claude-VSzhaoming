# -*- coding: utf-8 -*-
"""
随机抽样工具 — 避免字母序偏倚
用法：from 随机抽样工具 import 随机取文件, 加载市板映射
"""
import os, glob, random, pandas as pd

# 市板映射（全局缓存）
_市板映射 = None
_市板dict = None

核心池板块 = {'Qic', 'Qim', 'Qit'}  # 高波池（已剔除Qin非成分股）
排除池板块 = {'Qd', 'Qe', 'Qif', 'Qst'}
板块说明 = {
    'Qd': '指数', 'Qe': '基金/ETF', 'Qst': 'ST/退市',
    'Qif': '沪深300', 'Qic': '中证500', 'Qim': '中证1000',
    'Qit': '中证2000', 'Qin': '中证非'
}

def 加载市板映射(path='____temp/市板映射.csv'):
    """加载市板映射表，返回 (映射dict, 全部分布)"""
    global _市板映射, _市板dict
    sb = pd.read_csv(path, encoding='utf-8')
    sb['CIDL'] = sb['CIDL'].astype(str).str.strip()
    _市板映射 = sb
    _市板dict = dict(zip(sb['CIDL'], sb['市板']))
    return _市板dict, sb['市板'].value_counts()

def 随机取文件(n=500, data_dir='昭明算展/谕组日', seed=42, verbose=True):
    """随机取 n 个谕组日文件，返回文件路径列表及分布统计"""
    if _市板dict is None:
        加载市板映射()

    files = sorted(glob.glob(os.path.join(data_dir, '谕组日_*.csv')))
    random.seed(seed)
    random.shuffle(files)
    selected = files[:n]

    # 统计市板分布
    cidl_list = [os.path.basename(f).replace('谕组日_', '').replace('.csv', '') for f in selected]
    市板列 = [_市板dict.get(c, '未知') for c in cidl_list]
    核心数 = sum(1 for s in 市板列 if s in 核心池板块)
    排除数 = sum(1 for s in 市板列 if s in 排除池板块)

    if verbose:
        from collections import Counter
        dist = Counter(市板列)
        print(f"随机取 {n} 个文件:", flush=True)
        for k, v in sorted(dist.items(), key=lambda x: -x[1]):
            print(f"  {k} ({板块说明.get(k, '未知')}): {v} 文件 ({v/len(selected)*100:.1f}%)", flush=True)
        print(f"  核心池: {核心数} 文件 ({核心数/len(selected)*100:.1f}%), 排除池: {排除数} 文件 ({排除数/len(selected)*100:.1f}%)", flush=True)

    return selected, 市板列

def 文件池分布(files):
    """统计给定文件列表的市板分布"""
    if _市板dict is None:
        加载市板映射()
    cidl_list = [os.path.basename(f).replace('谕组日_', '').replace('.csv', '') for f in files]
    from collections import Counter
    return Counter(_市板dict.get(c, '未知') for c in cidl_list)

def 是核心池(cidl):
    """判断CIDL是否属于核心池"""
    if _市板dict is None:
        加载市板映射()
    return _市板dict.get(cidl, '') in 核心池板块

if __name__ == '__main__':
    # 测试
    加载市板映射()
    随机取文件(500)
    print(f"\n总共 {len(glob.glob('昭明算展/谕组日/谕组日_*.csv'))} 个文件")