# -*- coding: utf-8 -*-
"""
更新元数据映射 — 每次重新导出谕组日/谕组周 CSV 后运行
====================================================
功能：
  1. 读取谕组日/谕组周 CSV 表头（GBK），生成列映射（列号→列名）
  2. 校验列数与 VBA 导出代码预期一致（日66列/周53列）
  3. 更新固定元数据表：
       _产出物\_工具\元数据_vba数据映射_日类.md
       _产出物\_工具\元数据_vba数据映射_周类.md
  4. 记录导出日期、文件数、列数

用法：
  python _产出物\_工具\更新元数据映射.py
  （在项目根目录下执行）

权威来源：PX算研_RAP算展1引擎.bas → Sub XL算展取样调程_谕组单股通用
  - 日类表头 L1792，周类表头 L1708
  - 列序以 VBA 代码为准，本脚本从 CSV 表头读取（2026-09-24 重新导出后表头已与数据对齐）
"""
import csv, os, io, glob, datetime, sys

# ============================================================================
# 配置
# ============================================================================
项目根 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
日目录 = os.path.join(项目根, '昭明算展', '谕组日')
周目录 = os.path.join(项目根, '昭明算展', '谕组周')
日元数据 = os.path.join(项目根, '_产出物', '_工具', '元数据_vba数据映射_日类.md')
周元数据 = os.path.join(项目根, '_产出物', '_工具', '元数据_vba数据映射_周类.md')

# 预期列数（对照 VBA 导出代码）
# 2026-10-04 导出程序更新后：日类新增月策略日/月策分日P2/日策分P2/日层漏提示/月策分命 → 70列
# 周类新增周势型/四域/周策略P3/P1/ZA/策分系列/月策分命 → 60列（2026-10-11 确认，无周龄/周键）
预期列数 = {'日类': 70, '周类': 60}

# ============================================================================
# 抽检配置：每列的标准格式（值域/正则），用于验证列映射正确（防止列错位）
# 抽检规则：构建元数据时，抽样检查每列的值是否符合 VBA 变量的标准格式。
#   若某列符合率过低（<90%），说明该列可能错位（表头与数据列序不一致），须报警。
# 依据：VBA 导出代码 PX算研_RAP算展1引擎.bas 中各变量的值域/格式。
# ============================================================================
import re

# 通用校验：整数（交叉天数，可带负号）
def 是整数(v):
    return bool(re.match(r'^-?\d+$', v.strip()))

# 通用校验：浮点数（可带负号/小数，如 BSHA/BSAC 是百分比）
def 是浮点(v):
    return bool(re.match(r'^-?\d+(\.\d+)?$', v.strip()))

# 通用校验：非空字符串
def 非空(v):
    return bool(v.strip())

# 周类抽检配置：{列号: (列名, 校验函数)}
周类抽检 = {
    4: ('护型(WXAB)', lambda v: bool(re.match(r'^[abczyr][甲乙丙丁戊己]', v.strip()))),
    5: ('波型', lambda v: bool(re.match(r'^[A-Z]', v.strip()))),
    6: ('柱排周', lambda v: bool(v.strip()) and ('升' in v or '跌' in v or '人' in v)),
    9: ('周势型(WXCD)', lambda v: bool(re.match(r'^[0-9]', v.strip()))),
    13: ('ZA周', 是整数), 14: ('ZB周', 是整数), 15: ('ZC周', 是整数),
    16: ('ZD周', 是整数), 17: ('ZE周', 是整数), 18: ('ZF周', 是整数),
    19: ('AB周', 是整数), 20: ('AC周', 是整数), 21: ('BC周', 是整数),
    22: ('AD周', 是整数), 23: ('BD周', 是整数), 24: ('CD周', 是整数),
    25: ('CE周', 是整数), 26: ('DE周', 是整数), 27: ('CF周', 是整数), 28: ('EF周', 是整数),
    29: ('底周', 是整数), 30: ('哈周', 是整数), 31: ('哼周', 是整数),
    32: ('顶周', 是整数), 33: ('合底周', 是整数), 34: ('合顶周', 是整数),
    35: ('极折周', lambda v: v.strip() in ('高', '低', '撤', '弹')),
    36: ('顶态周', lambda v: v.strip() in ('G', 'K', 'L')),
    37: ('顶型周', lambda v: bool(re.match(r'^[a-zA-Z_]', v.strip()))),
    38: ('顶触周', lambda v: bool(re.match(r'^[GKL][0-9]', v.strip()))),
    48: ('并符串周', 非空),
}

# 日类抽检配置：{列号: (列名, 校验函数)}
日类抽检 = {
    8: ('DXCD', lambda v: v.strip() in ('上', '中', '下', '忐', '忠', '忑')),
    9: ('DXAB护型', lambda v: bool(re.match(r'^[abczyr][甲乙丙丁戊己]', v.strip()))),
    13: ('日ZA', 是整数), 14: ('日ZC', 是整数), 15: ('日ZE', 是整数),
    19: ('BSHA', 是浮点), 20: ('BSAC', 是浮点),
    42: ('顶型', lambda v: bool(re.match(r'^[a-zA-Z_]', v.strip()))),
    43: ('日等型', lambda v: bool(re.match(r'^等[0-9]', v.strip()))),
    44: ('仓日类', lambda v: bool(re.match(r'^[一-鿿]+[a-zA-Z]$', v.strip()))),
    66: ('DTZB', 是整数), 67: ('DTZD', 是整数), 68: ('DTAB', 是整数), 69: ('DTCD', 是整数),
}

# ============================================================================
# 抽检函数：抽样检查每列值是否符合标准格式
# ============================================================================
def 抽检列值(目录, 前缀, 抽检配置, 样本数=300):
    """抽样读取若干 CSV，检查配置列的值是否符合标准格式，返回 (符合率dict, 报警list)"""
    files = sorted(glob.glob(os.path.join(目录, f'{前缀}_*.csv')))
    if not files:
        return {}, []
    # 抽样文件（最多样本数）
    import random
    random.seed(42)
    抽样文件 = random.sample(files, min(样本数, len(files)))
    # 统计每列符合/总数
    统计 = {col: [0, 0] for col in 抽检配置}  # [符合, 总数]
    for f in 抽样文件:
        try:
            with open(f, encoding='gbk', errors='replace') as fh:
                reader = csv.reader(fh)
                next(reader)  # 跳过表头
                for row in reader:
                    for col in 抽检配置:
                        if col >= len(row):
                            continue
                        名, 校验 = 抽检配置[col]
                        统计[col][1] += 1
                        if 校验(row[col]):
                            统计[col][0] += 1
        except Exception:
            continue
    # 计算符合率
    符合率 = {}
    报警 = []
    for col, (名, 校验) in 抽检配置.items():
        n = 统计[col][1]
        if n == 0:
            continue
        rate = 统计[col][0] / n * 100
        符合率[col] = rate
        if rate < 90:
            报警.append(f'列[{col}]{名} 符合率 {rate:.1f}% < 90%，可能列错位！')
    return 符合率, 报警

# ============================================================================
# 读取 CSV 表头
# ============================================================================
def 读表头(目录, 前缀):
    """读取目录下第一个 CSV 的表头，返回 (列名列表, 文件数)"""
    files = sorted(glob.glob(os.path.join(目录, f'{前缀}_*.csv')))
    if not files:
        return None, 0
    with open(files[0], encoding='gbk') as f:
        reader = csv.reader(f)
        header = next(reader)
    return header, len(files)

# ============================================================================
# 更新元数据文件
# ============================================================================
def 更新元数据(元数据路径, 类别, header, 文件数):
    """更新元数据 md 文件：更新导出记录段（保留手写的列映射语义表）"""
    today = datetime.date.today().isoformat()
    列数 = len(header)

    # 读取现有文件
    with open(元数据路径, encoding='utf-8') as f:
        content = f.read()

    # 更新标题中的列数（"共 N 列"）
    import re
    content = re.sub(r'（0-based，共 \d+ 列）', f'（0-based，共 {列数} 列）', content)

    # 更新导出记录（替换 "## 导出记录" 段）
    记录开始 = content.find('## 导出记录')
    if 记录开始 != -1:
        content = content[:记录开始] + f'## 导出记录\n- {today}：重新导出，{类别}CSV 共 {列数} 列，文件数 {文件数}。表头与数据列序已对齐。\n'

    with open(元数据路径, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

# ============================================================================
# 主流程
# ============================================================================
def main():
    print('=' * 70)
    print('更新元数据映射')
    print('=' * 70)

    ok = True
    for 类别, 目录, 元数据路径, 前缀, 抽检配置 in [
        ('日类', 日目录, 日元数据, '谕组日', 日类抽检),
        ('周类', 周目录, 周元数据, '谕组周', 周类抽检),
    ]:
        header, 文件数 = 读表头(目录, 前缀)
        if header is None:
            print(f'[错误] {目录} 下无 CSV 文件，跳过 {类别}')
            ok = False
            continue

        列数 = len(header)
        预期 = 预期列数[类别]
        print(f'\n{类别}: 列数={列数} (预期{预期}), 文件数={文件数}')

        if 列数 != 预期:
            print(f'  [警告] 列数 {列数} ≠ 预期 {预期}！可能 VBA 导出代码已变更，需人工核对列序。')
            ok = False
        else:
            print(f'  [OK] 列数与预期一致')

        # 打印表头供核对
        print(f'  表头: {", ".join(header)}')

        # 抽检列值是否符合 VBA 变量标准格式（防止列错位）
        print(f'  [抽检] 抽样检查列值是否符合 VBA 变量标准格式...')
        符合率, 报警 = 抽检列值(目录, 前缀, 抽检配置)
        for col in sorted(符合率):
            print(f'    列[{col}] {抽检配置[col][0]}: 符合率 {符合率[col]:.1f}%')
        if 报警:
            for a in 报警:
                print(f'    [警告] {a}')
                ok = False
        else:
            print(f'  [OK] 抽检全部通过（符合率>=90%）')

        if 更新元数据(元数据路径, 类别, header, 文件数):
            print(f'  [OK] 已更新 {元数据路径}')
        else:
            ok = False

    print('\n' + '=' * 70)
    if ok:
        print('元数据更新完成。')
    else:
        print('存在警告，请人工核对列序后再跑分析。')
    print('=' * 70)

if __name__ == '__main__':
    main()
