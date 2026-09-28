path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

repl = [
    # §1.2 锚点错误：指向实际章节 3.3.0
    ('（见 [二、各护型介入点](#二各护型介入点dxzc0融合-c6-564) 的「⑤.1 乙(ZA<0) 的细化」：深跌+升排是超卖反弹',
     '（见 §3.3.0 乙(ZA<0) 的细化：深跌+升排是超卖反弹'),
    # §6.1.4 介入时机指向 §6.6（退时机）→ 应为 §6.5（进时机）
    ('第3层 · 介入时机（§6.6，DJA丘等1/2/3 + BSHA5）', '第3层 · 介入时机（§6.5，DJA丘等1/2/3 + BSHA5）'),
]
changed = 0
for old, new in repl:
    if old in content:
        content = content.replace(old, new)
        changed += 1
print(f'修正 {changed} 处')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
