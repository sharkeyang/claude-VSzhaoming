import os
fp = 'd:/@VSwork/VS昭明计划VBA优化/____temp/C_old_完整.md'
with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('### 2.1')
end = content.find('### 2.2')
sec21 = content[start:end]

out = 'd:/@VSwork/VS昭明计划VBA优化/____temp/C_old_sec21.txt'
with open(out, 'w', encoding='utf-8') as f:
    f.write(sec21)
print(f'Saved: {len(sec21)} chars to ____temp/C_old_sec21.txt')

# Also show key counts
for term in ['警示一', '警示二', '警示三', '警示四', '警示五',
             '四区划总览（从好到差）', '分区解释', '<table']:
    count = sec21.count(term)
    if count > 0:
        print(f'  [{term}] x{count}')
    else:
        print(f'  [{term}] MISSING')

# Also check what the CURRENT §2.1 has
c_path = None
for item in os.listdir('.'):
    if item.startswith('_') and os.path.isdir(item):
        full = os.path.join(os.getcwd(), item)
        try:
            files = os.listdir(full)
        except:
            continue
        if '全局_C昭明路线图.md' in files:
            c_path = os.path.join(full, '全局_C昭明路线图.md')
            break

with open(c_path, 'r', encoding='utf-8') as f:
    current = f.read()

start_c = current.find('### 2.1')
end_c = current.find('### 2.2')
sec21_c = current[start_c:end_c]
print(f'\n当前§2.1: {len(sec21_c)} chars')
print(f'内容:')
print(sec21_c)