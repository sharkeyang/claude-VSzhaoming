# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 测试仓日类校验
pat1 = re.compile(r'^[一-鿿][a-zA-Z]')
pat2 = re.compile(r'^[一-鿿][a-zA-Z]')
pat3 = re.compile(r'^[^\x00-\x7f][a-zA-Z]')  # 首字符非ASCII
for v in ['禁忑y', '念中z', '肋忠a', '上b', '忐a', '禁下y']:
    print(f'{v}: pat1={bool(pat1.match(v))} pat2={bool(pat2.match(v))} pat3={bool(pat3.match(v))}')
