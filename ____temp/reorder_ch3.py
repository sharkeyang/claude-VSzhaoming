import re

with open(r'_主文档/MC3.1_研究月基策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Extract 2.4 section
start_24 = content.index('### 2.4 操作规则')
end_24 = content.index('\n```\n', start_24)
end_24 = content.index('\n', end_24 + 5)  # past the closing ```

sec_24 = content[start_24:end_24 + 1]

# 2. Build new 3.1 section
sec_31 = '### 3.1 操作规则\n\n' + sec_24.split('\n', 1)[1]  # replace ### 2.4 with ### 3.1

# 3. Remove old 2.4 from document
before_24 = content[:start_24]
after_24 = content[end_24 + 1:]

# 4. Clean up blank lines and separators
# Remove the \n---\n\n\n\n---\n pattern (double separators)
after_24 = re.sub(r'\n---\n{2,}---\n', '\n---\n\n', after_24)

# 5. Change Chapter 3 title
after_24 = after_24.replace('## 第三章：月基策略：持仓预警与退出', '## 第三章：月基策略操作规则')

# 6. Insert 3.1 at start of Chapter 3
ch3_start = after_24.index('## 第三章：月基策略操作规则')
ch3_title_end = after_24.index('\n', ch3_start)
before_ch3 = after_24[:ch3_title_end + 1]
after_ch3_body = after_24[ch3_title_end + 1:]

# Build new content with 3.1 inserted
mid = before_ch3 + '\n' + sec_31.strip() + '\n\n' + after_ch3_body.strip()

# 7. Renumber existing 3.x sections: 3.1→3.2, 3.2→3.3, etc.
# But only AFTER the new 3.1. So we need to find the boundary.
# The new 3.1 is right after the chapter title, so everything after it is old content.
# Use reverse order to avoid replacement conflicts
for i in [5, 4, 3, 2, 1]:
    mid = mid.replace(f'### 3.{i} ', f'### 3.{i+1} ')

# The new 3.1 was also changed by the above loop (3.1→3.2)
# Fix it back
mid = mid.replace('### 3.2 操作规则\n', '### 3.1 操作规则\n')

# 8. Clean up double blank lines
mid = re.sub(r'\n{3,}', '\n\n', mid)

# 9. Rebuild full document
new_content = before_24 + mid

# Also clean up blank lines in the before_24 section
new_content = re.sub(r'\n{3,}', '\n\n', new_content)

with open(r'_主文档/MC3.1_研究月基策略.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('OK')