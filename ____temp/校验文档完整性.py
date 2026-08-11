# -*- coding: utf-8 -*-
"""内容完整性校验：当前文档 vs 原始备份"""
import re

def load(p):
    return open(p, encoding='utf-8').read().split('\n')

def check_section(orig_lines, cur_text, label, o_start, o_end, c_start=None, c_end=None):
    """检查原始指定行区间的内容是否都在当前文件中"""
    orig_block = '\n'.join(orig_lines[o_start:o_end])
    # 去掉纯标题行（可能被重编号），只检查正文内容行
    content_lines = [l for l in orig_block.split('\n')
                     if l.strip() and not l.strip().startswith(('#','|:','|---|---','>|'))]
    missing = []
    for line in content_lines:
        # 标题类行可能因编号改而不同，跳过
        if line.strip().startswith('#') or line.strip().startswith('|') and ':' in line[:5]:
            continue
        if line not in cur_text:
            missing.append(line)
    if missing:
        print(f'[缺失] {label}: {len(missing)} 行')
        for m in missing[:15]:
            print(f'    → {m[:60]}')
    else:
        print(f'[完整] {label}: {len(content_lines)} 行正文全部在')

# ========== 读取 ==========
mc31_orig = load('____temp/备份_MC3.1_研究月基策略.md')
mc31_cur  = load('_主文档/MC3.1_研究月基策略.md')
mc33_orig = load('____temp/备份_MC3.3_研究日冲策略.md')
mc33_cur  = load('_主文档/MC3.3_研究日冲策略.md')

cur31 = open('_主文档/MC3.1_研究月基策略.md', encoding='utf-8').read()
cur33 = open('_主文档/MC3.3_研究日冲策略.md', encoding='utf-8').read()

print('========== MC3.1：原始内容是否都在当前 ==========')
# 原始 §1-§4 (37-929行) → 当前 §1-§4
check_section(mc31_orig, cur31, 'MC3.1 原始§1祖训', 36, 73)
check_section(mc31_orig, cur31, 'MC3.1 原始§2月基分类', 73, 197)
check_section(mc31_orig, cur31, 'MC3.1 原始§3操作规则', 197, 293)
check_section(mc31_orig, cur31, 'MC3.1 原始§4三变量框架', 293, 929)
# 原始 §5 VBA实施计划 (930-end)
check_section(mc31_orig, cur31, 'MC3.1 原始§5 VBA实施计划', 929, 960)

print()
print('========== MC3.3：原始内容是否都在当前 ==========')
# 原始 §1 (60-91)
check_section(mc33_orig, cur33, 'MC3.3 原始§1总览', 59, 92)
# 原始 §2.1 DXEF-DXCD (95-264) → 当前 §3
check_section(mc33_orig, cur33, 'MC3.3 原始§2.1执行框架', 94, 264)
# 原始 §4 按形态探索 (1407-1492) → 当前 §4
check_section(mc33_orig, cur33, 'MC3.3 原始§4按形态探索', 1406, 1492)

print()
print('========== 216分支内容从 MC3.3 移到 MC3.1 ==========')
# 原始 §3.1-3.4 (405-920) 216分支概率表 → 当前 MC3.1 §5.3
check_section(mc33_orig, cur31, '216分支概率表(§3.1-3.4) → MC3.1§5.3', 405, 919)
# 原始 §3.8 规则验证 (1084-1242) → 当前 MC3.1 §5.4
check_section(mc33_orig, cur31, '规则验证(§3.8) → MC3.1§5.4', 1083, 1241)
# 原始 §3.0 分类系统 (270-404) → 当前 MC3.1 §5.1
check_section(mc33_orig, cur31, '8格分类(§3.0) → MC3.1§5.1', 269, 404)