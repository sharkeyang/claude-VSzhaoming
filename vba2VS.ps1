# ============================================================================
# vba2VS.ps1 — 导出 VBA 模块到 .bas 文本文件
# ============================================================================
# 用法: 在项目根目录执行  .\vba2VS.ps1
#
# 行为:
#   1. 若 Excel 已打开 → 仅保存目标工作簿（不关闭，不退出 Excel，不影响其他工作簿）
#   2. 复制 xlsm 到临时目录 → Python 导出 .bas → 复制到项目目录
#   3. 清理旧 .bas 再写入新 .bas，确保无残留文件、无 (1) 后缀
#
# 注意:
#   - 不会关闭 Excel，其他工作簿保持打开状态
#   - 需要 Python 环境已安装依赖: pip install oletools msoffcrypto
# ============================================================================

$ErrorActionPreference = "Stop"
$target = "昭明计划VS优化.xlsm"

# ============================================================================
# 1. 若 Excel 已打开 → 仅保存目标工作簿（不保存/不关闭其他，不退出 Excel）
# ============================================================================
try {
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    foreach ($wb in $excel.Workbooks) {
        if ($wb.Name -eq $target) {
            $wb.Save()
            Write-Host "已保存 [$target]。"
            break
        }
    }
} catch {
    Write-Host "Excel 未运行，跳过保存。"
}

# ============================================================================
# 2. 导出 xlsm → .bas（通过临时目录中转，避免 OneDrive 文件锁）
# ============================================================================
Copy-Item ".\$target" "$env:TEMP\$target" -Force
$src = "$env:TEMP\昭明计划VS优化_vba"
if (Test-Path $src) { Remove-Item -Recurse -Force $src; Start-Sleep 1 }

# Python 导出（-m 仅标准模块，-c NONE 跳过密码文件）
python ".\vba2宏操作.py" export "$env:TEMP\$target" -m -c NONE

# ============================================================================
# 3. 写入项目目录（先清空旧 .bas，确保无残留、无 (1) 后缀）
# ============================================================================
$dst = ".\昭明计划VS优化_vba"
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst; Start-Sleep 1 }
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item "$src\*.bas" $dst -Force
Write-Host "导出完成: $dst\  ($((Get-ChildItem $dst\*.bas).Count) 个模块)"
