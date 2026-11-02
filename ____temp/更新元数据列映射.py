#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""更新元数据文件列映射表（日类131→135列、周类63→65列），按含义列名匹配"""
import csv, sys, os
sys.stdout.reconfigure(encoding='utf-8')

项目根 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def 读旧语义(路径):
    """读取旧元数据，按含义列名提取 (变量, 含义, 备注)"""
    with open(路径, encoding='utf-8') as f:
        content = f.read()
    sem = {}  # 含义 -> (变量, 备注)
    for ln in content.split('\n'):
        if ln.startswith('|') and not ln.startswith('|:') and not ln.startswith('| 列'):
            parts = [p.strip() for p in ln.strip('|').split('|')]
            if len(parts) >= 3 and parts[0].isdigit():
                var = parts[1]
                meaning = parts[2]
                note = parts[3] if len(parts) > 3 else ''
                # 含义列可能含括号说明，取主名；也处理 "日ZA = DTZA" 格式
                main = meaning.split('（')[0].split('(')[0].strip()
                main = main.split(' = ')[0].split('=')[0].strip()
                sem[main] = (var, meaning, note)
    return sem

def 生成表(新表头, 旧语义, 新增列, 标题, 列数):
    lines = []
    lines.append(f'## 完整列映射（0-based，共 {列数} 列）')
    lines.append('')
    lines.append(f'### {标题}（2026-10-31 更新）')
    lines.append('')
    lines.append('| 列 | 变量 | 含义 | 备注 |')
    lines.append('|:--:|:--|:--|:--|')
    for i, name in enumerate(新表头):
        if i in 新增列:
            lines.append(f'| {i} | {name} | | 2026-10-31 新增 |')
            continue
        if name in 旧语义:
            var, meaning, note = 旧语义[name]
            lines.append(f'| {i} | {var} | {meaning} | {note} |')
        else:
            lines.append(f'| {i} | {name} | | |')
    return '\n'.join(lines)

# ============ 日类 ============
with open(os.path.join(项目根, '昭明算展', '谕组日', '谕组日_sh600004.csv'), encoding='gbk') as f:
    日表头 = next(csv.reader(f))
旧日 = 读旧语义(os.path.join(项目根, '____temp', '旧元数据_日类.md'))
新日 = 生成表(日表头, 旧日, {11, 12, 13, 80}, '日类指标（列 0-71）', 135)

日路径 = os.path.join(项目根, '_产出物', '_工具', '元数据_vba数据映射_日类.md')
with open(日路径, encoding='utf-8') as f:
    日内容 = f.read()
开始 = 日内容.find('## 完整列映射')
结束 = 日内容.find('## 关键语义')
if 开始 != -1 and 结束 != -1:
    日内容 = 日内容[:开始] + 新日 + '\n\n' + 日内容[结束:]
    with open(日路径, 'w', encoding='utf-8') as f:
        f.write(日内容)
    print('日类元数据列映射表已更新')

# ============ 周类 ============
with open(os.path.join(项目根, '昭明算展', '谕组周', '谕组周_sh600004.csv'), encoding='gbk') as f:
    周表头 = next(csv.reader(f))
旧周 = 读旧语义(os.path.join(项目根, '____temp', '旧元数据_周类.md'))
新周 = 生成表(周表头, 旧周, {9, 14}, '周类指标', 65)

周路径 = os.path.join(项目根, '_产出物', '_工具', '元数据_vba数据映射_周类.md')
with open(周路径, encoding='utf-8') as f:
    周内容 = f.read()
开始 = 周内容.find('## 完整列映射')
结束 = 周内容.find('## 关键语义')
if 开始 != -1 and 结束 != -1:
    周内容 = 周内容[:开始] + 新周 + '\n\n' + 周内容[结束:]
    with open(周路径, 'w', encoding='utf-8') as f:
        f.write(周内容)
    print('周类元数据列映射表已更新')