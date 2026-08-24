# -*- coding: utf-8 -*-
"""制作周级别一页纸"""
# 从MC3.1中提取第三章的关键数据
with open('_主文档/MC3.1_研究月基策略.md', 'rb') as f:
    data = f.read()

# 提取护型排序表（3.2.1附近）
ch3_start = data.find(b'## 3.2 \xe6\xa0\xb8\xe5\xbf\x83\xe9\xaa\x8c\xe8\xaf\x81\xe7\xbb\x93\xe6\x9e\x9c')
# 提取护型排序表
sort_start = data.find(b'WXZC>0 \xe6\x8e\x92\xe5\xba\x8f', ch3_start)
sort_end = data.find(b'WXZC\xe2\x89\xa40 \xe6\x8e\x92\xe5\xba\x8f', sort_start)
wxzc0_sort = data[sort_start:sort_end]

sort_start2 = data.find(b'WXZC\xe2\x89\xa40 \xe6\x8e\x92\xe5\xba\x8f', ch3_start)
sort_end2 = data.find(b'### 2.1.2', sort_start2)
wxzc0_sort2 = data[sort_start2:sort_end2]

print(wxzc0_sort.decode('utf-8', errors='replace')[:500])
print('---')
print(wxzc0_sort2.decode('utf-8', errors='replace')[:500])