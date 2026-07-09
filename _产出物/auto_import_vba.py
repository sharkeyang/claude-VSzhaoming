"""自动导入VBA: 使用已有Excel实例, 通过VBA宏保存文件"""
import os, sys, shutil, time
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
import win32com.client

BASE = r'd:\@VSwork\VS昭明计划VBA优化'
VBA_DIR = os.path.join(BASE, '昭明计划VS优化_vba')
TARGET = os.path.join(BASE, '昭明计划VS优化.xlsm')

# 1. 备份
shutil.copy2(TARGET, TARGET.replace('.xlsm', f'_backup_{time.strftime("%H%M%S")}.xlsm'))

# 2. 获取已有Excel实例
excel = win32com.client.GetActiveObject('Excel.Application')
excel.DisplayAlerts = False
excel.Visible = True

# 3. 打开xlsm
wb = excel.Workbooks.Open(TARGET)
proj = excel.VBE.ActiveVBProject
print(f'已打开, 当前模块: {len([c for c in proj.VBComponents if c.Type==1])}')

# 4. 删除旧模块
for c in list(proj.VBComponents):
    if c.Type == 1:
        try: proj.VBComponents.Remove(c)
        except: pass

# 5. 逐个导入
for f in sorted(os.listdir(VBA_DIR)):
    if not f.endswith('.bas'): continue
    try:
        proj.VBComponents.Import(os.path.join(VBA_DIR, f))
    except Exception as e:
        err = str(e)
        if '不是一个合法的对象名' in err:
            # 编码问题: 文件是GBK但VBA读成UTF-8, 显式用GBK写回
            fp = os.path.join(VBA_DIR, f)
            with open(fp, 'rb') as fh:
                raw = fh.read()
            try:
                text = raw.decode('gbk')
            except:
                text = raw.decode('gbk', errors='replace')
            # 写回GBK
            with open(fp, 'w', encoding='gbk') as fh:
                fh.write(text)
            # 重试
            try:
                proj.VBComponents.Import(os.path.join(VBA_DIR, f))
                print(f'  [GBK] {f}')
            except Exception as e2:
                print(f'  [FAIL] {f}: {str(e2)[:50]}')
        else:
            print(f'  [FAIL] {f}: {str(e)[:50]}')

imported = len([c for c in proj.VBComponents if c.Type==1])
print(f'导入完成: {imported}个模块')

# 6. 保存(关闭+重开, 避免RPC问题)
print('保存中...')
try:
    wb.Close(False)
    print(f'已关闭, 重新打开...')
    wb2 = excel.Workbooks.Open(TARGET)
    wb2.Save()
    print('保存成功!')
    wb2.Close(False)
except Exception as e:
    print(f'重开保存失败: {e}')
    try:
        excel.ActiveWorkbook.Save()
        print('ActiveWorkbook保存成功')
    except:
        pass

# 清理临时模块
for c in proj.VBComponents:
    if c.Name == 'tmpVBAutoSave':
        try: proj.VBComponents.Remove(c)
        except: pass

# 关闭
wb.Close(False)
print('关闭完成')
print(f'最终: {imported}个模块导入成功')