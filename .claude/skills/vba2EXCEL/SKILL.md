---
name: vba2EXCEL
description: Import edited .bas files back into 昭明计划VS优化.xlsm. Use after editing VBA code in text files. Cleans all old modules before importing. Always saves timestamped backup first.
---

# VBA Import

Imports all `.bas` files from `昭明计划VS优化_vba/` into `昭明计划VS优化.xlsm`. Automatically removes all old standard modules first for a clean import. **Always saves a timestamped backup** before overwriting.

Paths are relative to `d:\@VSwork\VS昭明计划VBA优化`.

## Execution (one shot)

```powershell
# 关闭Excel → 备份xlsm → 导入bas
try { 
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    $excel.Workbooks | ForEach-Object { $_.Save() }
    $excel.Quit()
    [Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    Start-Sleep 2
} catch { }

# 始终保存带时间戳的副本
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item .\昭明计划VS优化.xlsm ".\昭明计划VS优化_$ts.xlsm" -Force

# 导入
$tmpvba = "$env:TEMP\昭明计划VS优化_vba"
$tmpxlsm = "$env:TEMP\昭明计划VS优化.xlsm"
if (Test-Path $tmpvba) { Remove-Item -Recurse -Force $tmpvba; Start-Sleep 1 }
New-Item -ItemType Directory -Force $tmpvba | Out-Null
Copy-Item ".\昭明计划VS优化_vba\*.bas" $tmpvba -Force
Copy-Item .\昭明计划VS优化.xlsm $tmpxlsm -Force
python ".\VBA宏操作_导入_Python版.py" $tmpxlsm -s $tmpvba -m -c NONE
Copy-Item $tmpxlsm .\昭明计划VS优化.xlsm -Force
```

After import, open the xlsm in Excel to run the macros.
