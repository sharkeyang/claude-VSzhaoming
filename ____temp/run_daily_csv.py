# -*- coding: utf-8 -*-
"""批量生成日级别CSV - 调用VBA XL算展前调_日_默认"""
import win32com.client, os, time, sys

sys.stdout.reconfigure(encoding='utf-8')

xlsm_path = os.path.abspath(r'____temp\昭明计划VS优化_副本_20260804.xlsm')
temp_dir = os.path.dirname(xlsm_path)

print(f'[1] 副本路径: {xlsm_path}')
print(f'[2] 正在启动Excel...')

excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False

try:
    print(f'[3] 打开工作簿...')
    wb = excel.Workbooks.Open(xlsm_path)
    print(f'[4] 运行宏 XL算展前调_日_默认 ...')
    print(f'    正在处理全部代码，请耐心等待...')
    t0 = time.time()
    
    excel.Application.Run('XL算展前调_日_默认')
    
    elapsed = time.time() - t0
    print(f'[5] 宏运行完成，耗时 {elapsed:.0f}s')
    
    print(f'[6] 保存工作簿...')
    wb.Save()
    wb.Close()
    
    # 检查输出
    output_dir = os.path.join(os.path.dirname(os.path.dirname(xlsm_path)), '昭明算展', '谕组日')
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
        print(f'[7] 输出目录: {output_dir}')
        print(f'    共生成 {len(files)} 个CSV文件')
    else:
        print(f'[7] 输出目录不存在: {output_dir}')
    
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()

finally:
    excel.Quit()
    win32com.client.ReleaseComObject(excel)
    print(f'[8] Excel已关闭')
