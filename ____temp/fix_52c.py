import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 处理真正的操作规则内容（保留课题原文引用）
replacements = [
    ('等2内部按中符末位+柱排细分，操作规则：', '等2内部按中符末位+柱排细分，操作结论（第六章 §6.5.4 已定型）：'),
    ('**结论：操作规则优化可行，核心价值在风险管理**', '**结论：升管/跌管思维优化可行，核心价值在风险管理**'),
    ('> ✅ 用户操作规则可行，核心价值在风险管理', '> ✅ 用户升管/跌管思维可行，核心价值在风险管理'),
    ('**修正后的操作规则：**', '**修正后的操作结论：**'),
    ('**操作规则总纲（与§6.5定型操作规则统一）：**', '**操作结论总纲（与§6.7定型操作规则统一）：**'),
    ('操作规则总纲各环节均有数据支持', '操作结论总纲各环节均有数据支持'),
    ('柱与DJA三态理论 + 操作规则优化是第六章', '柱与DJA三态理论 + 升管/跌管思维是第六章'),
]
changed = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        changed += 1

print(f'替换 {changed} 处')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
