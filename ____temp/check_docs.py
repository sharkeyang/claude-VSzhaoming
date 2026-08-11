# -*- coding: utf-8 -*-
"""检查各文档中需要更新的分类引用"""
import os, re

docs = ['MC3.2_研究周冲策略.md', 'MC3.3.2_研究日级别探索路径.md', 'MC3.3.5_等高线分类分析.md',
        '全局_A盯盘警示卡.md', '全局_B交易体系.md', '全局_C昭明路线图.md', '昭明计划大局观体系.md']

with open('____temp/check_docs_result.txt', 'w', encoding='utf-8') as out:
    for doc in docs:
        path = f'_主文档/{doc}'
        if not os.path.exists(path):
            out.write(f'{doc}: 文件不存在\n')
            continue
        text = open(path, encoding='utf-8').read()
        keywords = ['A级','B级','C级','D级','E级','F级','G级','H级','S级','禁止级',
                    '牢牢抓住','可持仓','仅观察','坚决禁止','主动持仓','被动持有','试仓','8格','四层']
        hits = []
        for i, line in enumerate(text.split('\n'), 1):
            for kw in keywords:
                if kw in line:
                    hits.append((i, kw, line.strip()[:80]))
                    break
        if hits:
            out.write(f'\n{doc}:\n')
            for line_no, kw, content in hits:
                out.write(f'  L{line_no} [{kw}]: {content}\n')
        else:
            out.write(f'{doc}: 无相关引用\n')

print('Done')