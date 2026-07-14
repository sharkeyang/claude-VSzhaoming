"""fix-toc — 文档目录与章节编号修复工具

用法：python fix_toc.py 研究周冲策略.md
功能：重新生成TOC + 检测编号断号 + 检查交叉引用
"""
import re, sys, os

# 强制 UTF-8 输出
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def gfm_anchor(text):
    """生成 GitHub 风格锚点"""
    # 去掉数字点号后的空格（1.1 → 11）
    text = re.sub(r'(\d+)\.(\d+)', r'\1\2', text)
    # 去掉括号及内容
    text = re.sub(r'[（(][^)）]*[)）]', '', text)
    # 转小写、去标点、空格变连字符
    text = text.lower()
    text = re.sub(r'[^\w一-鿿\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text

def parse_headings(content):
    """提取所有 ## 和 ### 标题"""
    headings = []
    for i, line in enumerate(content.split('\n'), 1):
        m = re.match(r'^(#{2,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            anchor = gfm_anchor(text)
            headings.append({'line': i, 'level': level, 'text': text, 'anchor': anchor})
    return headings

def build_toc(headings):
    """根据标题列表生成 TOC 文本"""
    lines = []
    lines.append('**目录：**')
    lines.append('')
    for h in headings:
        indent = '    ' * (h['level'] - 2)
        lines.append(f'{indent}- [{h["text"]}](#{h["anchor"]})')
    return '\n'.join(lines)

def check_cross_refs(content, headings):
    """检查文中 §X.X 引用是否匹配实际标题编号"""
    # 提取所有标题编号映射
    num_map = {}
    for h in headings:
        m = re.match(r'(\d+\.\d+)', h['text'])
        if m:
            num_map[m.group(1)] = h['text']

    # 扫描所有 §X.X 引用
    refs = re.findall(r'§(\d+\.\d+)', content)
    issues = []
    for ref in refs:
        if ref not in num_map:
            # 检查相近编号
            closest = None
            for k in num_map:
                if k.startswith(ref.rsplit('.', 1)[0]):
                    closest = k
            issues.append(f'  引用 §{ref} → 未找到，最近匹配: §{closest}' if closest else f'  引用 §{ref} → 未找到')
    return issues

def check_gaps(headings):
    """检测编号断号"""
    nums = []
    for h in headings:
        m = re.match(r'(\d+\.\d+)', h['text'])
        if m:
            nums.append(m.group(1))
    issues = []
    for i in range(1, len(nums)):
        cur = nums[i]
        prev = nums[i-1]
        # 检查是否跳跃超过0.1
        try:
            cur_f = float(cur)
            prev_f = float(prev)
            if cur_f - prev_f > 0.11:
                issues.append(f'  断号: §{prev} → §{cur} 之间缺失章节')
        except:
            pass
    return issues

def fix_toc(filepath, dry_run=False):
    if not os.path.exists(filepath):
        print(f'文件不存在: {filepath}')
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    headings = parse_headings(content)
    toc = build_toc(headings)

    print(f'=== {os.path.basename(filepath)} ===')
    print(f'扫描到 {len(headings)} 个标题')
    print()

    # 检测断号
    gaps = check_gaps(headings)
    if gaps:
        print('编号断号:')
        for g in gaps:
            print(g)
        print()
    else:
        print('编号连续 ✅')

    # 检查交叉引用
    ref_issues = check_cross_refs(content, headings)
    if ref_issues:
        print('交叉引用问题:')
        for r in ref_issues:
            print(r)
        print()
    else:
        print('交叉引用全部匹配 ✅')

    print()
    print('=== 新 TOC ===')
    print(toc)

    # 替换 TOC
    if not dry_run:
        # 找 TOC 区域（从 **目录：** 到第一个 ## 标题之间）
        toc_start = content.find('**目录：**')
        first_h2 = None
        for h in headings:
            if h['level'] == 2:
                first_h2 = h['text']
                break
        if first_h2:
            idx = content.find(f'## {first_h2}')
            if idx >= 0 and toc_start >= 0:
                new_content = content[:toc_start] + toc + '\n\n' + content[idx:]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'\n✅ TOC 已更新到 {filepath}')
            else:
                print('\n⚠️ 无法定位 TOC 区域，请手动替换')
        else:
            print('\n⚠️ 未找到 ## 标题')


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not files:
        # 默认扫描 _主文档/
        files = [os.path.join('_主文档', f) for f in os.listdir('_主文档') if f.endswith('.md')]
    for fp in files:
        fix_toc(fp, dry_run=dry)
        print('='*60)