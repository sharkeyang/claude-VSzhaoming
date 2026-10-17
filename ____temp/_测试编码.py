# -*- coding: utf-8 -*-
import re
out = []
chars = ['禁', '念', '肋', '上', '忐', '一', '鿿']
for c in chars:
    out.append(f'{c}: U+{ord(c):04X}')
pat = re.compile(r'^[一-鿿][a-zA-Z]')
for v in ['禁忑y', '念中z', '肋忠a', '上b', '忐a']:
    out.append(f'{v}: {bool(pat.match(v))}')
with open('____temp/_编码结果.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
