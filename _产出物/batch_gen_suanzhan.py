"""通过VBA COM批量生成算展文件"""
import os, sys, time
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
import win32com.client

BASE = r'd:\@VSwork\VS昭明计划VBA优化'
SUANZHAN = os.path.join(BASE, '昭明算展')
ZDATA = r'D:\zdata\data中股'

excel = win32com.client.GetActiveObject('Excel.Application')

# 已有算展
existing = set()
for f in os.listdir(SUANZHAN):
    if f.startswith('算展.') and f.endswith('.xlsx'):
        code = f.replace('算展.','').replace('.xlsx','')
        existing.add(code)

# 找zdata中ETF但无算展的
targets = []
for f in sorted(os.listdir(ZDATA)):
    if not f.endswith('.csv'): continue
    c = f.replace('.csv','')
    full = f'sh{c}' if c.startswith(('5','6')) else f'sz{c}'
    if full not in existing and c.startswith(('51','159','56','52')):
        targets.append(full)

print(f'待生成算展: {len(targets)}只')

# 方法: 通过COM操作Excel界面
# 1. 在工作簿中新建sheet, 命名为代码
# 2. 调用VBA生成数据
# 3. 保存为算展文件

# 先获取工作簿
xlsm = None
for wb in excel.Workbooks:
    if '昭明计划VS优化' in wb.Name:
        xlsm = wb
        break

if not xlsm:
    print('未找到昭明计划VS优化.xlsm')
    sys.exit(1)

print(f'工作簿: {xlsm.Name}')

ok = 0
for i, code in enumerate(targets):
    fp = os.path.join(SUANZHAN, f'算展.{code}.xlsx')
    if os.path.exists(fp):
        ok += 1
        print(f'[{i+1}/{len(targets)}] {code} 已有')
        continue

    try:
        print(f'[{i+1}/{len(targets)}] {code}...', end=' ', flush=True)

        # 调用取谕组 - 会生成算展文件到____temp
        excel.Application.Run("XL算展取谕组", code)
        time.sleep(0.3)

        # 检查____temp下的谕组文件
        temp_dir = os.path.join(BASE, '____temp')
        found = None
        for f in os.listdir(temp_dir):
            if code in f and f.endswith('.xlsx') and '谕组' in f:
                found = os.path.join(temp_dir, f)
                break

        if found:
            # 保存到算展目录
            import shutil
            shutil.copy2(found, fp)
            print(f'✓ ({os.path.getsize(found)//1024}KB)')
            ok += 1
        else:
            # 可能在工作簿的____temp下
            print('未找到输出')
    except Exception as e:
        print(f'失败: {e}')

    time.sleep(0.2)

print(f'\n完成: {ok}/{len(targets)}')
total_etf = len([c for c in targets if c in existing] or []) + ok
print(f'总算展ETF: {total_etf+52}只')
print(f'总算展文件: {len(existing)+ok}个')