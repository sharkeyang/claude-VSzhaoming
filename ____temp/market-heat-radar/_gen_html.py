# -*- coding: utf-8 -*-
import json

with open('_consolidated.json', encoding='utf-8') as f:
    DATA = json.load(f)

# Serialize data as a JS object (compact, ensure_ascii=False for Chinese)
data_js = json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>市场热度与飙升雷达 · Market Heat Radar</title>
<style>
  :root{
    --bg:#0b0f17; --bg2:#111827; --panel:#151c2c; --panel2:#1a2336;
    --line:#243049; --line2:#2e3b57;
    --txt:#e6edf7; --txt2:#9aa7bd; --txt3:#6b7a93;
    --accent:#4f8cff; --accent2:#7aa8ff;
    --hot:#ff5d5d; --sky:#ffb020; --up:#ff5d5d; --down:#2fd18a; --flat:#9aa7bd;
    --shadow:0 8px 30px rgba(0,0,0,.35);
    --radius:14px;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{background:var(--bg);color:var(--txt);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;line-height:1.5}
  a{color:var(--accent2);text-decoration:none}
  .wrap{max-width:1180px;margin:0 auto;padding:24px 20px 60px}

  /* Header */
  .topbar{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:22px}
  .brand{display:flex;align-items:center;gap:14px}
  .logo{width:44px;height:44px;border-radius:12px;flex:none;
    background:linear-gradient(135deg,#4f8cff,#7a5cff);
    display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:var(--shadow)}
  .brand h1{font-size:22px;font-weight:700;letter-spacing:.5px}
  .brand .sub{font-size:12px;color:var(--txt3);margin-top:2px}
  .meta{text-align:right;font-size:12px;color:var(--txt3);line-height:1.7}
  .meta b{color:var(--txt2);font-weight:600}

  /* Tabs */
  .tabs{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap}
  .tab{display:flex;align-items:center;gap:8px;padding:10px 18px;border-radius:10px;
    background:var(--panel);border:1px solid var(--line);cursor:pointer;
    font-size:14px;font-weight:600;color:var(--txt2);transition:all .15s;user-select:none}
  .tab:hover{border-color:var(--line2);color:var(--txt)}
  .tab.active{background:linear-gradient(135deg,rgba(79,140,255,.18),rgba(122,92,255,.12));
    border-color:var(--accent);color:var(--txt)}
  .tab .dot{width:8px;height:8px;border-radius:50%}
  .tab .dot.hot{background:var(--hot)}
  .tab .dot.sky{background:var(--sky)}
  .tab .badge{font-size:11px;background:rgba(255,255,255,.08);padding:1px 7px;border-radius:20px;color:var(--txt2)}

  /* Stat strip */
  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:18px}
  .stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px}
  .stat .k{font-size:11px;color:var(--txt3);text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
  .stat .v{font-size:22px;font-weight:700}
  .stat .v small{font-size:12px;color:var(--txt3);font-weight:500;margin-left:4px}
  .stat .d{font-size:11px;color:var(--txt3);margin-top:4px}

  /* Panels */
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:18px;overflow:hidden}
  .panel-head{display:flex;align-items:center;justify-content:space-between;gap:12px;
    padding:14px 18px;border-bottom:1px solid var(--line);flex-wrap:wrap}
  .panel-head h2{font-size:15px;font-weight:700;display:flex;align-items:center;gap:9px}
  .panel-head h2 .tag{font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px}
  .tag.hot{background:rgba(255,93,93,.14);color:var(--hot)}
  .tag.sky{background:rgba(255,176,32,.14);color:var(--sky)}
  .panel-head .note{font-size:11px;color:var(--txt3)}
  .panel-body{padding:16px 18px}

  /* Table */
  .tbl{width:100%;border-collapse:collapse;font-size:13px}
  .tbl th{font-size:11px;color:var(--txt3);text-transform:uppercase;letter-spacing:.5px;
    text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);font-weight:600;white-space:nowrap}
  .tbl td{padding:10px;border-bottom:1px solid rgba(36,48,73,.5);vertical-align:middle}
  .tbl tr:last-child td{border-bottom:none}
  .tbl tr:hover td{background:rgba(79,140,255,.05)}
  .rank{font-weight:700;font-size:14px;width:44px;color:var(--txt2)}
  .rank.top1{color:var(--hot)} .rank.top2{color:var(--sky)} .rank.top3{color:#ffd76a}
  .name{font-weight:600}
  .code{font-size:11px;color:var(--txt3);margin-top:1px}
  .heat{font-variant-numeric:tabular-nums;font-weight:600}
  .heat small{color:var(--txt3);font-weight:400;font-size:11px}
  .chg{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}
  .chg.up{color:var(--up)} .chg.down{color:var(--down)} .chg.flat{color:var(--flat)}
  .trend-pill{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;
    padding:2px 9px;border-radius:20px}
  .trend-pill.up{background:rgba(255,93,93,.13);color:var(--up)}
  .trend-pill.down{background:rgba(47,209,138,.13);color:var(--down)}
  .trend-pill.flat{background:rgba(154,167,189,.12);color:var(--flat)}
  .bar-cell{min-width:120px}
  .bar{height:6px;border-radius:4px;background:var(--line);overflow:hidden;position:relative}
  .bar i{display:block;height:100%;border-radius:4px;background:linear-gradient(90deg,var(--accent),var(--accent2))}
  .bar i.hot{background:linear-gradient(90deg,#ff5d5d,#ff9d5d)}
  .bar i.sky{background:linear-gradient(90deg,#ffb020,#ffd76a)}

  /* Chart */
  #chartWrap{position:relative;width:100%;height:340px}
  #chart{width:100%;height:100%;display:block}
  .chart-legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--txt2);margin-top:10px}
  .chart-legend .item{display:flex;align-items:center;gap:6px}
  .chart-legend .sw{width:14px;height:3px;border-radius:2px}
  .chart-tooltip{position:absolute;pointer-events:none;background:rgba(11,15,23,.95);
    border:1px solid var(--line2);border-radius:10px;padding:10px 12px;font-size:12px;
    box-shadow:var(--shadow);opacity:0;transition:opacity .1s;z-index:20;min-width:150px}
  .chart-tooltip .tt-title{font-weight:700;margin-bottom:6px;font-size:13px}
  .chart-tooltip .tt-row{display:flex;justify-content:space-between;gap:16px;padding:2px 0}
  .chart-tooltip .tt-row .l{color:var(--txt3)}
  .chart-tooltip .tt-row .r{font-weight:600;font-variant-numeric:tabular-nums}
  .range-hint{font-size:11px;color:var(--txt3);margin-top:8px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
  .range-hint .chip{background:var(--panel2);border:1px solid var(--line);padding:2px 9px;border-radius:20px;font-size:11px;color:var(--txt2)}
  .range-hint .chip b{color:var(--txt)}

  /* Overlap */
  .overlap-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
  .ov{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
  .ov .pair{font-size:12px;color:var(--txt2);margin-bottom:6px}
  .ov .pair b{color:var(--txt)}
  .ov .num{font-size:24px;font-weight:700}
  .ov .num small{font-size:12px;color:var(--txt3);font-weight:500}
  .ov .bar2{height:5px;border-radius:3px;background:var(--line);margin-top:8px;overflow:hidden}
  .ov .bar2 i{display:block;height:100%;border-radius:3px;background:linear-gradient(90deg,var(--accent),var(--accent2))}

  /* Insight */
  .insight{background:linear-gradient(135deg,rgba(79,140,255,.08),rgba(122,92,255,.06));
    border:1px solid rgba(79,140,255,.25);border-radius:var(--radius);padding:16px 18px;margin-bottom:18px}
  .insight h3{font-size:13px;color:var(--accent2);margin-bottom:8px;display:flex;align-items:center;gap:7px}
  .insight ul{margin-left:18px;font-size:13px;color:var(--txt2);line-height:1.8}
  .insight li b{color:var(--txt)}

  /* Footer / disclaimer */
  .disclaimer{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    padding:16px 18px;font-size:12px;color:var(--txt3);line-height:1.8;margin-top:6px}
  .disclaimer b{color:var(--txt2)}
  .foot{text-align:center;font-size:11px;color:var(--txt3);margin-top:22px;line-height:1.8}

  @media (max-width:640px){
    .wrap{padding:16px 12px 40px}
    .brand h1{font-size:18px}
    .meta{text-align:left;margin-top:4px}
    .tbl{font-size:12px}
    .tbl th,.tbl td{padding:8px 6px}
    .bar-cell{display:none}
    #chartWrap{height:280px}
    .panel-body{padding:12px}
  }
</style>
</head>
<body>
<div class="wrap">

  <!-- Header -->
  <div class="topbar">
    <div class="brand">
      <div class="logo">&#128225;</div>
      <div>
        <h1>市场热度与飙升雷达</h1>
        <div class="sub">Market Heat &amp; Skyrocket Radar · A股特色榜单监控</div>
      </div>
    </div>
    <div class="meta">
      <div>榜单时间：<b id="metaTime">&mdash;</b></div>
      <div>统计周期：<b>24小时 / 小时</b> · 数据源：<b>同花顺 hithink-finance</b></div>
      <div>数据延迟：<b>榜单为快照，非实时行情</b></div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs" id="tabs">
    <div class="tab active" data-view="hot_day"><span class="dot hot"></span>热股榜 · 24小时<span class="badge" id="b_hot_day">30</span></div>
    <div class="tab" data-view="hot_hour"><span class="dot hot"></span>热股榜 · 小时<span class="badge" id="b_hot_hour">30</span></div>
    <div class="tab" data-view="sky_day"><span class="dot sky"></span>飙升榜 · 24小时<span class="badge" id="b_sky_day">30</span></div>
    <div class="tab" data-view="sky_hour"><span class="dot sky"></span>飙升榜 · 小时<span class="badge" id="b_sky_hour">30</span></div>
  </div>

  <!-- Stats -->
  <div class="stats" id="stats"></div>

  <!-- Insight -->
  <div class="insight">
    <h3>&#9889; 榜单解读（基于当前快照，非投资建议）</h3>
    <ul id="insightList"></ul>
  </div>

  <!-- Main table -->
  <div class="panel">
    <div class="panel-head">
      <h2><span class="tag" id="panelTag">热股</span><span id="panelTitle">热股榜 · 24小时</span></h2>
      <div class="note" id="panelNote">热度为相对量纲，热股榜与飙升榜口径不同，不可直接混比</div>
    </div>
    <div class="panel-body">
      <table class="tbl">
        <thead>
          <tr>
            <th>#</th><th>股票</th><th>热度</th><th>排名变化</th><th>趋势</th><th class="bar-cell">热度占比</th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- Rank trend chart -->
  <div class="panel">
    <div class="panel-head">
      <h2>&#128200; 热股榜前3 · 近30日排名轨迹</h2>
      <div class="note">纵轴为排名（1 最热），对数刻度；排名越低越靠前</div>
    </div>
    <div class="panel-body">
      <div id="chartWrap">
        <svg id="chart"></svg>
        <div class="chart-tooltip" id="tooltip"></div>
      </div>
      <div class="chart-legend" id="legend"></div>
      <div class="range-hint" id="rangeHint"></div>
    </div>
  </div>

  <!-- Overlap -->
  <div class="panel">
    <div class="panel-head">
      <h2>&#128279; 榜单重合度</h2>
      <div class="note">两榜单同时上榜的股票数量（各榜取前30）</div>
    </div>
    <div class="panel-body">
      <div class="overlap-grid" id="overlapGrid"></div>
    </div>
  </div>

  <!-- Disclaimer -->
  <div class="disclaimer">
    <b>数据说明：</b>本看板数据来自同花顺 hithink-finance 特色数据接口（热股榜 / 飙升榜 / 热度趋势），榜单为抓取时刻的<b>快照</b>，存在一定延迟，非实时行情。热股榜反映<b>关注热度</b>，飙升榜反映<b>短期涨幅/异动强度</b>，两者含义不同，不应混为单一评分；排名变化反映的是热度相对位置变动，<b>不构成确定性买卖信号</b>。榜单热度与排名受市场情绪、消息面、交易活跃度等多因素影响，波动剧烈，仅供参考。
    <br><br>
    <b>&#9888; 非投资建议：</b>本页面仅用于市场热度观察与数据展示，不构成任何投资建议、荐股或收益承诺。股市有风险，投资需谨慎。据此操作，风险自担。
  </div>

  <div class="foot">
    生成时间：<span id="genTime">&mdash;</span> · 数据源：同花顺 hithink-finance · 单文件离线看板，无外部依赖，无运行时请求
  </div>
</div>

<script>
const DATA = __DATA__;

// ---------- helpers ----------
const fmtHeat = v => {
  const n = parseFloat(v);
  if (n >= 1e8) return (n/1e8).toFixed(2)+'亿';
  if (n >= 1e4) return (n/1e4).toFixed(1)+'万';
  return n.toLocaleString();
};
const trendLabel = {up:'上升', down:'下降', flat:'持平'};
const trendColor = {up:'up', down:'down', flat:'flat'};
const VIEW_META = {
  hot_day:{tag:'热股',tagCls:'hot',title:'热股榜 · 24小时',tsKey:'hot_day',barCls:'hot',heatUnit:'热度'},
  hot_hour:{tag:'热股',tagCls:'hot',title:'热股榜 · 小时',tsKey:'hot_hour',barCls:'hot',heatUnit:'热度'},
  sky_day:{tag:'飙升',tagCls:'sky',title:'飙升榜 · 24小时',tsKey:'sky_day',barCls:'sky',heatUnit:'飙升强度'},
  sky_hour:{tag:'飙升',tagCls:'sky',title:'飙升榜 · 小时',tsKey:'sky_hour',barCls:'sky',heatUnit:'飙升强度'},
};

// ---------- state ----------
let currentView = 'hot_day';
let range = null; // {startIdx,endIdx} for chart exploration

// ---------- tabs ----------
document.getElementById('tabs').addEventListener('click', e => {
  const tab = e.target.closest('.tab');
  if (!tab) return;
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  tab.classList.add('active');
  currentView = tab.dataset.view;
  range = null;
  renderAll();
});

// ---------- render ----------
function renderAll(){
  renderMeta();
  renderStats();
  renderInsight();
  renderTable();
  renderChart();
  renderOverlap();
}

function renderMeta(){
  const ts = DATA.timestamps[currentView];
  document.getElementById('metaTime').textContent = ts;
  document.getElementById('genTime').textContent = DATA.generated_at;
}

function renderStats(){
  const items = DATA.lists[currentView];
  const meta = VIEW_META[currentView];
  const maxHeat = Math.max(...items.map(i=>parseFloat(i.heat)));
  const upCount = items.filter(i=>i.rank_trend==='up').length;
  const downCount = items.filter(i=>i.rank_trend==='down').length;
  const flatCount = items.filter(i=>i.rank_trend==='flat').length;
  const top1 = items[0];
  const stats = [
    {k:'榜单股票', v:items.length, d:'前30名'},
    {k:'榜首', v:top1.name, d:top1.thscode + ' · 热度 '+fmtHeat(top1.heat)},
    {k:'热度峰值', v:fmtHeat(maxHeat), d:meta.heatUnit+' 最高'},
    {k:'趋势分布', v:upCount+'&#8593; / '+downCount+'&#8595; / '+flatCount+'&mdash;', d:'排名上升/下降/持平'},
  ];
  document.getElementById('stats').innerHTML = stats.map(s=>
    '<div class="stat"><div class="k">'+s.k+'</div><div class="v">'+s.v+'</div><div class="d">'+s.d+'</div></div>'
  ).join('');
}

function renderInsight(){
  const items = DATA.lists[currentView];
  const meta = VIEW_META[currentView];
  const upCount = items.filter(i=>i.rank_trend==='up').length;
  const downCount = items.filter(i=>i.rank_trend==='down').length;
  const flatCount = items.filter(i=>i.rank_trend==='flat').length;
  const top3 = items.slice(0,3).map(i=>i.name).join('、');
  const li = [];
  li.push('<li><b>'+meta.title+'</b> 榜首为 <b>'+items[0].name+'</b>（'+items[0].thscode+'），热度 '+fmtHeat(items[0].heat)+'。</li>');
  li.push('<li>前3名：<b>'+top3+'</b>。'+upCount+' 只排名上升、'+downCount+' 只下降、'+flatCount+' 只持平。</li>');
  if(currentView.startsWith('hot')){
    li.push('<li>热股榜反映<b>关注热度</b>，与飙升榜（短期涨幅/异动强度）含义不同，两者不可混为单一评分。</li>');
  } else {
    li.push('<li>飙升榜反映<b>短期涨幅/异动强度</b>，与热股榜（关注热度）含义不同，两者不可混为单一评分。</li>');
  }
  li.push('<li>排名变化仅反映热度相对位置变动，<b>不构成确定性买卖信号</b>，请结合基本面与风险审慎判断。</li>');
  document.getElementById('insightList').innerHTML = li.join('');
}

function renderTable(){
  const items = DATA.lists[currentView];
  const meta = VIEW_META[currentView];
  const maxHeat = Math.max(...items.map(i=>parseFloat(i.heat)));
  document.getElementById('panelTag').textContent = meta.tag;
  document.getElementById('panelTag').className = 'tag ' + meta.tagCls;
  document.getElementById('panelTitle').textContent = meta.title;
  const rows = items.map((it,i)=>{
    const rankCls = i===0?'top1':i===1?'top2':i===2?'top3':'';
    const chg = it.rank_change;
    const chgCls = chg>0?'up':chg<0?'down':'flat';
    const chgTxt = chg>0?'+'+chg:chg<0?String(chg):'0';
    const pct = (parseFloat(it.heat)/maxHeat*100).toFixed(1);
    return '<tr>'+
      '<td class="rank '+rankCls+'">'+it.rank+'</td>'+
      '<td><div class="name">'+it.name+'</div><div class="code">'+it.thscode+'</div></td>'+
      '<td class="heat">'+fmtHeat(it.heat)+'</td>'+
      '<td class="chg '+chgCls+'">'+chgTxt+'</td>'+
      '<td><span class="trend-pill '+trendColor[it.rank_trend]+'">'+trendLabel[it.rank_trend]+'</span></td>'+
      '<td class="bar-cell"><div class="bar"><i class="'+meta.barCls+'" style="width:'+pct+'%"></i></div></td>'+
    '</tr>';
  }).join('');
  document.getElementById('tbody').innerHTML = rows;
}

// ---------- chart ----------
const TREND_COLORS = ['#4f8cff','#ffb020','#2fd18a'];
function renderChart(){
  const trends = DATA.trends;
  const svg = document.getElementById('chart');
  const wrap = document.getElementById('chartWrap');
  const W = wrap.clientWidth, H = wrap.clientHeight;
  const pad = {l:46, r:16, t:16, b:34};
  const iw = W-pad.l-pad.r, ih = H-pad.t-pad.b;
  svg.setAttribute('viewBox', '0 0 '+W+' '+H);
  svg.innerHTML = '';

  // x domain across all series (union of dates)
  const allDates = [...new Set(trends.flatMap(t=>t.series.map(s=>s.date)))].sort();
  const xIdx = {}; allDates.forEach((d,i)=>xIdx[d]=i);
  const x = i => pad.l + (i/(allDates.length-1))*iw;

  // y domain: log scale of ranks (1..maxRank)
  const allRanks = trends.flatMap(t=>t.series.map(s=>s.rank));
  const maxRank = Math.max(...allRanks);
  const minRank = 1;
  const logMin = Math.log10(minRank), logMax = Math.log10(maxRank);
  const yLog = r => pad.t + (1-(Math.log10(r)-logMin)/(logMax-logMin))*ih;

  // gridlines (log ticks)
  const ticks = [];
  for(let p=0; p<=Math.ceil(logMax); p++){
    const v = Math.pow(10,p);
    if(v>=minRank && v<=maxRank) ticks.push(v);
  }
  ticks.forEach(v=>{
    const yy = yLog(v);
    const line = document.createElementNS('http://www.w3.org/2000/svg','line');
    line.setAttribute('x1',pad.l); line.setAttribute('x2',W-pad.r);
    line.setAttribute('y1',yy); line.setAttribute('y2',yy);
    line.setAttribute('stroke','#243049'); line.setAttribute('stroke-width','1');
    line.setAttribute('stroke-dasharray','3,4');
    svg.appendChild(line);
    const t = document.createElementNS('http://www.w3.org/2000/svg','text');
    t.setAttribute('x',pad.l-8); t.setAttribute('y',yy+4);
    t.setAttribute('text-anchor','end'); t.setAttribute('font-size','10');
    t.setAttribute('fill','#6b7a93');
    t.textContent = v>=1000 ? (v/1000)+'k' : v;
    svg.appendChild(t);
  });

  // x axis labels (subset)
  const labelEvery = Math.ceil(allDates.length/8);
  allDates.forEach((d,i)=>{
    if(i%labelEvery!==0 && i!==allDates.length-1) return;
    const t = document.createElementNS('http://www.w3.org/2000/svg','text');
    t.setAttribute('x',x(i)); t.setAttribute('y',H-pad.b+18);
    t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','10');
    t.setAttribute('fill','#6b7a93');
    t.textContent = d.slice(5);
    svg.appendChild(t);
  });

  // range highlight (exploration)
  if(range){
    const x0 = x(range.startIdx), x1 = x(range.endIdx);
    const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
    rect.setAttribute('x',x0); rect.setAttribute('y',pad.t);
    rect.setAttribute('width',x1-x0); rect.setAttribute('height',ih);
    rect.setAttribute('fill','rgba(79,140,255,.10)');
    rect.setAttribute('stroke','rgba(79,140,255,.4)'); rect.setAttribute('stroke-width','1');
    svg.appendChild(rect);
  }

  // series lines
  trends.forEach((tr,si)=>{
    const color = TREND_COLORS[si%TREND_COLORS.length];
    const pts = tr.series.map(s=>[x(xIdx[s.date]), yLog(s.rank)]);
    // area fill (subtle)
    const area = document.createElementNS('http://www.w3.org/2000/svg','path');
    const areaD = pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ')
      + ' L'+pts[pts.length-1][0].toFixed(1)+','+(pad.t+ih)+' L'+pts[0][0].toFixed(1)+','+(pad.t+ih)+' Z';
    area.setAttribute('d',areaD);
    area.setAttribute('fill',color); area.setAttribute('opacity','0.06');
    svg.appendChild(area);
    // line
    const path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d', pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' '));
    path.setAttribute('fill','none'); path.setAttribute('stroke',color);
    path.setAttribute('stroke-width','2.2'); path.setAttribute('stroke-linejoin','round');
    path.setAttribute('stroke-linecap','round');
    svg.appendChild(path);
    // points
    pts.forEach((p,i)=>{
      const c = document.createElementNS('http://www.w3.org/2000/svg','circle');
      c.setAttribute('cx',p[0]); c.setAttribute('cy',p[1]); c.setAttribute('r','3');
      c.setAttribute('fill',color); c.setAttribute('stroke','#0b0f17'); c.setAttribute('stroke-width','1.2');
      c.setAttribute('data-si',si); c.setAttribute('data-idx',i);
      c.style.cursor='pointer';
      c.addEventListener('mouseenter', function(ev){ showTooltip(ev, tr, i, color); });
      c.addEventListener('mousemove', moveTooltip);
      c.addEventListener('mouseleave', hideTooltip);
      svg.appendChild(c);
    });
  });

  // legend
  document.getElementById('legend').innerHTML = trends.map((tr,si)=>
    '<div class="item"><span class="sw" style="background:'+TREND_COLORS[si%TREND_COLORS.length]+'"></span>'+tr.name+' <span style="color:var(--txt3)">'+tr.thscode+'</span></div>'
  ).join('');

  // range hint
  const hint = document.getElementById('rangeHint');
  if(range){
    const startD = allDates[range.startIdx], endD = allDates[range.endIdx];
    const seg = trends.map(tr=>{
      const sub = tr.series.filter(s=>s.date>=startD && s.date<=endD);
      if(!sub.length) return null;
      const first = sub[0].rank, last = sub[sub.length-1].rank;
      const delta = last-first;
      const dir = delta<0?'&#8593; 上升':delta>0?'&#8595; 下降':'&mdash; 持平';
      return '<span class="chip"><b>'+tr.name+'</b> '+first+'&rarr;'+last+' '+dir+'</span>';
    }).filter(Boolean).join(' ');
    hint.innerHTML = '区间 '+startD+' ~ '+endD+'：'+seg+' <span class="chip" style="cursor:pointer" onclick="clearRange()">&#10005; 清除区间</span>';
  } else {
    hint.innerHTML = '&#128161; 在图表上按住拖动可框选区间，查看该区间内各股排名变化';
  }
}

// tooltip
const tooltip = document.getElementById('tooltip');
function showTooltip(ev, tr, idx, color){
  const s = tr.series[idx];
  tooltip.innerHTML =
    '<div class="tt-title" style="color:'+color+'">'+tr.name+' <span style="color:var(--txt3);font-weight:400">'+tr.thscode+'</span></div>'+
    '<div class="tt-row"><span class="l">日期</span><span class="r">'+s.date+'</span></div>'+
    '<div class="tt-row"><span class="l">排名</span><span class="r">#'+s.rank+'</span></div>';
  tooltip.style.opacity = '1';
  moveTooltip(ev);
}
function moveTooltip(ev){
  const wrap = document.getElementById('chartWrap').getBoundingClientRect();
  let tx = ev.clientX - wrap.left + 14;
  let ty = ev.clientY - wrap.top - 10;
  const tw = tooltip.offsetWidth, th = tooltip.offsetHeight;
  if(tx + tw > wrap.width) tx = ev.clientX - wrap.left - tw - 14;
  if(ty + th > wrap.height) ty = ev.clientY - wrap.top - th - 10;
  tooltip.style.left = tx+'px'; tooltip.style.top = ty+'px';
}
function hideTooltip(){ tooltip.style.opacity='0'; }

// range selection via drag
(function(){
  const svg = document.getElementById('chart');
  let dragging=false, startX=0;
  const allDates = [...new Set(DATA.trends.flatMap(t=>t.series.map(s=>s.date)))].sort();
  svg.addEventListener('mousedown', function(e){ dragging=true; startX=e.offsetX; });
  svg.addEventListener('mousemove', function(e){
    if(!dragging) return;
    const wrap = document.getElementById('chartWrap');
    const W = wrap.clientWidth, pad=46;
    const iw = W-pad-16;
    const x0 = Math.min(startX,e.offsetX), x1=Math.max(startX,e.offsetX);
    const i0 = Math.max(0, Math.min(allDates.length-1, Math.round((x0-pad)/iw*(allDates.length-1))));
    const i1 = Math.max(0, Math.min(allDates.length-1, Math.round((x1-pad)/iw*(allDates.length-1))));
    if(i1-i0>=1){ range={startIdx:i0,endIdx:i1}; renderChart(); }
  });
  svg.addEventListener('mouseup', function(){ dragging=false; });
  svg.addEventListener('mouseleave', function(){ dragging=false; });
})();
function clearRange(){ range=null; renderChart(); }

// ---------- overlap ----------
function renderOverlap(){
  const ov = DATA.overlap;
  const pairs = [
    {k:'hot_day_hot_hour', l:'热股·24h', r:'热股·小时', desc:'热股榜跨周期'},
    {k:'sky_day_sky_hour', l:'飙升·24h', r:'飙升·小时', desc:'飙升榜跨周期'},
    {k:'hot_day_sky_day', l:'热股·24h', r:'飙升·24h', desc:'同周期跨榜单'},
    {k:'hot_hour_sky_hour', l:'热股·小时', r:'飙升·小时', desc:'同周期跨榜单'},
    {k:'hot_day_sky_hour', l:'热股·24h', r:'飙升·小时', desc:'跨周期跨榜单'},
  ];
  const grid = document.getElementById('overlapGrid');
  grid.innerHTML = pairs.map(p=>{
    const n = ov[p.k];
    const pct = (n/30*100).toFixed(0);
    return '<div class="ov">'+
      '<div class="pair"><b>'+p.l+'</b> &#8745; <b>'+p.r+'</b></div>'+
      '<div class="num">'+n+'<small> / 30</small></div>'+
      '<div class="bar2"><i style="width:'+pct+'%"></i></div>'+
      '<div style="font-size:11px;color:var(--txt3);margin-top:6px">'+p.desc+' · 重合 '+pct+'%</div>'+
    '</div>';
  }).join('');
}

// ---------- init ----------
renderAll();
window.addEventListener('resize', function(){ renderChart(); });
</script>
</body>
</html>
'''

html = HTML.replace('__DATA__', data_js)

# Write to current directory (project root)
out_path = r'd:\@VSwork\VS昭明计划VBA优化\market-heat-radar.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('written', out_path, len(html), 'bytes')