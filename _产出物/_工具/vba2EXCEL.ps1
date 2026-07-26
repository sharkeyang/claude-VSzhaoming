# ============================================================================
# vba2EXCEL.ps1 — 导入 .bas 文本文件到 VBA 模块
# ============================================================================
# 用法: 在项目根目录下执行
#   _产出物\_工具\vba2EXCEL.ps1
#   或（如果 PATH 已配置）直接: vba2EXCEL
# ============================================================================
# 说明: 从昭明计划VS优化_vba/ 导入 .bas 到昭明计划VS优化.xlsm
#       自动备份原文件（时间戳命名），导入后打开最终文件
# 前提:
#   - pip install pywin32 msoffcrypto olefile
#   - Excel 信任中心勾选「信任对 VBA 工程对象模型的访问」
# ============================================================================

$ErrorActionPreference = "Stop"
$脚本目录 = Split-Path -Parent $MyInvocation.MyCommand.Path
$项目根目录 = Resolve-Path "$脚本目录\..\.."
$target = "昭明计划VS优化.xlsm"

# ============================================================================
# 1. 若目标 xlsm 正打开 → 保存并提示手动关闭
# ============================================================================
$excel = $null
try {
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
} catch { }

if ($excel -ne $null) {
    $targetWb = $null
    foreach ($wb in $excel.Workbooks) {
        if ($wb.Name -eq $target) {
            $targetWb = $wb
            break
        }
    }

    if ($targetWb -ne $null) {
        $targetWb.Save()
        Write-Host "已保存 [$target]。"

        Add-Type -AssemblyName System.Windows.Forms

        $closed = $false
        while (-not $closed) {
            $result = [System.Windows.Forms.MessageBox]::Show(
                "请手动关闭 Excel 中的 [$target]（不要关闭其他工作簿），`n关闭后点击【确定】继续导入；`n点击【取消】则退出导入。",
                "提示关闭工作簿",
                [System.Windows.Forms.MessageBoxButtons]::OKCancel,
                [System.Windows.Forms.MessageBoxIcon]::Information
            )

            if ($result -eq [System.Windows.Forms.DialogResult]::Cancel) {
                Write-Host "用户取消，退出导入。"
                exit 0
            }

            $stillOpen = $false
            foreach ($wb in $excel.Workbooks) {
                if ($wb.Name -eq $target) {
                    $stillOpen = $true
                    break
                }
            }

            if (-not $stillOpen) {
                $closed = $true
                Write-Host "[$target] 已关闭，继续导入。"
            }
        }
    } else {
        Write-Host "[$target] 未打开，继续。"
    }
} else {
    Write-Host "Excel 未运行，继续。"
}

# ============================================================================
# 2. 导入 .bas → xlsm（通过临时目录中转）
# ============================================================================
$tmpvba = "$env:TEMP\昭明计划VS优化_vba"
$tmpxlsm = "$env:TEMP\$target"

if (Test-Path $tmpvba) { Remove-Item -Recurse -Force $tmpvba; Start-Sleep 1 }
New-Item -ItemType Directory -Force $tmpvba | Out-Null

Copy-Item "$项目根目录\昭明计划VS优化_vba\*.bas" $tmpvba -Force
Copy-Item "$项目根目录\$target" $tmpxlsm -Force

# 备份原 xlsm（时间戳命名）
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "昭明计划VS优化_$ts.xlsm"
Copy-Item "$项目根目录\$target" "$项目根目录\$backupName" -Force
Write-Host "备份已保存: $backupName"

# 执行 Python 导入
python "$脚本目录\vba2宏操作.py" import $tmpxlsm -s $tmpvba -m -c NONE
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 导入失败（退出码: $LASTEXITCODE），保留原文件不变。"
    exit $LASTEXITCODE
}

# 覆盖回项目目录
$retry = 5
while ($retry -gt 0) {
    try {
        Copy-Item $tmpxlsm "$项目根目录\$target" -Force -ErrorAction Stop
        Write-Host "导入完成: $target"
        break
    } catch {
        $retry--
        if ($retry -gt 0) {
            Write-Host "文件被占用，1秒后重试（剩余 $retry 次）..."
            Start-Sleep 1
        } else {
            Write-Host "错误: 无法覆盖 $target，文件可能被其他进程锁定。"
            Write-Host "临时文件保留在: $tmpxlsm"
            exit 1
        }
    }
}

# ============================================================================
# 3. 在 Excel 中打开最终文件
# ============================================================================
try {
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    $excel.Visible = $true
    $finalPath = (Resolve-Path "$项目根目录\$target").Path
    $alreadyOpen = $false
    foreach ($wb in $excel.Workbooks) {
        if ($wb.FullName -eq $finalPath) {
            $wb.Activate()
            $alreadyOpen = $true
            break
        }
    }
    if (-not $alreadyOpen) {
        $excel.Workbooks.Open($finalPath) | Out-Null
    }
    Write-Host "已在 Excel 中打开: $target"
} catch {
    Start-Process "$项目根目录\$target"
    Write-Host "已打开: $target"
}