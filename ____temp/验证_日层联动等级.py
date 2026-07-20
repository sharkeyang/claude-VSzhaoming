#!/usr/bin/env python3
"""验证日层联动等级体系 vs 下日冲高概率，在所有日类算展上"""
import os, sys, glob, re
from collections import defaultdict, Counter
import openpyxl

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SZ_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718'
files = sorted(glob.glob(os.path.join(SZ_DIR, '算展.*.xlsx')))
print(f'共 {len(files)} 个算展文件')

# ============================================================
# 辅助函数：从日周联动字符串提取首字(金银唏嘘尿屎)和等级
# ============================================================
def parse_联动(联动_str):
    """解析日周联动字符串，返回 (首字, 等级串, 后缀)"""
    if not 联动_str:
        return ('', '', '')
    s = str(联动_str).strip()
    if not s:
        return ('', '', '')
    首字 = s[0]
    # 提取等级：E0/E1/.../e5/V7/.../v0/转空
    m = re.search(r'([VEve><][0-9转空][上中下忐忑忠好]?)', s)
    等级 = m.group(1) if m else ''
    # 提取后缀
    idx = s.find('.')
    后缀 = s[idx:] if idx > 0 else ''
    return (首字, 等级, 后缀)

def compute_EV等级(ZE, CD, ZC, ZD, BC, AB, ZA, ZB):
    """计算 E/V 等级，与 VBA 逻辑一致"""
    if ZE > 0:  # DJE之上 → E系列
        if CD > 0:
            if ZC > 0:
                if BC > 0 and AB > 0:
                    if ZA > 0:
                        return 'E0上'
                    elif ZB > 0:
                        return 'E2上'
                    else:
                        return 'E1上'
                elif BC > 0:
                    return 'E3上'
                else:
                    return 'E4上'
            elif ZD > 0:
                return 'e5中'
            else:
                return 'e6下'
        elif ZC <= 0:
            return 'e7忑'
        elif ZC > 0 and ZD <= 0:
            return 'e8忠'
        elif ZD > 0:
            return 'E9忐'
        else:
            return '>转空'
    else:  # DJE之下 → V系列
        if CD > 0:
            if ZC > 0:
                return 'V7上'
            elif ZD > 0:
                return 'V8中'
            else:
                return 'v9下'
        elif ZD > 0:
            return 'V6忐'
        elif ZC > 0:
            return 'V5忠'
        elif BC > 0:
            return 'v4忑'
        elif AB > 0:
            return 'v3忑'
        elif ZB > 0:
            return 'v2忑'
        elif ZA > 0:
            return 'v1忑'
        else:
            return 'v0忑'

# ============================================================
# 统计
# ============================================================
# 按等级统计
等级统计 = defaultdict(lambda: {'总':0, '冲高3':0, '冲高5':0, '涨和':0.0})
# 按首字统计
首字统计 = defaultdict(lambda: {'总':0, '冲高3':0, '冲高5':0, '涨和':0.0})
# 按后缀统计
后缀统计 = defaultdict(lambda: {'总':0, '冲高3':0, '冲高5':0, '涨和':0.0})
# 按(首字+等级)统计
组合统计 = defaultdict(lambda: {'总':0, '冲高3':0, '冲高5':0, '涨和':0.0})

total_rows = 0
等级_但无联动 = 0

for fi, fpath in enumerate(files):
    if fi % 50 == 0 and fi > 0:
        print(f'  已处理 {fi}/{len(files)} 个文件...')
    try:
        wb = openpyxl.load_workbook(fpath, data_only=True, read_only=True)
        ws = wb.active
        # 获取所有行
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            continue

        # 列索引: 0=日龄, 8=日涨, 86=日周联动
        # 日BT: 265=ZA, 266=ZB, 267=ZC, 268=AB, 271=ZD, 272=ZE, 273=CD
        for r in range(1, len(rows) - 1):  # 最后一行没有下一日
            row = rows[r]
            next_row = rows[r+1]
            if len(row) < 274 or len(next_row) < 9:
                continue

            联动 = row[86]  # 日周联动
            日涨 = row[8]    # 当日涨
            下日涨 = next_row[8]  # 下日涨

            # 转数值
            try:
                日涨_f = float(日涨) if 日涨 else 0.0
                下日涨_f = float(下日涨) if 下日涨 else 0.0
            except (ValueError, TypeError):
                continue

            # 读取 BT 数据计算等级
            try:
                ZE = float(row[272]) if row[272] else 0
                CD = float(row[273]) if row[273] else 0
                ZC = float(row[267]) if row[267] else 0
                ZD = float(row[271]) if row[271] else 0
                BC = float(row[284]) if len(row) > 284 and row[284] else 0
                AB = float(row[268]) if row[268] else 0
                ZA = float(row[265]) if row[265] else 0
                ZB = float(row[266]) if row[266] else 0
            except (ValueError, TypeError, IndexError):
                continue

            # 计算等级
            ev = compute_EV等级(ZE, CD, ZC, ZD, BC, AB, ZA, ZB)

            # 解析联动字符串
            首字, 联动等级, 后缀 = parse_联动(联动)

            total_rows += 1

            # 按等级统计
            等级统计[ev]['总'] += 1
            if 下日涨_f >= 3: 等级统计[ev]['冲高3'] += 1
            if 下日涨_f >= 5: 等级统计[ev]['冲高5'] += 1
            等级统计[ev]['涨和'] += 下日涨_f

            # 按首字统计
            if 首字:
                首字统计[首字]['总'] += 1
                if 下日涨_f >= 3: 首字统计[首字]['冲高3'] += 1
                if 下日涨_f >= 5: 首字统计[首字]['冲高5'] += 1
                首字统计[首字]['涨和'] += 下日涨_f

            # 按后缀统计
            if 后缀:
                后缀统计[后缀]['总'] += 1
                if 下日涨_f >= 3: 后缀统计[后缀]['冲高3'] += 1
                if 下日涨_f >= 5: 后缀统计[后缀]['冲高5'] += 1
                后缀统计[后缀]['涨和'] += 下日涨_f

            # 按组合统计
            key = f'{首字}_{ev}'
            组合统计[key]['总'] += 1
            if 下日涨_f >= 3: 组合统计[key]['冲高3'] += 1
            if 下日涨_f >= 5: 组合统计[key]['冲高5'] += 1
            组合统计[key]['涨和'] += 下日涨_f

        wb.close()
    except Exception as e:
        print(f'  错误 {fpath}: {e}')
        continue

print(f'\n总行数: {total_rows:,}')
print(f'{"="*80}')

# ============================================================
# 输出：按 E/V 等级
# ============================================================
print('\n【E/V等级 vs 下日冲高概率】')
print(f'{"等级":<8s} {"总数":>8s} {"P>=3%":>8s} {"P>=5%":>8s} {"均涨":>8s} {"柱状图":<30s}')
print('-'*72)

# 等级排序
等级顺序 = ['E0上','E1上','E2上','E3上','E4上','e5中','e6下','e7忑','e8忠','E9忐','>转空',
           'V7上','V8中','v9下','V6忐','V5忠','v4忑','v3忑','v2忑','v1忑','v0忑']
for ev in 等级顺序:
    d = 等级统计[ev]
    if d['总'] < 50:
        continue
    r3 = d['冲高3']/d['总']*100
    r5 = d['冲高5']/d['总']*100
    avg = d['涨和']/d['总']
    bar = '█' * int(r3 / 2)
    print(f'{ev:<8s} {d["总"]:>8,} {r3:>7.1f}% {r5:>7.1f}% {avg:>7.2f}% {bar:<30s}')

# ============================================================
# 输出：按首字（金银唏嘘尿屎）
# ============================================================
print('\n【首字(金银唏嘘尿屎) vs 下日冲高概率】')
print(f'{"首字":<6s} {"总数":>8s} {"P>=3%":>8s} {"P>=5%":>8s} {"均涨":>8s} {"柱状图":<30s}')
print('-'*72)
for 首字 in ['金','银','唏','嘘','尿','屎']:
    d = 首字统计[首字]
    if d['总'] < 50:
        continue
    r3 = d['冲高3']/d['总']*100
    r5 = d['冲高5']/d['总']*100
    avg = d['涨和']/d['总']
    bar = '█' * int(r3 / 2)
    print(f'{首字:<6s} {d["总"]:>8,} {r3:>7.1f}% {r5:>7.1f}% {avg:>7.2f}% {bar:<30s}')

# ============================================================
# 输出：按后缀
# ============================================================
print('\n【后缀(.被/.警/.盈) vs 下日冲高概率】')
print(f'{"后缀":<8s} {"总数":>8s} {"P>=3%":>8s} {"P>=5%":>8s} {"均涨":>8s} {"柱状图":<30s}')
print('-'*72)
for 后缀 in sorted(后缀统计.keys(), key=lambda k: 后缀统计[k]['总'], reverse=True):
    d = 后缀统计[后缀]
    if d['总'] < 50:
        continue
    r3 = d['冲高3']/d['总']*100
    r5 = d['冲高5']/d['总']*100
    avg = d['涨和']/d['总']
    bar = '█' * int(r3 / 2)
    print(f'{后缀:<8s} {d["总"]:>8,} {r3:>7.1f}% {r5:>7.1f}% {avg:>7.2f}% {bar:<30s}')

# ============================================================
# 输出：按组合
# ============================================================
print('\n【首字+等级组合 Top30】')
print(f'{"组合":<12s} {"总数":>8s} {"P>=3%":>8s} {"P>=5%":>8s} {"均涨":>8s} {"柱状图":<30s}')
print('-'*72)
scores = [(k, v['冲高3']/v['总']*100, v['总']) for k, v in 组合统计.items() if v['总'] >= 30]
scores.sort(key=lambda x: x[1], reverse=True)
for k, r3, n in scores[:30]:
    d = 组合统计[k]
    r5 = d['冲高5']/d['总']*100
    avg = d['涨和']/d['总']
    bar = '█' * int(r3 / 2)
    print(f'{k:<12s} {n:>8,} {r3:>7.1f}% {r5:>7.1f}% {avg:>7.2f}% {bar:<30s}')

# ============================================================
# 合并建议：寻找更好的分类
# ============================================================
print('\n【合并分析】E系列合并 vs V系列合并')
for prefix, label in [('E','E系列(DJE之上)'), ('e','e系列(DJE之上衰退)'), ('V','V系列(DJE之下修复)'), ('v','v系列(DJE之下最弱)')]:
    total = sum(等级统计[k]['总'] for k in 等级统计 if k.startswith(prefix))
    hit3 = sum(等级统计[k]['冲高3'] for k in 等级统计 if k.startswith(prefix))
    hit5 = sum(等级统计[k]['冲高5'] for k in 等级统计 if k.startswith(prefix))
    if total > 0:
        print(f'  {label}: n={total:,}, P>=3%={hit3/total*100:.1f}%, P>=5%={hit5/total*100:.1f}%')

print('\n【强/中/弱 三档合并建议】')
# 强: E0~E4 + V7 + 金/银
强总 = sum(等级统计[k]['总'] for k in ['E0上','E1上','E2上','E3上','E4上','V7上'])
强3 = sum(等级统计[k]['冲高3'] for k in ['E0上','E1上','E2上','E3上','E4上','V7上'])
强5 = sum(等级统计[k]['冲高5'] for k in ['E0上','E1上','E2上','E3上','E4上','V7上'])
# 中: e5~e8 + V8~V5 + 唏嘘
中总 = sum(等级统计[k]['总'] for k in ['e5中','e6下','e7忑','e8忠','E9忐','V8中','v9下','V6忐','V5忠'])
中3 = sum(等级统计[k]['冲高3'] for k in ['e5中','e6下','e7忑','e8忠','E9忐','V8中','v9下','V6忐','V5忠'])
中5 = sum(等级统计[k]['冲高5'] for k in ['e5中','e6下','e7忑','e8忠','E9忐','V8中','v9下','V6忐','V5忠'])
# 弱: v4~v0 + 屎尿
弱总 = sum(等级统计[k]['总'] for k in ['v4忑','v3忑','v2忑','v1忑','v0忑','>转空'])
弱3 = sum(等级统计[k]['冲高3'] for k in ['v4忑','v3忑','v2忑','v1忑','v0忑','>转空'])
弱5 = sum(等级统计[k]['冲高5'] for k in ['v4忑','v3忑','v2忑','v1忑','v0忑','>转空'])

for label, total, h3, h5 in [('强(金+E0~E4+V7)', 强总, 强3, 强5),
                               ('中(银唏嘘+e5~E9+V8~V5)', 中总, 中3, 中5),
                               ('弱(屎尿+v4~v0+转空)', 弱总, 弱3, 弱5)]:
    if total > 0:
        print(f'  {label}: n={total:,}, P>=3%={h3/total*100:.1f}%, P>=5%={h5/total*100:.1f}%')

print(f'\n{"="*80}')
print('验证完成')