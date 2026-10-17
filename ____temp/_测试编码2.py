# -*- coding: utf-8 -*-
import re
out = []
# 测试单个字符是否在 [一-鿿] 范围内
pat = re.compile(r'^[一-鿿]')
for c in ['禁', '念', '肋', '上', '忐', '一', '鿿', '中', '下', '忠', '忑']:
    out.append(f'{c}(U+{ord(c):04X}): {bool(pat.match(c))}')
# 测试用 一-鿿
pat2 = re.compile(r'^[一-鿿]')
out.append('--- 用 \\u4e00-\\u9fff ---')
for c in ['禁', '念', '肋', '上', '忐', '中', '下', '忠', '忑']:
    out.append(f'{c}(U+{ord(c):04X}): {bool(pat2.match(c))}')
with open('____temp/_编码结果2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
