import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
# 第六章范围 3351-4900
concepts = {
    '跌管退出': ['跌管退出', 'DTZA≤-2', 'DTZA<=-2'],
    '冲高回落减仓': ['升管内跌排', '跌排减仓'],
    'DXZC<0退出': ['DXZC<0必须退出', 'DXZC<0退出'],
    'DJA之上警惕': ['DJA之上跌连', 'DJA之上跌排'],
    '重新站上诱多': ['重新站上诱多', '重新站上DJA'],
    '阴柱/阳柱接入': ['阴柱接入', '阳柱接入'],
    '操盘成功率': ['操盘成功率', '成功率'],
    '管宽跌连退出': ['管宽≥10', '管宽>=10'],
}
print('=== 第六章(3351-4900)中 5.2 概念出现次数 ===')
for name, needles in concepts.items():
    count = 0
    for i in range(3350, 4900):
        for n in needles:
            if n in lines[i]:
                count += 1
                break
    print(f'  {name}: {count} 处')
