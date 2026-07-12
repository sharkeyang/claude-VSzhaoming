# -*- coding: utf-8 -*-
"""Check for lost content by comparing old vs new"""
import os, subprocess

root = os.getcwd()

# Get old version from git
result = subprocess.run(
    ['git', 'show', '6d7da47:_规则文档/全局_C昭明路线图.md'],
    capture_output=True, shell=True, cwd=root
)
old = result.stdout.decode('utf-8', errors='replace')

# Get current version
rules_dir = None
for item in os.listdir(root):
    if item.startswith('_') and os.path.isdir(os.path.join(root, item)):
        full = os.path.join(root, item)
        files = os.listdir(full)
        if '全局_C昭明路线图.md' in files:
            rules_dir = full
            break

c_path = os.path.join(rules_dir, '全局_C昭明路线图.md')
with open(c_path, 'r', encoding='utf-8') as f:
    new = f.read()

# Check specific key phrases that should exist
check_items = [
    '三大公理', '有容乃大', '镜面对称', '必赢战法',
    '一票否决', '四域', '多长', '多被', '空看', '空长',
    '金+甲乙己', 'ZA区间', '柱排', '盈提示', '波型',
    '龙猪', '头正', '震正', '尾反孕',
    '仁慈级', '股性评分', '月基策分', '周冲评分',
    '仓位管理', '板块轮动', 'ETF',
    'MC1', 'MC2', 'MC3', 'MC4', 'MC5',
    'MP1', 'MP2', 'MP3', 'MP4', 'MP5',
    'MO1', 'MO2', 'MO3',
    '交割单审计', '流水线',
]

missing = []
for item in check_items:
    if item in old and item not in new:
        missing.append(item)

if missing:
    print(f'MISSING from current ({len(missing)} items):')
    for m in missing:
        print(f'  - {m}')
else:
    print('All key content items preserved!')

# Check character counts
print(f'\nOld: {len(old)} chars')
print(f'New: {len(new)} chars')
print(f'Diff: {len(new) - len(old)} chars')

# The diff should be from blank line removal and section reorganization only
# Check if any meaningful text lines were lost
old_lines = [l.strip() for l in old.split('\n') if l.strip() and not l.strip().startswith('```')]
new_lines_set = set(l.strip() for l in new.split('\n') if l.strip() and not l.strip().startswith('```'))

lost_lines = [l for l in old_lines if l not in new_lines_set and len(l) > 40]
print(f'\nLines >40 chars in old but not in new: {len(lost_lines)}')
for l in lost_lines[:20]:
    print(f'  [{l[:80]}]' if len(l) > 80 else f'  [{l}]')