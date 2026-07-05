"""Compare two VA files deeply"""
import difflib, re

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕1.bas', encoding='utf-8') as f:
    a = f.readlines()
with open('IQQQ跨码_D据擎2神谕.修改策略.bas', encoding='gbk') as f:
    b = f.readlines()

diff = list(difflib.unified_diff(a, b, fromfile='神谕1', tofile='修改策略', n=0))
adds = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
rems = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
print(f'神谕1: {len(a)}行 | 修改策略: {len(b)}行')
print(f'总差异: +{adds}/-{rems}')
print()

# Group by regions
regions = {}
for line in diff:
    if line.startswith('@@'):
        m = re.search(r'@@ -(\d+),\d+ \+(\d+),\d+ @@', line)
        if m:
            old_ln = int(m.group(1))
            new_ln = int(m.group(2))
            if new_ln < 500: sec = '常量区'
            elif new_ln < 1200: sec = 'BTZ/四域计算'
            elif new_ln < 2800: sec = '主结算循环'
            elif new_ln < 3500: sec = '策略计算'
            elif new_ln < 5000: sec = '衍生函数'
            else: sec = 'Excel输出'
    regions.setdefault(sec, []).append(line)

for sec, lines in sorted(regions.items()):
    adds = len([l for l in lines if l.startswith('+') and not l.startswith('+++')])
    rems = len([l for l in lines if l.startswith('-') and not l.startswith('---')])
    if adds + rems > 3:
        print(f'=== {sec} (+{adds}/-{rems}) ===')
        for line in lines[:25]:
            t = line.rstrip()
            if t.startswith('@@'):
                print(f'  {t[:65]}')
            elif t.startswith('+') and not t.startswith('+++'):
                print(f'  + {t[1:75]}')
            elif t.startswith('-') and not t.startswith('---'):
                print(f'  - {t[1:75]}')
        if len(lines) > 25:
            print(f'  ... 还有{len(lines)-25}行差异')
        print()