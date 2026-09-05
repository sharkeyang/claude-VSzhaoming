# -*- coding: utf-8 -*-
"""
高波池_综合验证.py
==================
只跑高波池（Qic+Qim+Qit），一次遍历完成 5 个任务：
  任务1: 上符串符号统计（A/B/v/w/_ 各符号次日冲高）
  任务2: 十字星(无长上影) 样本量 + 是否需构成升连
  任务3: BSHA 深度研究 + 与管宽结合（管宽 vs BSHA 哪个重要）
  任务4: 5.4.2/5.4.3 最强信号合并，按高波池验证
  任务5: 5.2 乙(DXZA>0) 转坏数据补全
"""
import numpy as np, pandas as pd, os, glob, time, json, warnings, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}


class IncAgg:
    def __init__(self):
        self.n = 0
        self.sum_hr = 0.0
        self.n_p3 = 0
        self.n_p5 = 0

    def add(self, next_hr):
        self.n += 1
        self.sum_hr += next_hr
        if next_hr >= 3:
            self.n_p3 += 1
        if next_hr >= 5:
            self.n_p5 += 1

    def stats(self):
        if self.n == 0:
            return None
        return {'n': self.n, 'P3': self.n_p3 / self.n * 100,
                'P5': self.n_p5 / self.n * 100, '均值': self.sum_hr / self.n}


def calc_合顶天数(sf):
    if not sf or len(sf) == 0:
        return 0
    c = 0
    for ch in reversed(sf):
        if ch == 'A':
            c += 1
        else:
            break
    return c


def is_十字星(open_, close, high, low):
    body = abs(close - open_)
    full = high - low
    if full <= 0:
        return False
    return body < 0.1 * full


def is_长上影(open_, close, high, low):
    body = abs(close - open_)
    upper = high - max(close, open_)
    full = high - low
    if full <= 0:
        return False
    return upper > 2 * body and upper > 0.4 * full


def main():
    t0 = time.time()
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        board_map = json.load(f)
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)

    gb_cids = [k for k, v in board_map.items() if v in 高波池板块]
    gb_cids_set = set(gb_cids)
    print(f'高波池股票: {len(gb_cids)}', flush=True)

    agg_上符 = defaultdict(IncAgg)
    agg_十字星 = defaultdict(IncAgg)
    agg_bsha = defaultdict(IncAgg)
    agg_管宽 = defaultdict(IncAgg)
    agg_bsha_管宽 = defaultdict(IncAgg)
    agg_最强 = defaultdict(IncAgg)
    agg_乙转坏 = defaultdict(IncAgg)
    agg_乙转坏_指标 = defaultdict(IncAgg)

    gb_rows = 0
    n_files = 0

    files = [f for f in files if any(c in f for c in ['sh600004', 'sh600006', 'sh600007', 'sh600008', 'sh600012'])]
    for i, f in enumerate(files):
        if i % 500 == 0:
            print(f'  [加载] {i}/{len(files)}...', flush=True)
        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        if cidl not in gb_cids_set:
            continue
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) < 6:
                continue
        except Exception:
            continue
        n_files += 1
        n = len(df)
        gb_rows += n

        # 次日高幅 = 下一行的高幅（CSV表头[26]上身列实际是次日高幅，但用高幅下移最可靠）
        hr = pd.to_numeric(df['高幅'], errors='coerce').values
        next_hr = np.roll(hr, -1)
        next_hr[-1] = np.nan  # 最后一行无次日
        open_ = pd.to_numeric(df['开'], errors='coerce').values
        close = pd.to_numeric(df['收'], errors='coerce').values
        high = pd.to_numeric(df['高'], errors='coerce').values
        low = pd.to_numeric(df['低'], errors='coerce').values
        za = pd.to_numeric(df['日ZA'], errors='coerce').values
        zc = pd.to_numeric(df['日ZC'], errors='coerce').values
        bsha = pd.to_numeric(df['BSHA'], errors='coerce').values
        # 上符串在表头[30]层界列（CSV表头错位，层界列实际是上符串）
        shangfu = df['层界'].astype(str).values
        kuanheng = pd.to_numeric(df['宽哼JC'], errors='coerce').values
        dxab = df['DXAB'].astype(str).values
        zhupai = df['柱排'].astype(str).values
        boying = df['波型'].astype(str).values
        ying = df['盈提示'].astype(str).values
        dingxing = df['顶型'].astype(str).values
        ri等型 = df['日等型'].astype(str).values

        for j in range(n - 1):
            if np.isnan(next_hr[j]) or next_hr[j] <= -99:
                continue
            nhr = next_hr[j]
            sf = shangfu[j]
            is_touch = len(sf) > 0 and sf[-1] == 'A'
            合顶 = calc_合顶天数(sf)

            # 任务1: 上符串符号
            if len(sf) > 0:
                sym = sf[-1]
                agg_上符[(sym,)].add(nhr)
                if zc[j] > 0:
                    agg_上符[('ZC>0', sym)].add(nhr)

            # 任务2: 十字星（触顶+BSHA>=8 子集）
            if zc[j] > 0 and is_touch and bsha[j] >= 8:
                is_x = is_十字星(open_[j], close[j], high[j], low[j])
                is_ys = is_长上影(open_[j], close[j], high[j], low[j])
                if is_x and not is_ys:
                    agg_十字星[('十字星无长上影',)].add(nhr)
                    if '升' in zhupai[j]:
                        agg_十字星[('十字星+升排',)].add(nhr)
                    else:
                        agg_十字星[('十字星+非升排',)].add(nhr)
                    if j > 0 and close[j] < close[j - 1]:
                        agg_十字星[('十字星+阴柱',)].add(nhr)
                    else:
                        agg_十字星[('十字星+阳柱',)].add(nhr)
                elif is_ys:
                    agg_十字星[('长上影',)].add(nhr)
                else:
                    agg_十字星[('无形态',)].add(nhr)

            # 任务3: BSHA / 管宽 / 联合（ZC>0+触顶）
            if zc[j] > 0 and is_touch:
                b = bsha[j]
                if not np.isnan(b):
                    if b < 1:
                        agg_bsha[('BSHA0~1',)].add(nhr)
                    elif b < 2:
                        agg_bsha[('BSHA1~2',)].add(nhr)
                    elif b < 3:
                        agg_bsha[('BSHA2~3',)].add(nhr)
                    elif b < 5:
                        agg_bsha[('BSHA3~5',)].add(nhr)
                    elif b < 8:
                        agg_bsha[('BSHA5~8',)].add(nhr)
                    elif b < 10:
                        agg_bsha[('BSHA8~10',)].add(nhr)
                    else:
                        agg_bsha[('BSHA>=10',)].add(nhr)
                kh = kuanheng[j]
                if not np.isnan(kh):
                    if kh < 5:
                        agg_管宽[('管宽0~5',)].add(nhr)
                    elif kh < 10:
                        agg_管宽[('管宽5~10',)].add(nhr)
                    elif kh < 20:
                        agg_管宽[('管宽10~20',)].add(nhr)
                    elif kh < 40:
                        agg_管宽[('管宽20~40',)].add(nhr)
                    else:
                        agg_管宽[('管宽>40',)].add(nhr)
                    bkey = 'BSHA<5' if b < 5 else ('BSHA5~8' if b < 8 else 'BSHA>=8')
                    kkey = '管宽<10' if kh < 10 else ('管宽10~20' if kh < 20 else '管宽>=20')
                    agg_bsha_管宽[(bkey, kkey)].add(nhr)

            # 任务4: 最强信号（ZC>0）
            if zc[j] > 0:
                if is_touch and bsha[j] >= 8:
                    agg_最强[('触顶+BSHA>=8',)].add(nhr)
                if '乙' in dxab[j] and is_touch and bsha[j] >= 5:
                    agg_最强[('乙+触顶+BSHA>=5',)].add(nhr)
                if is_touch and 合顶 >= 3:
                    agg_最强[('触顶+合顶>=3',)].add(nhr)
                if is_touch and bsha[j] >= 8 and 合顶 >= 3:
                    agg_最强[('触顶+BSHA>=8+合顶>=3',)].add(nhr)

            # 任务5: 乙(DXZA>0) 转坏
            if '乙' in dxab[j] and za[j] > 0:
                if j + 1 < n - 1:
                    next_dxab = dxab[j + 1]
                    next_za = za[j + 1]
                    still_乙 = ('乙' in next_dxab) and next_za > 0
                    if not still_乙:
                        agg_乙转坏[('乙转坏',)].add(nhr)
                        agg_乙转坏_指标[('柱排', zhupai[j])].add(nhr)
                        agg_乙转坏_指标[('波型', boying[j][:2])].add(nhr)
                        agg_乙转坏_指标[('盈提示', ying[j])].add(nhr)
                        agg_乙转坏_指标[('顶型', dingxing[j])].add(nhr)
                        agg_乙转坏_指标[('日等型', ri等型[j])].add(nhr)
                    else:
                        agg_乙转坏[('乙保持',)].add(nhr)

    print(f'  高波池文件: {n_files}, 行: {gb_rows:,}', flush=True)

    out = []
    out.append('=' * 80)
    out.append('高波池综合验证（Qic+Qim+Qit）')
    out.append('=' * 80)
    out.append(f'高波池文件: {n_files}, 样本行: {gb_rows:,}')
    out.append('')

    def dump(title, agg, keys):
        out.append(f'【{title}】')
        out.append(f'{"条件":<28s}  {"P3":>7s}  {"P5":>7s}  {"均值":>7s}  {"样本":>10s}')
        out.append('-' * 65)
        for k in keys:
            # key 可能是字符串或元组，统一转元组
            kk = (k,) if isinstance(k, str) else k
            s = agg[kk].stats()
            if s:
                out.append(f'{str(k):<28s}  {s["P3"]:>6.1f}%  {s["P5"]:>6.1f}%  {s["均值"]:>6.2f}  {s["n"]:>10,d}')
        out.append('')

    dump('任务1: 上符串符号（全样本）', agg_上符, ['A', 'B', 'v', 'w', '_'])
    dump('任务1: 上符串符号（ZC>0）', agg_上符, [('ZC>0', 'A'), ('ZC>0', 'B'), ('ZC>0', 'v'), ('ZC>0', 'w'), ('ZC>0', '_')])

    dump('任务2: 十字星（触顶+BSHA>=8 子集）', agg_十字星,
         ['十字星无长上影', '十字星+升排', '十字星+非升排', '十字星+阴柱', '十字星+阳柱', '长上影', '无形态'])

    dump('任务3: BSHA 分级（ZC>0+触顶）', agg_bsha,
         ['BSHA0~1', 'BSHA1~2', 'BSHA2~3', 'BSHA3~5', 'BSHA5~8', 'BSHA8~10', 'BSHA>=10'])
    dump('任务3: 管宽分级（ZC>0+触顶）', agg_管宽,
         ['管宽0~5', '管宽5~10', '管宽10~20', '管宽20~40', '管宽>40'])
    out.append('【任务3: BSHA×管宽 联合（ZC>0+触顶）】')
    hdr = 'BSHA\\管宽'
    out.append(f'{hdr:<20s}  {"管宽<10":>12s}  {"管宽10~20":>12s}  {"管宽>=20":>12s}')
    out.append('-' * 60)
    for bkey in ['BSHA<5', 'BSHA5~8', 'BSHA>=8']:
        row = [f'{bkey:<20s}']
        for kkey in ['管宽<10', '管宽10~20', '管宽>=20']:
            s = agg_bsha_管宽[(bkey, kkey)].stats()
            row.append(f'{s["P3"]:>7.1f}%({s["n"]:>6,d})' if s else f'{"-":>12s}')
        out.append('  '.join(row))
    out.append('')

    dump('任务4: 最强信号（ZC>0）', agg_最强,
         ['触顶+BSHA>=8', '乙+触顶+BSHA>=5', '触顶+合顶>=3', '触顶+BSHA>=8+合顶>=3'])

    dump('任务5: 乙(DXZA>0) 转坏', agg_乙转坏, ['乙转坏', '乙保持'])
    out.append('【任务5: 乙转坏 微观指标映射】')
    for dim in ['柱排', '波型', '盈提示', '顶型', '日等型']:
        out.append(f'--- {dim} ---')
        out.append(f'{"值":<20s}  {"P3":>7s}  {"样本":>10s}')
        out.append('-' * 40)
        items = [(k[1], s) for k, s in agg_乙转坏_指标.items() if k[0] == dim and s.n > 0]
        items.sort(key=lambda x: -x[1].n)
        for val, s in items[:15]:
            st = s.stats()
            if st:
                out.append(f'{str(val):<20s}  {st["P3"]:>6.1f}%  {st["n"]:>10,d}')
        out.append('')

    result = '\n'.join(out)
    print(result)
    out_path = '____temp/高波池_综合验证结果.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'\n结果已保存: {out_path}')
    print(f'耗时: {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
