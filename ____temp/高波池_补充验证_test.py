# -*- coding: utf-8 -*-
"""高波池_补充验证.py 跑高波池全量补齐5.4.1/5.4.3/5.8.1/5.8.2/5.10数据"""
import numpy as np, pandas as pd, os, glob, time, json, warnings, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
目标板块 = {'Qic', 'Qim', 'Qit'}
class IncAgg:
    def __init__(self):
        self.n = 0; self.sum_hr = 0.0; self.n_p3 = 0; self.n_p5 = 0
    def add(self, next_hr):
        self.n += 1; self.sum_hr += next_hr
        if next_hr >= 3: self.n_p3 += 1
        if next_hr >= 5: self.n_p5 += 1
    def stats(self):
        if self.n == 0: return None
        return {'n': self.n, 'P3': self.n_p3/self.n*100, 'P5': self.n_p5/self.n*100, '均值': self.sum_hr/self.n}
def calc_合顶天数(sf):
    if not sf or len(sf) == 0: return 0
    c = 0
    for ch in reversed(sf):
        if ch == 'A': c += 1
        else: break
    return c
def 判K线(o, c, h, l, pc):
    body = abs(c - o); full = h - l
    if full <= 0: return '无'
    upper = h - max(o, c)
    if body < 0.1 * full:
        if upper > 2 * body and upper > 0.4 * full: return '十字星+长上影'
        return '十字星'
    if upper > 2 * body and upper > 0.4 * full: return '长上影'
    if c < pc: return '阴柱'
    return '阳柱'

def main():
    t0 = time.time()
    with open(BOARD_MAP_PATH, encoding='utf-8') as f: board_map = json.load(f)
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)
    agg_合顶 = defaultdict(IncAgg); agg_合顶_zc = defaultdict(IncAgg)
    agg_护型 = defaultdict(IncAgg); agg_护型合顶 = defaultdict(IncAgg)
    agg_动态 = defaultdict(IncAgg); agg_触顶龙 = defaultdict(IncAgg)
    agg_触顶vs = defaultdict(IncAgg); agg_zc前提 = defaultdict(IncAgg)
    agg_bsha组合 = defaultdict(IncAgg); agg_失败 = defaultdict(IncAgg)
    agg_十字星 = defaultdict(IncAgg); agg_好模型 = defaultdict(IncAgg)
    n_files = 0; gb_rows = 0
    files = [f for f in files if any(c in f for c in ['sh600004', 'sh600006', 'sh600007', 'sh600008', 'sh600012'])]
    for i, f in enumerate(files):
        if i % 500 == 0: print(f'  [加载] {i}/{len(files)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) < 6: continue
        except Exception: continue
        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 目标板块: continue
        n_files += 1; gb_rows += len(df)
        hr = pd.to_numeric(df['高幅'], errors='coerce').values
        next_hr = np.roll(hr, -1); next_hr[-1] = np.nan
        open_ = pd.to_numeric(df['开'], errors='coerce').values
        close = pd.to_numeric(df['收'], errors='coerce').values
        high = pd.to_numeric(df['高'], errors='coerce').values
        low = pd.to_numeric(df['低'], errors='coerce').values
        za = pd.to_numeric(df['日ZA'], errors='coerce').values
        zc = pd.to_numeric(df['日ZC'], errors='coerce').values
        bsha = pd.to_numeric(df['BSHA'], errors='coerce').values
        shangfu = df['层界'].astype(str).values
        dxab = df['DXAB'].astype(str).values
        zhupai = df['柱排'].astype(str).values
        n = len(df)
        for j in range(n - 1):
            nhr = next_hr[j]
            if np.isnan(nhr): continue
            zc_val = zc[j]; za_val = za[j]; bsha_val = bsha[j]
            sf = shangfu[j]; ab = dxab[j]
            is_touch = len(sf) > 0 and sf[-1] == 'A'
            合顶 = calc_合顶天数(sf)
            agg_合顶[(合顶,)].add(nhr)
            if zc_val > 0: agg_合顶_zc[(合顶,)].add(nhr)
            if is_touch: agg_触顶vs[('触顶',)].add(nhr)
            else: agg_触顶vs[('非触顶',)].add(nhr)
            if zc_val > 0:
                if is_touch: agg_zc前提[('ZC>0+触顶',)].add(nhr)
                else: agg_zc前提[('ZC>0+非触顶',)].add(nhr)
            else:
                if is_touch: agg_zc前提[('ZC<=0+触顶',)].add(nhr)
                else: agg_zc前提[('ZC<=0+非触顶',)].add(nhr)
            if zc_val > 0 and is_touch:
                for h in ['乙', '甲', '己', '丙', '戊']:
                    if h in ab:
                        agg_护型[(h,)].add(nhr); break
                if '乙' in ab:
                    if 合顶 >= 2: agg_护型合顶[('乙+触顶+合顶>=2',)].add(nhr)
                    if 合顶 >= 3: agg_护型合顶[('乙+触顶+合顶>=3',)].add(nhr)
                if '甲' in ab and 合顶 >= 3: agg_护型合顶[('甲+触顶+合顶>=3',)].add(nhr)
                if '己' in ab and 合顶 >= 3: agg_护型合顶[('己+触顶+合顶>=3',)].add(nhr)
            if zc_val > 0 and is_touch:
                for h in ['乙', '甲', '己']:
                    if h in ab:
                        if 合顶 >= 3: agg_护型[(h+'+合顶>=3',)].add(nhr)
                        else: agg_护型[(h+'+合顶<3',)].add(nhr)
                        break
            if zc_val > 0:
                if '己' in ab and za_val > 0: agg_动态[('己→甲转',)].add(nhr)
                if '乙' in ab and is_touch: agg_动态[('乙+触顶',)].add(nhr)
                if '甲' in ab:
                    if 合顶 >= 3: agg_动态[('甲+合顶>=3',)].add(nhr)
                    if is_touch: agg_动态[('甲+触顶',)].add(nhr)
                    else: agg_动态[('甲+未触顶',)].add(nhr)
                if '己' in ab and is_touch: agg_动态[('己+触顶',)].add(nhr)
            if zc_val > 0 and is_touch:
                if 合顶 >= 2: agg_触顶龙[('合顶>=2(继续触顶)',)].add(nhr)
                else: agg_触顶龙[('合顶=1(刚触顶)',)].add(nhr)
            if zc_val > 0:
                if is_touch and bsha_val >= 8: agg_bsha组合[('触顶+BSHA>=8',)].add(nhr)
                if '乙' in ab and is_touch and bsha_val >= 5: agg_bsha组合[('乙+触顶+BSHA>=5',)].add(nhr)
                if '甲' in ab and is_touch and bsha_val >= 5: agg_bsha组合[('甲+触顶+BSHA>=5',)].add(nhr)
                if '己' in ab and is_touch and bsha_val >= 5: agg_bsha组合[('己+触顶+BSHA>=5',)].add(nhr)
            if is_touch and bsha_val >= 8:
                k = 判K线(open_[j], close[j], high[j], low[j], close[j-1] if j > 0 else close[j])
                agg_失败[(k,)].add(nhr); agg_失败[('全部',)].add(nhr)
                if k == '十字星': agg_失败[('十字星无长上影',)].add(nhr)
                if k == '阴柱': agg_失败[('阴柱无长上影',)].add(nhr)
                if k == '长上影': agg_失败[('长上影非阴柱',)].add(nhr)
            if zc_val > 0 and is_touch:
                k = 判K线(open_[j], close[j], high[j], low[j], close[j-1] if j > 0 else close[j])
                if k == '十字星':
                    if bsha_val < 1: agg_十字星[('BSHA0~1',)].add(nhr)
                    elif bsha_val < 2: agg_十字星[('BSHA1~2',)].add(nhr)
                    elif bsha_val < 3: agg_十字星[('BSHA2~3',)].add(nhr)
                    elif bsha_val < 4: agg_十字星[('BSHA3~4',)].add(nhr)
                    elif bsha_val < 5: agg_十字星[('BSHA4~5',)].add(nhr)
                    elif bsha_val < 6: agg_十字星[('BSHA5~6',)].add(nhr)
                    elif bsha_val < 7: agg_十字星[('BSHA6~7',)].add(nhr)
                    elif bsha_val < 8: agg_十字星[('BSHA7~8',)].add(nhr)
                    elif bsha_val < 9: agg_十字星[('BSHA8~9',)].add(nhr)
                    elif bsha_val < 10: agg_十字星[('BSHA9~10',)].add(nhr)
                    else: agg_十字星[('BSHA>=10',)].add(nhr)
                    agg_十字星[(f'合顶{合顶}',)].add(nhr)
                    if '升' in zhupai[j]: agg_十字星[('十字星+升排',)].add(nhr)
                    else: agg_十字星[('十字星+非升排',)].add(nhr)
                    if bsha_val >= 8 and 合顶 >= 3: agg_十字星[('十字星+BSHA>=8+合顶>=3',)].add(nhr)
                    if bsha_val >= 10: agg_十字星[('十字星+BSHA>=10',)].add(nhr)
            if zc_val > 0:
                is_好模型 = ('甲' in ab or '乙' in ab or '己' in ab)
                if is_好模型:
                    agg_好模型[('好模型基准',)].add(nhr)
                    if bsha_val >= 5: agg_好模型[('好模型+BSHA5',)].add(nhr)
                    if is_touch: agg_好模型[('好模型+触顶A',)].add(nhr)
                    if is_touch and bsha_val >= 5: agg_好模型[('好模型+触顶A+BSHA5',)].add(nhr)
                    if is_touch and 合顶 >= 3: agg_好模型[('好模型+触顶A+合顶>=3',)].add(nhr)
                if is_touch and bsha_val >= 8:
                    k = 判K线(open_[j], close[j], high[j], low[j], close[j-1] if j > 0 else close[j])
                    if k == '十字星':
                        agg_好模型[('触顶A+BSHA8+十字星',)].add(nhr)
                        if is_好模型: agg_好模型[('好模型+触顶A+BSHA8+十字星',)].add(nhr)
                        if '乙' in ab: agg_好模型[('乙+触顶A+BSHA8+十字星',)].add(nhr)
                        if 合顶 >= 3: agg_好模型[('触顶A+BSHA8+合顶>=3+十字星',)].add(nhr)
                    agg_好模型[('触顶A+BSHA8(无十字星)',)].add(nhr)
                if not is_touch and bsha_val >= 8:
                    k = 判K线(open_[j], close[j], high[j], low[j], close[j-1] if j > 0 else close[j])
                    if k == '十字星': agg_好模型[('不触顶+BSHA8+十字星',)].add(nhr)
    print(f'  高波池文件: {n_files}, 行: {gb_rows:,}', flush=True)

    out = []
    out.append('='*70); out.append('高波池补充验证'); out.append('='*70)
    out.append(f'高波池文件: {n_files}, 样本行: {gb_rows:,}'); out.append('')
    def dump(title, agg, keys):
        out.append(f'【{title}】')
        out.append(f'{"条件":<26s}  {"P3":>7s}  {"P5":>7s}  {"均值":>7s}  {"样本":>10s}')
        out.append('-'*62)
        for k in keys:
            kk = (k,) if not isinstance(k, tuple) else k
            s = agg[kk].stats()
            if s: out.append(f'{str(k):<26s}  {s["P3"]:>6.1f}%  {s["P5"]:>6.1f}%  {s["均值"]:>6.2f}  {s["n"]:>10,d}')
        out.append('')
    dump('5.4.1 合顶天数(全)', agg_合顶, [0,1,2,3,4,5])
    dump('5.4.1 合顶天数(ZC>0)', agg_合顶_zc, [0,1,2,3,4,5])
    dump('5.4.1 护型状态(ZC>0+触顶)', agg_护型, ['乙+合顶>=3','乙+合顶<3','甲+合顶>=3','甲+合顶<3','己+合顶>=3','己+合顶<3'])
    dump('5.4.1 动态状态转移(ZC>0)', agg_动态, ['己→甲转','乙+触顶','甲+合顶>=3','甲+触顶','己+触顶','甲+未触顶'])
    dump('5.4.1 触顶龙(ZC>0+触顶)', agg_触顶龙, ['合顶>=2(继续触顶)','合顶=1(刚触顶)'])
    dump('5.4.3 触顶vs非触顶', agg_触顶vs, ['触顶','非触顶'])
    dump('5.4.3 ZC前提', agg_zc前提, ['ZC>0+触顶','ZC>0+非触顶','ZC<=0+触顶','ZC<=0+非触顶'])
    dump('5.4.3 护型排序(ZC>0+触顶)', agg_护型, ['乙','甲','己','丙','戊'])
    dump('5.4.3 护型×合顶(ZC>0+触顶)', agg_护型合顶, ['乙+触顶+合顶>=2','乙+触顶+合顶>=3','甲+触顶+合顶>=3','己+触顶+合顶>=3'])
    dump('5.4.3 BSHA组合(ZC>0)', agg_bsha组合, ['触顶+BSHA>=8','乙+触顶+BSHA>=5','甲+触顶+BSHA>=5','己+触顶+BSHA>=5'])
    dump('5.8.1 失败情形(触顶+BSHA>=8)', agg_失败, ['全部','长上影','阴柱','十字星','十字星无长上影','阴柱无长上影','长上影非阴柱','十字星+长上影','阳柱'])
    dump('5.8.2 十字星+BSHA', agg_十字星, ['BSHA0~1','BSHA1~2','BSHA2~3','BSHA3~4','BSHA4~5','BSHA5~6','BSHA6~7','BSHA7~8','BSHA8~9','BSHA9~10','BSHA>=10'])
    dump('5.8.2 十字星+合顶', agg_十字星, ['合顶1','合顶2','合顶3','合顶4','合顶5'])
    dump('5.8.2 十字星+升排', agg_十字星, ['十字星+升排','十字星+非升排'])
    dump('5.8.2 十字星联合', agg_十字星, ['十字星+BSHA>=8+合顶>=3','十字星+BSHA>=10'])
    dump('5.10 好模型 vs 触顶', agg_好模型, ['好模型基准','好模型+BSHA5','好模型+触顶A','好模型+触顶A+BSHA5','好模型+触顶A+合顶>=3','触顶A+BSHA8+十字星','好模型+触顶A+BSHA8+十字星','乙+触顶A+BSHA8+十字星','触顶A+BSHA8+合顶>=3+十字星','触顶A+BSHA8(无十字星)','不触顶+BSHA8+十字星'])

    result = '\n'.join(out)
    print(result)
    out_path = '____temp/高波池_补充验证结果.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'\n结果已保存: {out_path}')
    print(f'耗时: {time.time()-t0:.0f}s', flush=True)

if __name__ == '__main__':
    main()
