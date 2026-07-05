import re

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Delete 附录三 后续衍生工作 (including 期货应用 section)
# Find from "## 附录三" to next "##"
old_app3 = c.find('## 附录三 后续衍生工作')
next_section = c.find('\n## ', old_app3 + 1)
if old_app3 >= 0 and next_section >= 0:
    c = c[:old_app3] + c[next_section:]
    print('附录三 deleted')

# 2. Rename 附录四 待完成零碎工作 → 第五章 待完成零碎工作
c = c.replace('## 附录四 待完成零碎工作', '## 第五章 待完成零碎工作')

# 3. Rename 附录五 专题讨论 → 第四章 专题讨论
c = c.replace('## 附录五 专题讨论', '## 第四章 专题讨论')

# 4. Fix sub-items in 第四章: promote ### 专题 to proper level
# 专题一/二/三 are currently ###, they should be proper sub-headings
# They're already ### under ## 第四章, which is correct

# 5. Fix #17 section heading
c = c.replace('**#17 期货板块轮动框架**', '### 17. 期货板块轮动框架')

# 6. Fix #14 section heading
c = c.replace('**#14 行程卡→小传转化**', '### 14. 行程卡→小传转化')

# 7. Fix #13 section heading
c = c.replace('**#13 VBA2python迁移进度记录 (2026-06-30):**', '### 13. VBA2python迁移进度记录')

# 8. Update TOC - need to regenerate
# Find TOC boundaries
start = c.find('**目录：**')
end = c.find('\n---\n\n\n# 昭明路线图', start)
if start >= 0 and end >= 0:
    before = c[:start]
    after = c[end:]
    c = before + '**目录：**\n' + after

# 9. Fix 附录一 and 附录二 (keep as appendices)
# No change needed

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')