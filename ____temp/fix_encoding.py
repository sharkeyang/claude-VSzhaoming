# -*- coding: utf-8 -*-
"""修复编码错误"""
with open('_主文档/MC3.1_研究月基策略.md', 'rb') as f:
    data = f.read()

# 查找并替换错误的路径编码
old = b'`\\\\xe6\\\\x98\\\\xad\\\\xe6\\\\x98\\\\x8e\\\\xe7\\\\xae\\\\x97\\\\xe5\\\\xb1\\\\x95\\\\\\\\xe8\\\\xb0\\\\x95\\\\xe7\\\\xbb\\\\x84\\\\xe5\\\\x91\\\\xa8\\\\\\\\`'
new = b'`\xe6\x98\xad\xe6\x98\x8e\xe7\xae\x97\xe5\xb1\x95\\\xe8\xb0\x95\xe7\xbb\x84\xe5\x91\xa8\\`'

if old in data:
    data = data.replace(old, new)
    with open('_主文档/MC3.1_研究月基策略.md', 'wb') as f:
        f.write(data)
    print('修复成功')
else:
    print('未找到匹配')
    # 尝试其他可能的编码
    # 查找包含 昭明算展 的片段
    idx = data.find(b'\xe6\x98\xad\xe6\x98\x8e\xe7\xae\x97\xe5\xb1\x95')
    if idx >= 0:
        print(f'找到昭明算展 at pos {idx}')
        print(data[idx-10:idx+50])