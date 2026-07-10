# Fix curly quotes in 筛选.bas - use unicode escapes
fp = r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_P展擎1筛选.bas'
with open(fp, 'r', encoding='utf-8') as f:
    t = f.read()

t = t.replace('“', '"')
t = t.replace('”', '"')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(t)

cnt = t.count('“') + t.count('”')
print(f'Remaining curly quotes: {cnt}')