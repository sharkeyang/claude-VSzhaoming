with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Find the first occurrence of the target text
target_before = '| 内存 | 项目记忆 | '
target_after = ' |\n\n---\n\n## 附录二 启动资产基线'

idx = c.find(target_before)
if idx >= 0:
    # Find the specific pattern after this
    pattern_end = c.find('\n\n---\n\n## 附录二 启动资产基线', idx)
    if pattern_end >= 0:
        full_pattern = c[idx:pattern_end + len('\n\n---\n\n## 附录二 启动资产基线')]
        # Remove only this occurrence
        c = c.replace(full_pattern, c[idx:pattern_end], 1)
        print('Fixed')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)