import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
concepts = ['DTZA≤-2', '跌管退出', '冲高回落', 'DXZC<0必须退出', '重新站上诱多', '跌连不退出', '管宽≥10', '阴柱接入', '阳柱接入']
print('=== 第六章(3351行后)中 5.2 关键概念 ===')
for i in range(3350, len(lines)):
    l = lines[i]
    for c in concepts:
        if c in l:
            hdr = '?'
            for j in range(i, max(i-15, 0), -1):
                if re.match(r'^#{3,6} ', lines[j]):
                    hdr = lines[j].strip()[:55]
                    break
            print(f'  [{i+1}] "{c}" → 附近标题: {hdr}')
            break
