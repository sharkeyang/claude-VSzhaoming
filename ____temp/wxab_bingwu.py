# -*- coding: utf-8 -*-
import pandas as pd, os, glob, warnings
warnings.simplefilter('ignore')

WK_DIR = 'D:\\@VSwork\\VS昭明计划VBA优化\\昭明算展\\谕组周'
wfiles = sorted(glob.glob(os.path.join(WK_DIR, '谕组周_*.csv')))
print('文件:', len(wfiles), flush=True)

dfs = []
for i, f in enumerate(wfiles):
    if i % 500 == 0: print(' 读入:', i, '/', len(wfiles), flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) >= 10:
            df['fid'] = i
            dfs.append(df)
    except: continue
wk = pd.concat(dfs, ignore_index=True)
print('总行:', len(wk), flush=True)

def q(wx):
    if pd.isna(wx): return 'X'
    s = str(wx)
    if len(s) >= 2:
        return s[1]  # 第二字永远是护型: 甲/乙/丙/丁/戊/己
    return 'X'

wk['护型'] = wk['WXAB'].apply(q)
wk['下周护型'] = wk.groupby('fid')['WXAB'].shift(-1).apply(q)
wk = wk[wk['护型'] != 'X']
print('有护型:', len(wk), flush=True)

out = open('D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\WXAB_丙戊分析.txt', 'w', encoding='utf-8')

def fmt(name, mask, out):
    g = wk[mask]
    n = len(g)
    if n < 100: return
    nxt = g['下周护型'].value_counts()
    ok = sum(nxt.get(c, 0) for c in '甲乙己') / n * 100
    bad = sum(nxt.get(c, 0) for c in '丙丁戊') / n * 100
    out.write(name.ljust(30) + ' n=' + str(n) + ' 下周甲乙己=' + format(ok, '.1f') + '% 丙丁戊=' + format(bad, '.1f') + '%\n')

out.write('=' * 60 + '\n')
out.write('WXAB护型 下周转好概率\n')
out.write('=' * 60 + '\n\n')

out.write('一、丙-甲乙己\n')
fmt('丙-整体', wk['护型'] == '丙', out)
fmt('丙+ZA>0', (wk['护型'] == '丙') & (wk['ZA周'] > 0), out)
fmt('丙+ZA<=0', (wk['护型'] == '丙') & (wk['ZA周'] <= 0), out)
fmt('丙+ZC>0', (wk['护型'] == '丙') & (wk['ZC周'] > 0), out)

out.write('\n二、戊-甲乙己\n')
fmt('戊-整体', wk['护型'] == '戊', out)
fmt('戊+ZA>0', (wk['护型'] == '戊') & (wk['ZA周'] > 0), out)
fmt('戊+ZA<=0', (wk['护型'] == '戊') & (wk['ZA周'] <= 0), out)
fmt('戊+ZC>0', (wk['护型'] == '戊') & (wk['ZC周'] > 0), out)

out.write('\n三、丁-甲乙己（对比）\n')
fmt('丁-整体', wk['护型'] == '丁', out)
fmt('丁+ZA>0', (wk['护型'] == '丁') & (wk['ZA周'] > 0), out)

out.write('\n四、甲乙己 baseline\n')
for c in '甲乙己':
    fmt(c + '-保持', wk['护型'] == c, out)

out.write('\n五、丙+ZA分级\n')
for za in [-2, -1, 0, 1, 2, 3, 5]:
    m = (wk['护型'] == '丙') & (wk['ZA周'] == za)
    n = m.sum()
    if n >= 50:
        g = wk[m]
        nxt = g['下周护型'].value_counts()
        ok = sum(nxt.get(c, 0) for c in '甲乙己') / n * 100
        out.write('  丙+ZA=' + str(za).rjust(2) + ': n=' + str(n) + ' 下周甲乙己=' + format(ok, '.1f') + '%\n')

out.write('\n六、戊+ZA分级\n')
for za in [-2, -1, 0, 1, 2, 3, 5]:
    m = (wk['护型'] == '戊') & (wk['ZA周'] == za)
    n = m.sum()
    if n >= 50:
        g = wk[m]
        nxt = g['下周护型'].value_counts()
        ok = sum(nxt.get(c, 0) for c in '甲乙己') / n * 100
        out.write('  戊+ZA=' + str(za).rjust(2) + ': n=' + str(n) + ' 下周甲乙己=' + format(ok, '.1f') + '%\n')

out.write('\n七、丙/戊 下周具体转化\n')
for label in ['丙', '戊']:
    g = wk[wk['护型'] == label]
    n = len(g)
    nxt = g['下周护型'].value_counts()
    out.write(label + '->下周:\n')
    for c in '甲乙丙丁戊己':
        p = nxt.get(c, 0) / n * 100 if n > 0 else 0
        if p > 1:
            out.write('  ->' + c + ': ' + format(p, '.1f') + '%\n')

out.close()
print('完成')