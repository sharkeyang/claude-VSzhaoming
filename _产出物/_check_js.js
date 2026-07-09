
const SIYU_COLORS = {"多长":"#00c853","多被":"#ffc107","空看":"#5c2d82","空长":"#d32f2f"};
const AMT_WAN_THRESHOLD = 5;

function fmtAmt(amt) {
    return amt < AMT_WAN_THRESHOLD ? (amt*10000).toFixed(0) : amt.toFixed(1)+'w';
}

function badge(siyu) {
    const c = SIYU_COLORS[siyu] || '#666';
    const icon = {'多长':'🟢','多被':'🟡','空看':'🟣','空长':'🔴'}[siyu] || '⚪';
    return '<span class="badge" style="background:'+c+'">'+icon+' '+siyu+'</span>';
}

function parseCC(ccStr) {
    const r = {};
    if (!ccStr) return r;
    const parts = ccStr.split(' | ');
    ['四域','日级别','波形','机阱','冲高'].forEach((k,i)=>{ if(i<parts.length) r[k]=parts[i]; });
    if(parts[0]) { const m=parts[0].match(/四域=(\S+)/); if(m) r._四域=m[1]; }
    if(parts[1]) { ['仓日','日段','日信号'].forEach(k=>{ const m=parts[1].match(new RegExp(k+'=(\\S+)')); if(m) r['_'+k]=m[1]; }); }
    return r;
}

function renderStrategies(strats) {
    return strats.map(s=>'<div class="strat-item">'+s+'</div>').join('');
}

function renderQuestions(cc) {
    const qs = [];
    const sy = cc._四域||'', rd=cc._日段||'', cr=cc._仓日||'';
    if(sy=='多长') qs.push(['四域多长','✅ 趋势完整，持有']);
    else if(sy=='多被') qs.push(['四域多被','⚠️ 被动跟随，等转强']);
    else if(sy=='空看') qs.push(['四域空看','🟣 空头观望']);
    else if(sy=='空长') qs.push(['四域空长','🔴 空头趋势']);
    if(rd=='持主') qs.push(['日段持主','🔹 持主，关注止盈']);
    else if(rd=='卖浮') qs.push(['日段卖浮','🟠 浮仓卖出']);
    else if(!rd&&cr=='无') qs.push(['日段空','⚪ DJE之下']);
    if(cr=='无') qs.push(['仓日无','📉 无均线支撑']);
    return qs.map(q=>'<div class="q-item"><span class="q-type">'+q[0]+'</span> '+q[1]+'</div>').join('');
}

// ECharts 暗色主题
const DARK_THEME = {
    backgroundColor: 'transparent',
    textStyle: {color:'#b0bec5'},
    xAxis: {axisLine:{lineStyle:{color:'#1a2540'}}, axisLabel:{color:'#546e7a',fontSize:9}},
    yAxis: {axisLine:{lineStyle:{color:'#1a2540'}}, axisLabel:{color:'#546e7a',fontSize:9}},
    splitLine: {lineStyle:{color:'#0d1520'}},
};

let pieChart = null;
let intradayCharts = {};

function initCharts() {
    try {
        if (typeof echarts !== 'undefined') {
            pieChart = echarts.init(document.getElementById('pieChart'), 'dark', {renderer:'canvas'});
        }
    } catch(e) { console.log('ECharts init error:', e); }
}

function updatePie(positions) {
    if (!pieChart) return;
    const bySy = {};
    positions.forEach(p => {
        const cc = parseCC(p.策传);
        const sy = cc._四域 || p.四域周 || '其他';
        bySy[sy] = (bySy[sy]||0) + Math.abs(p.金额||0);
    });
    const total = Object.values(bySy).reduce((a,b)=>a+b,0);
    const order = ['多长','多被','空看','空长'];
    const data = order.filter(k => bySy[k]).map(k => ({
        name: k, value: bySy[k],
        itemStyle: {color: SIYU_COLORS[k]||'#666'}
    }));
    pieChart.setOption({
        tooltip: {trigger:'item', formatter:'{b}: {c}万 ({d}%)'},
        legend: {
            orient:'vertical', left:'5%', top:'center',
            textStyle:{color:'#b0bec5',fontSize:10},
            itemWidth:10, itemHeight:10,
            formatter: function(name) {
                const v = bySy[name]||0;
                const pct = total>0 ? (v/total*100).toFixed(0) : 0;
                return name + '  ' + pct + '%(' + v.toFixed(0) + 'w)';
            }
        },
        series: [{
            type:'pie', radius:['30%','65%'],
            center:['65%','50%'],
            data: data,
            label: {show:false},
            labelLine: {show:false},
            itemStyle: {borderColor:'#0a0e17',borderWidth:1},
        }],
        backgroundColor: 'transparent',
    });
}

function updateIntraday(containerId, intradayData, mp) {
    const dom = document.getElementById(containerId);
    if (!dom) return;
    // 清除旧内容
    dom.innerHTML = '';
    let chart = intradayCharts[containerId];
    if (!chart) {
        chart = echarts.init(dom, 'dark', {renderer:'canvas'});
        intradayCharts[containerId] = chart;
    }
    if (!intradayData || intradayData.length === 0) {
        dom.innerHTML = '<div class="chart-placeholder" style="padding:50px 10px;text-align:center;color:#546e7a;font-size:11px">暂无分时数据</div>';
        return;
    }
    const times = intradayData.map(d => d.t.slice(11,16));
    const prices = intradayData.map(d => d.p);
    const volumes = intradayData.map(d => d.v);
    const zs = mp.昨收 || 0;
    const zg = mp.最高 || Math.max(...prices);
    const zd = mp.最低 || Math.min(...prices);
    const lastPx = prices[prices.length-1] || 0;
    const isUp = lastPx >= zs;

    chart.setOption({
        tooltip: {
            trigger:'axis',
            axisPointer:{type:'cross'},
            formatter: function(params) {
                const p = params[0];
                const chg = zs>0 ? ((p.value - zs) / zs * 100) : 0;
                const sign = chg>=0 ? '+' : '';
                return p.axisValue + '<br/>价格: ' + p.value.toFixed(2) +
                    '  <span style="color:'+(chg>=0?'#ef5350':'#26c6da')+'">' + sign + chg.toFixed(2) + '%</span>';
            }
        },
        grid: [{left:'3%',right:'3%',top:'8%',bottom:'8%'}],
        xAxis: [{
            type:'category', data:times,
            axisLabel:{fontSize:8},
            splitLine:{show:false},
        }],
        yAxis: [{
            type:'value',
            splitNumber:3, axisLabel:{fontSize:8, formatter: function(v){return (v - zs).toFixed(1);}},
            splitLine:{lineStyle:{color:'#0d1520'}},
            // 以昨收为基准居中
            min: zs>0 ? Math.min(zd||zs, zs) - Math.abs(zg||zs - (zd||zs)) * 0.03 : undefined,
            max: zs>0 ? Math.max(zg||zs, zs) + Math.abs(zg||zs - (zd||zs)) * 0.03 : undefined,
        }],
        series: [{
            name:'价格', type:'line', data:prices,
            smooth:true, showSymbol:false,
            lineStyle:{width:1.5, color: isUp?'#ef5350':'#26c6da'},
            areaStyle:{color: isUp?'rgba(239,83,80,0.08)':'rgba(38,198,218,0.08)'},
            markLine: zs>0 ? {
                silent:true, data:[{
                    yAxis:zs, label:{formatter:'昨收 '+zs.toFixed(2),fontSize:9,color:'#546e7a'},
                    lineStyle:{color:'#546e7a',type:'dashed',width:0.8}
                }]
            } : undefined,
        }],
        backgroundColor: 'transparent',
    });
    chart.resize();
}

function updateCard(p, mp, intraday) {
    const cc = parseCC(p.策传);
    const sy = cc._四域 || p.四域周 || '';
    const code = p.code;
    const zx = mp.最新价||0, chg = mp.涨跌幅||0;
    const zs = mp.昨收||0, jk= mp.今开||0, zg=mp.最高||0, zd=mp.最低||0;
    const score = (()=>{
        let s=0;
        if(sy=='多长') s=50; else if(sy=='多被') s=25; else if(sy=='空看') s=15; else if(sy=='空长') s=5;
        const rd=cc._日段||'';
        if(rd=='持主') s+=20; else if(rd=='持被') s+=10; else if(rd=='卖浮') s+=5;
        if(cc._仓日&&cc._仓日!='无') s+=15;
        return Math.min(s,100);
    })();
    const qHtml = '<div class="questions">'+renderQuestions(cc)+'</div>';
    const strat = renderStrategies(['🐵 猴市：见好就收',
        zx>jk?'📈 收涨'+chg.toFixed(1)+'%':'📉 收跌'+chg.toFixed(1)+'%',
        sy=='多长'?'✅ 持有':(sy=='空长'?'🔴 逢高减仓':'⚠️ 观望')]);
    const chartId = 'chart_'+code.replace(/[^a-zA-Z0-9]/g,'_');
    const dateStr = intraday && intraday.length>0 ? intraday[0].t.slice(0,10) : '';

    return '<div class="card card-'+sy+'">'+
        '<div class="card-top">'+
            '<div class="row1">'+
                '<span class="card-name">'+p.name+'</span>'+
                '<span class="card-code">'+code+'</span>'+
                '<span class="tag-dense">板块:'+(p.hanglang||'—')+'</span>'+
                '<span class="card-tag">'+p.cangzhu+'</span>'+
                '<span class="tag-dense">金额:'+fmtAmt(p.金额||0)+'</span>'+
                '<span class="tag-dense">股数:'+(p.股数||0).toFixed(0)+'</span>'+
                '<span class="tag-dense">成本:'+(p.成本||0).toFixed(1)+'</span>'+
                '<span class="tag-dense">肉垫:'+(p.肉垫||0).toFixed(0)+'</span>'+
            '</div>'+
            '<div class="row2">'+badge(sy)+'<span class="score-badge">策分:'+score+'</span></div>'+
        '</div>'+
        '<div class="card-body">'+
            '<div class="card-left">'+
                '<div class="info-title">💡 需应对问题</div>'+qHtml+
                '<div class="info-title" style="margin-top:6px">📋 8项策传映射</div>'+
                '<table class="cc-table">'+
                    '<tr><td class="cc-num">①</td><td class="cc-label">四域</td><td class="cc-val">'+(cc.四域||'').slice(0,60)+'</td></tr>'+
                    '<tr><td class="cc-num">②</td><td class="cc-label">日级</td><td class="cc-val">'+(cc.日级别||'').slice(0,55)+'</td></tr>'+
                    '<tr><td class="cc-num">③</td><td class="cc-label">波形</td><td class="cc-val">'+(cc.波形||'').slice(0,65)+'</td></tr>'+
                    '<tr><td class="cc-num">④</td><td class="cc-label">机阱</td><td class="cc-val">'+(cc.机阱||'').slice(0,50)+'</td></tr>'+
                    '<tr><td class="cc-num">⑤</td><td class="cc-label">冲高</td><td class="cc-val">'+(cc.冲高||'').slice(0,55)+'</td></tr>'+
                    '<tr><td class="cc-num">⑥</td><td class="cc-label">策分</td><td class="cc-val">'+score+'分</td></tr>'+
                '</table>'+
                '<div class="info-title" style="margin-top:6px">🎯 走势应对策略</div>'+
                '<div class="strat-box">'+strat+'</div>'+
            '</div>'+
            '<div class="card-right">'+
                '<div class="info-title">📊 走势信息</div>'+
                '<table class="quote-table">'+
                    '<tr><td>昨收</td><td>'+zs.toFixed(2)+'</td><td>今开</td><td>'+jk.toFixed(2)+'</td></tr>'+
                    '<tr><td>最高</td><td class="red">'+zg.toFixed(2)+'</td><td>最低</td><td class="green">'+zd.toFixed(2)+'</td></tr>'+
                    '<tr><td>最新</td><td class="'+(chg>=0?'red':'green')+'">'+zx.toFixed(2)+'</td><td>涨跌</td><td class="'+(chg>=0?'red':'green')+'">'+chg.toFixed(2)+'%</td></tr>'+
                '</table>'+
                '<div class="info-title" style="margin-top:6px">📈 当日分时走势'+(dateStr?' ('+dateStr+')':'')+'</div>'+
                '<div class="chart-wrap" id="'+chartId+'"></div>'+
            '</div>'+
        '</div>'+
    '</div>';
}

function updateIndexCard(p, mp, intraday) {
    const cc = parseCC(p.策传);
    const sy = cc._四域 || p.四域周 || '';
    const code = p.code;
    const zx = mp.最新价||0, chg=mp.涨跌幅||0;
    const chartId = 'idxchart_'+code.replace(/[^a-zA-Z0-9]/g,'_');
    const dateStr = intraday && intraday.length>0 ? intraday[0].t.slice(0,10) : '';

    return '<div class="card card-'+sy+'" style="margin-bottom:6px">'+
        '<div class="card-body">'+
            '<div class="card-left">'+
                '<div class="row1">'+
                    '<span class="card-name">'+p.name+'</span>'+
                    '<span class="card-code">'+code+'</span>'+
                '</div>'+
                '<div class="row2">'+badge(sy)+'</div>'+
                '<table class="quote-table">'+
                    '<tr><td>最新</td><td class="'+(chg>=0?'red':'green')+'">'+zx.toFixed(2)+'</td><td>涨跌</td><td class="'+(chg>=0?'red':'green')+'">'+chg.toFixed(2)+'%</td></tr>'+
                '</table>'+
            '</div>'+
            '<div class="card-right">'+
                '<div class="chart-wrap" id="'+chartId+'" style="height:80px"></div>'+
            '</div>'+
        '</div>'+
    '</div>';
}

function updateDashboard(data) {
    if (!data || !data.positions) return;
    const {positions, indices, market_prices, intraday, watch_rules, total_amt, total_profit, timestamp} = data;
    const mp = market_prices || {};
    const id = intraday || {};

    // 顶栏
    document.getElementById('headerInfo').innerHTML =
        '<span class="meta-item">🕒 '+timestamp+'</span>'+
        '<span class="meta-item">💰 '+(total_amt||0).toFixed(0)+'万</span>'+
        '<span class="meta-item">📊 盈亏: <span class="'+(total_profit<0?'red':'green')+'">'+(total_profit||0).toFixed(0)+'</span></span>'+
        '<span class="meta-item">📈 '+positions.length+' 只</span>';

    // 饼图
    updatePie(positions);

    // 组合概览
    const dailyPnl = positions.reduce((s,p)=>{const m=mp[p.code]||{};return s+Math.abs(p.金额||0)*((m.涨跌幅||0)/100);},0);
    document.getElementById('statsSection').style.display='';
    document.getElementById('statsGrid').innerHTML =
        '<div class="s-item"><label>持仓</label><span>'+positions.length+' 只</span></div>'+
        '<div class="s-item"><label>总市值</label><span class="green">'+(total_amt||0).toFixed(0)+'万</span></div>'+
        '<div class="s-item"><label>累计盈亏</label><span class="'+(total_profit<0?'red':'green')+'">'+(total_profit||0).toFixed(0)+'</span></div>'+
        '<div class="s-item"><label>当日浮动</label><span class="'+(dailyPnl<0?'red':'green')+'">'+dailyPnl.toFixed(1)+'万</span></div>'+
        '<div class="s-item"><label>状态</label><span class="tag-orange" style="background:#e65100;color:#fff;padding:0 6px;border-radius:3px;font-size:11px">猴市 🐵</span></div>'+
        '<div class="s-item"><label>策略</label><span class="tag-blue" style="background:#1565c0;color:#fff;padding:0 6px;border-radius:3px;font-size:11px">见好就收</span></div>';

    // 板块集中度
    const boardW = {};
    positions.forEach(p => {
        const hl = p.hanglang;
        if(!hl) return;
        boardW[hl] = (boardW[hl]||0) + Math.abs(p.金额||0)/(total_amt||1)*100;
    });
    const topBoards = Object.entries(boardW).sort((a,b)=>b[1]-a[1]).slice(0,5);
    document.getElementById('boardSection').style.display='';
    document.getElementById('boardList').innerHTML = topBoards.map(([b,pct])=>
        '<div class="board-item">'+(pct>25?'⚠️':'📊')+' '+b+': '+pct.toFixed(0)+'%</div>'
    ).join('');

    // 策卡
    document.getElementById('posCount').textContent = positions.length+' 只';
    const posCardsHtml = positions.map(p => {
        const ch = updateCard(p, mp[p.code]||{}, id[p.code]||[]);
        return ch + '<div class="card-divider"></div>';
    }).join('');
    document.getElementById('posCards').innerHTML = posCardsHtml;

    // 核心宽基
    const core = (indices&&indices.core) || [];
    document.getElementById('coreCount').textContent = core.length+' 只';
    const coreHtml = core.map(p => {
        const ch = updateIndexCard(p, mp[p.code]||{}, id[p.code]||[]);
        return ch;
    }).join('');
    document.getElementById('coreCards').innerHTML = coreHtml;

    // 重点行业
    const industry = (indices&&indices.industry) || [];
    const keyInds = ['证券','半导体','白酒','银行'];
    const keyEtfs = industry.filter(i => keyInds.some(k=>i.name.includes(k)));
    if (keyEtfs.length > 0) {
        document.getElementById('keyIndustrySection').style.display='';
        document.getElementById('keyCount').textContent = keyEtfs.length+' 只';
        const keyHtml = keyEtfs.map(p => updateIndexCard(p, mp[p.code]||{}, id[p.code]||[])).join('');
        document.getElementById('keyCards').innerHTML = keyHtml;
    }

    // 初始化所有分时图（等DOM渲染完成后统一执行）
    function initAllCharts() {
        // 持仓
        positions.forEach(p => {
            const e = document.getElementById('chart_'+p.code.replace(/[^a-zA-Z0-9]/g,'_'));
            if(e) updateIntraday(e.id, id[p.code]||[], mp[p.code]||{});
        });
        // 宽基
        core.forEach(p => {
            const e = document.getElementById('idxchart_'+p.code.replace(/[^a-zA-Z0-9]/g,'_'));
            if(e) updateIntraday(e.id, id[p.code]||[], mp[p.code]||{});
        });
        // 重点行业
        keyEtfs.forEach(p => {
            const e = document.getElementById('idxchart_'+p.code.replace(/[^a-zA-Z0-9]/g,'_'));
            if(e) updateIntraday(e.id, id[p.code]||[], mp[p.code]||{});
        });
    }
    // 先等200ms让DOM完成，如果还有没渲染的，用requestAnimationFrame轮询
    setTimeout(initAllCharts, 200);
    // 保险：500ms后再检查一次，补漏
    setTimeout(() => {
        document.querySelectorAll('.chart-wrap').forEach(el => {
            // 如果chart-wrap还是空的，尝试初始化
            if(el.children.length === 0 || el.innerHTML.trim() === '') {
                const id = el.id;
                // 从id反查code
                if(id.startsWith('chart_')) {
                    const p = positions.find(p2 => 'chart_'+p2.code.replace(/[^a-zA-Z0-9]/g,'_')===id);
                    if(p) updateIntraday(id, id[p.code]||[], mp[p.code]||{});
                } else if(id.startsWith('idxchart_')) {
                    const allIdx = [...core, ...keyEtfs];
                    const p = allIdx.find(p2 => 'idxchart_'+p2.code.replace(/[^a-zA-Z0-9]/g,'_')===id);
                    if(p) updateIntraday(id, id[p.code]||[], mp[p.code]||{});
                }
            }
        });
    }, 800);

    // 窗口resize时重绘图表
    window.addEventListener('resize', function() {
        Object.values(intradayCharts).forEach(c => { try{c.resize()}catch(e){} });
        try{pieChart.resize()}catch(e){}
    });

    // 盯盘
    if (watch_rules && watch_rules.length > 0) {
        document.getElementById('ruleCount').textContent = watch_rules.length+' 条';
        document.getElementById('rulesBox').innerHTML = watch_rules.map(r =>
            '<div class="rule-item"><span class="rule-type">'+r.type+'</span> '+r.msg+'</div>'
        ).join('');
    }

    // 其他指数
    const otherIdx = (industry||[]).filter(i => !keyInds.some(k=>i.name.includes(k)));
    const bigIdx = (indices&&indices.raw && indices.raw['核心大盘指数']) || [];
    const allOther = [...otherIdx, ...bigIdx];
    if (allOther.length > 0) {
        document.getElementById('otherIdxSection').style.display='';
        document.getElementById('otherCount').textContent = allOther.length+' 只';
        document.getElementById('otherIdxBody').innerHTML = allOther.map(idx=>{
            const c = parseCC(idx.策传);
            const sy = c._四域 || idx.四域周 || '';
            const m = mp[idx.code]||{};
            const sc = (()=>{let s=0;if(sy=='多长')s=50;else if(sy=='多被')s=25;else if(sy=='空看')s=15;else if(sy=='空长')s=5;return s;})();
            return '<tr><td>'+idx.code+'</td><td>'+idx.name+'</td><td>'+badge(sy)+'</td><td>'+sc+'</td><td class="'+(m.涨跌幅>=0?'red':'green')+'">'+(m.最新价||0).toFixed(2)+'</td><td class="'+(m.涨跌幅>=0?'red':'green')+'">'+(m.涨跌幅||0).toFixed(2)+'%</td></tr>';
        }).join('');
    }
}

// 定时刷新
let fetchCount = 0;
function refresh() {
    fetch('/api/data').then(r=>r.json()).then(data=>{
        fetchCount++;
        // 调试信息
        let dbg = document.getElementById('debugInfo');
        if(dbg) dbg.textContent = '#'+fetchCount+' pos='+(data.positions||[]).length+' loading='+(data.loading?'Y':'N');
        console.log('['+new Date().toLocaleTimeString()+'] #'+fetchCount+' 更新');
        if (data.loading) {
            setTimeout(refresh, 5000);
            return;
        }
        try {
            updateDashboard(data);
            if(dbg) dbg.textContent += ' render=OK';
        } catch(e) {
            if(dbg) dbg.textContent += ' ERROR: '+e.message;
            console.error('render error:', e);
        }
    }).catch(e=>{
        let dbg = document.getElementById('debugInfo');
        if(dbg) dbg.textContent = 'fetch ERROR: '+e.message;
        console.error('fetch error:', e);
    });
}

// 初始加载
initCharts();
refresh();
setInterval(refresh, (60 || 60)*1000);
