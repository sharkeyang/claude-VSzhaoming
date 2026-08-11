# -*- coding: utf-8 -*-
"""全面检查 _主文档 中需要更新的内容"""
import os, glob

# 旧名词列表
old_terms = [
    '牢牢抓住', '可持仓', '仅观察', '坚决禁止', 'S级', '禁止级',
    '试(试仓)', '屎(屎中捡豆)', '屎中捡豆',  # 旧层级
    '主(主动持仓)', '被(被动持有)',  # 需确认是否一致
]

# 新正确名词
new_terms = ['傻(傻吃屎豆)', '傻吃屎豆']

docs = glob.glob('_主文档/*.md')

with open('____temp/全文档检查.txt', 'w', encoding='utf-8') as out:
    for doc in sorted(docs):
        text = open(doc, encoding='utf-8').read()
        found = []
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            for term in old_terms:
                if term in line:
                    found.append((i, term, line.strip()[:80]))
                    break
        if found:
            out.write(f'\n{doc}:\n')
            for i, term, content in found:
                out.write(f'  L{i} [{term}]: {content}\n')
        else:
            out.write(f'{doc}: 无需更新\n')

print('Done')