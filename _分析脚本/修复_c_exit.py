with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

old = '''	  仓位仅跟随区划：
	    __多长      → 持有基仓
	    _多被   → 可参与（视情况开基仓）
	    _空看    → 不参与
	    _空长   → 不参与
	```

	**4. 待代码实现**
	- [ ] 重构_多长区仓位逻辑：移除_多长浮仓/_多长减仓，统一为_多长基仓
	- [ ] 冲高信号独立为浮仓入场信号（下周冲高→周频浮仓，下日冲高→日频浮仓）
	- [ ] 仓位退出统一由区划切换触发（区划≠_多长时清仓）'''

new = '''	  仓位退出规则：
	    _多长基仓 → 持有，等待 WXZC<0 时退出
	    _多长浮仓 → 在 DJE&DJC 之上介入，下破 DJC 退出浮仓
	    _多被     → 可参与（视情况开基仓）
	    _空看     → 不参与
	    _空长     → 不参与
	```

	**4. 待代码实现**
	- [ ] 重构_多长区仓位逻辑：移除_多长浮仓/_多长减仓，统一为_多长基仓
	- [ ] 冲高信号独立为浮仓入场信号（下周冲高→周频浮仓，下日冲高→日频浮仓）
	- [ ] 基仓退出条件：WXZC<0；浮仓退出条件：下破DJC（基仓不受浮仓退出影响）'''

if old in c:
    c = c.replace(old, new)
    print('C fixed')
else:
    # Try with different whitespace
    import re
    # Find the section by regex
    pattern = r'仓位仅跟随区划：\n.*__多长.*\n.*_多被.*\n.*_空看.*\n.*_空长.*\n'
    match = re.search(pattern, c)
    if match:
        print('Found via regex')
        # Just replace the specific lines
        c = c.replace('仓位仅跟随区划：', '仓位退出规则：')
        c = c.replace('__多长      → 持有基仓', '_多长基仓 → 持有，等待 WXZC<0 时退出')
        c = c.replace('_多被   → 可参与（视情况开基仓）', '_多长浮仓 → 在 DJE&DJC 之上介入，下破 DJC 退出浮仓\n	    _多被     → 可参与（视情况开基仓）')
        c = c.replace('仓位退出统一由区划切换触发（区划≠_多长时清仓）', '基仓退出条件：WXZC<0；浮仓退出条件：下破DJC（基仓不受浮仓退出影响）')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')