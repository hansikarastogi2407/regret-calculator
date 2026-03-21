"""
Regret Calculator — Premium Streamlit App
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math, io

from calc import (
    Habit, Scenario, SCENARIO_COLORS, PRESET_HABITS, FREQ_OPTIONS, FREQ_LABELS,
    calc_scenario, make_default_scenarios, fmt_usd, fmt_usd_dec,
)

st.set_page_config(page_title="Regret Calculator", page_icon="💸", layout="wide",
                   initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500&display=swap');

*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#07070a!important;color:#e6e2da!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}
section[data-testid="stSidebar"]{display:none!important}

/* Animated grid bg */
body::before{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:linear-gradient(rgba(232,197,71,.025) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(232,197,71,.025) 1px,transparent 1px);
  background-size:56px 56px;
  animation:gridMove 25s linear infinite;
}
@keyframes gridMove{from{background-position:0 0}to{background-position:56px 56px}}

/* Glow blobs */
body::after{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(600px circle at 80% 10%, rgba(232,197,71,.06), transparent 50%),
    radial-gradient(500px circle at 10% 80%, rgba(62,207,178,.05), transparent 50%),
    radial-gradient(400px circle at 50% 50%, rgba(74,158,255,.03), transparent 50%);
}

/* Content wrapper */
.wrap{position:relative;z-index:1;padding:0 44px 100px;max-width:1160px;margin:0 auto}

/* Sticky nav */
.topnav{
  position:sticky;top:0;z-index:200;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 44px;height:60px;
  background:rgba(7,7,10,.88);backdrop-filter:blur(24px);
  border-bottom:1px solid rgba(255,255,255,.05);
  margin-bottom:0;
}
.logo{font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:800;color:#e8c547;letter-spacing:-.01em}
.logo span{color:#e6e2da}
.nav-hint{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#2e2c28}

/* Page hero */
.hero{padding:52px 0 32px;animation:fadeUp .5s ease both}
.hero h1{
  font-family:'Syne',sans-serif;font-size:clamp(2.4rem,5vw,3.8rem);
  font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:0 0 10px;
  background:linear-gradient(135deg,#fff 0%,#e8c547 45%,#3ecfb2 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero p{font-size:1rem;color:#55524e;max-width:480px;line-height:1.6}

/* ── Quick Calc shell ── */
.calc-box{
  background:linear-gradient(135deg,rgba(232,197,71,.07),rgba(62,207,178,.03));
  border:1px solid rgba(232,197,71,.18);border-radius:22px;padding:28px 32px;
  margin-bottom:28px;position:relative;overflow:hidden;
  animation:fadeUp .5s .08s ease both;
}
.calc-box::after{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(232,197,71,.55),transparent);
}
.calc-lbl{
  font-family:'Syne',sans-serif;font-size:.62rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.16em;color:#e8c547;margin-bottom:18px;
}
.calc-nums{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:20px}
.calc-num-block{}
.calc-num-sub{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#55524e;margin-bottom:4px}
.calc-num-val{
  font-family:'JetBrains Mono',monospace;font-weight:700;line-height:1;
  font-size:clamp(1.6rem,3.5vw,2.8rem);
  transition:all .35s ease;
}
.calc-num-val.gold{color:#e8c547;text-shadow:0 0 32px rgba(232,197,71,.35)}
.calc-num-val.red {color:#e85d3c;text-shadow:0 0 24px rgba(232,93,60,.2)}
.calc-num-val.teal{color:#3ecfb2;text-shadow:0 0 24px rgba(62,207,178,.2)}
.calc-insight{
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
  border-radius:12px;padding:15px 18px;font-size:.88rem;color:#7a766f;line-height:1.65;
}
.calc-insight b{color:#e6e2da}
.hl-gold{color:#e8c547;font-family:'JetBrains Mono',monospace;font-weight:700}
.hl-teal{color:#3ecfb2;font-family:'JetBrains Mono',monospace;font-weight:700}
.hl-red {color:#e85d3c;font-family:'JetBrains Mono',monospace;font-weight:700}

/* Example cards */
.ex-card{
  background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
  border-radius:14px;padding:16px 18px;margin-bottom:12px;
  transition:border-color .2s,transform .2s;cursor:default;
}
.ex-card:hover{border-color:rgba(232,197,71,.2);transform:translateY(-2px)}
.ex-name{font-size:.95rem;margin-bottom:8px}
.ex-meta{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:#3a3733;margin-bottom:4px}
.ex-val{font-family:'JetBrains Mono',monospace;font-size:1.35rem;font-weight:700;color:#e8c547}
.ex-note{font-size:.72rem;color:#55524e;margin-top:4px}

/* Scenario card */
.sc-card{
  background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
  border-radius:20px;padding:22px;margin-bottom:14px;position:relative;overflow:hidden;
  transition:border-color .2s,transform .2s;animation:fadeUp .45s ease both;
}
.sc-card:hover{border-color:rgba(255,255,255,.12);transform:translateY(-2px)}
.sc-top-bar{height:2px;position:absolute;top:0;left:0;right:0}
.sc-hdr{display:flex;align-items:center;gap:9px;margin-bottom:18px}
.sc-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;animation:dotPulse 2.5s ease-in-out infinite}
@keyframes dotPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.7;transform:scale(1.3)}}
.sc-nm{font-family:'Syne',sans-serif;font-size:.95rem;font-weight:700;flex:1}
.sc-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-bottom:14px}
.sc-m{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);border-radius:11px;padding:10px 13px}
.sc-m.big{grid-column:span 2;border-color:rgba(232,197,71,.15);background:rgba(232,197,71,.04)}
.sc-ml{font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:#3a3733;margin-bottom:3px}
.sc-mv{font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:#e6e2da}
.sc-m.big .sc-mv{color:#e8c547;font-size:1.5rem}
.tags{display:flex;flex-wrap:wrap;gap:5px}
.tag{font-size:.68rem;padding:3px 9px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:20px;color:#55524e}

/* Compare card */
.cmp-card{
  background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
  border-radius:20px;padding:22px;position:relative;overflow:hidden;
  animation:fadeUp .45s ease both;
}
.cmp-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--cc)}

/* Delta */
.delta{
  background:linear-gradient(135deg,rgba(232,197,71,.07),rgba(62,207,178,.04));
  border:1px solid rgba(232,197,71,.2);border-radius:16px;padding:18px 22px;
  margin-bottom:24px;font-size:.92rem;color:#7a766f;line-height:1.65;
  animation:fadeUp .45s .1s ease both;position:relative;overflow:hidden;
}
.delta::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(232,197,71,.5),transparent);
}

/* Chart shell */
.chart-shell{
  background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
  border-radius:20px;padding:22px;margin-bottom:18px;animation:fadeUp .45s ease both;
}
.chart-ttl{font-family:'Syne',sans-serif;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#3a3733;margin-bottom:14px}

/* Section label */
.slbl{font-family:'Syne',sans-serif;font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.16em;color:#2e2c28;margin:28px 0 12px}

/* Habit row */
.hrow{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:11px;padding:12px 15px;margin-bottom:7px;transition:border-color .2s}
.hrow:hover{border-color:rgba(255,255,255,.1)}

/* Animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}

/* ── Widget overrides ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input{
  background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;
  border-radius:10px!important;color:#e6e2da!important;
  font-family:'JetBrains Mono',monospace!important;font-size:.88rem!important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus{
  border-color:rgba(232,197,71,.4)!important;box-shadow:0 0 0 3px rgba(232,197,71,.08)!important;
}
div[data-testid="stSelectbox"]>div>div{
  background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.1)!important;
  border-radius:10px!important;color:#e6e2da!important;
}
div[data-testid="stSlider"] [role="slider"]{
  background:#e8c547!important;border-color:#e8c547!important;
  box-shadow:0 0 14px rgba(232,197,71,.5)!important;
}
div[data-testid="stSlider"] [data-baseweb="slider"]>div:first-child{
  background:rgba(255,255,255,.08)!important;
}
.stButton>button{
  font-family:'Syne',sans-serif!important;font-weight:700!important;
  border-radius:10px!important;transition:all .2s!important;
  background:rgba(255,255,255,.04)!important;
  border:1px solid rgba(255,255,255,.1)!important;color:#9e9b94!important;
}
.stButton>button:hover{
  background:rgba(255,255,255,.09)!important;color:#e6e2da!important;
  transform:translateY(-1px)!important;border-color:rgba(255,255,255,.18)!important;
}
button[kind="primary"],.stButton>button[kind="primary"]{
  background:#e8c547!important;color:#000!important;border-color:transparent!important;
}
button[kind="primary"]:hover,.stButton>button[kind="primary"]:hover{
  background:#f0d060!important;box-shadow:0 4px 22px rgba(232,197,71,.38)!important;color:#000!important;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"]{
  background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.07)!important;
  border-radius:12px!important;padding:4px!important;gap:3px!important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]{
  background:transparent!important;color:#55524e!important;border-radius:9px!important;
  font-family:'Syne',sans-serif!important;font-weight:700!important;
  font-size:.82rem!important;padding:7px 18px!important;border:none!important;
}
div[data-testid="stTabs"] [aria-selected="true"]{
  background:rgba(232,197,71,.1)!important;color:#e8c547!important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"]{display:none!important}
div[data-testid="stExpander"]{
  background:rgba(255,255,255,.02)!important;border:1px solid rgba(255,255,255,.07)!important;
  border-radius:13px!important;
}
label[data-testid="stWidgetLabel"] p,div[data-testid="stWidgetLabel"] p{
  color:#3a3733!important;font-size:.68rem!important;
  text-transform:uppercase!important;letter-spacing:.09em!important;font-weight:500!important;
}
div[data-testid="stDownloadButton"] button{
  background:rgba(62,207,178,.07)!important;border:1px solid rgba(62,207,178,.22)!important;
  color:#3ecfb2!important;font-family:'Syne',sans-serif!important;font-weight:700!important;
}
div[data-testid="stDownloadButton"] button:hover{
  background:rgba(62,207,178,.13)!important;box-shadow:0 4px 22px rgba(62,207,178,.2)!important;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "scenarios"   not in st.session_state: st.session_state.scenarios   = make_default_scenarios()
if "years"       not in st.session_state: st.session_state.years       = 10
if "rate"        not in st.session_state: st.session_state.rate        = 7
if "editing_id"  not in st.session_state: st.session_state.editing_id  = None

# ── HELPERS ────────────────────────────────────────────────────────────────────
def hex_rgba(hx, a=.1):
    hx=hx.lstrip("#"); r,g,b=int(hx[:2],16),int(hx[2:4],16),int(hx[4:],16)
    return f"rgba({r},{g},{b},{a})"

def fv_daily(daily, years, rate):
    annual = daily * 365
    if rate == 0: return annual * years
    r = rate / 100
    return annual * ((math.pow(1+r, years)-1) / r)

def make_chart(datasets, years, dashed=False, height=300):
    fig = go.Figure()
    xs = [f"Yr {i+1}" for i in range(years)]
    for ds in datasets:
        line = dict(color=ds["color"], width=2.5, dash="dot" if dashed else "solid")
        fig.add_trace(go.Scatter(
            x=xs, y=ds["data"], name=ds["label"], mode="lines",
            fill="tozeroy" if not dashed else None,
            fillcolor=hex_rgba(ds["color"], .07) if not dashed else None,
            line=line,
            hovertemplate=f"<b>{ds['label']}</b><br>$%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono,monospace", color="#3a3733", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#7a766f")),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#161618", bordercolor="rgba(255,255,255,.1)",
                        font=dict(family="JetBrains Mono", color="#e6e2da", size=12)),
        margin=dict(l=0, r=0, t=6, b=0), height=height,
        xaxis=dict(gridcolor="rgba(255,255,255,.04)", showline=False,
                   tickfont=dict(size=10), zeroline=False, tickcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.04)", showline=False,
                   tickfont=dict(size=10), zeroline=False,
                   tickprefix="$", tickformat=",.0f", tickcolor="rgba(0,0,0,0)"),
    )
    return fig

def export_csv(scenarios, years, rate):
    rows = []
    for i in range(years):
        yr = i+1
        row = {"Year": yr}
        for s in scenarios:
            r = calc_scenario(s, yr, rate)
            row[f"{s.name} — Spent"]    = round(r["total_spent"])
            row[f"{s.name} — Invested"] = round(r["invested_value"])
        rows.append(row)
    buf = io.StringIO()
    pd.DataFrame(rows).to_csv(buf, index=False)
    return buf.getvalue()

# ── NAV ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topnav">
  <div class="logo">💸 Regret<span>Calc</span></div>
  <div class="nav-hint">what could your money become?</div>
</div>
""", unsafe_allow_html=True)

# ── MAIN ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="wrap">', unsafe_allow_html=True)

# ── EDITOR (takes over whole page) ────────────────────────────────────────────
if st.session_state.editing_id:
    scenario = next((s for s in st.session_state.scenarios if s.id == st.session_state.editing_id), None)
    if not scenario:
        st.session_state.editing_id = None
        st.rerun()

    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
    if st.button("← Back to scenarios"):
        st.session_state.editing_id = None
        st.rerun()
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    n_col, c_col, t_col = st.columns([3,2,1])
    with n_col:
        nn = st.text_input("Scenario name", value=scenario.name)
        if nn != scenario.name: scenario.name = nn
    with c_col:
        cmap = {"🟡 Gold":"#e8c547","🟢 Teal":"#3ecfb2","🔵 Blue":"#4a9eff","🩷 Pink":"#e85d8a","🟣 Purple":"#b88aff"}
        cur = next((k for k,v in cmap.items() if v==scenario.color),"🟡 Gold")
        ch = st.selectbox("Color", list(cmap.keys()), index=list(cmap.keys()).index(cur))
        scenario.color = cmap[ch]
    with t_col:
        st.markdown(f'<div style="padding-top:26px;font-family:JetBrains Mono,monospace;font-size:1.7rem;font-weight:700;color:{scenario.color};text-shadow:0 0 20px {scenario.color}44">{fmt_usd(scenario.yearly_total)}<span style="font-size:.75rem;color:#2e2c28">/yr</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">Quick add from presets</div>', unsafe_allow_html=True)
    pcols = st.columns(5)
    for i, p in enumerate(PRESET_HABITS):
        with pcols[i%5]:
            added = any(h.name==p["name"] for h in scenario.habits)
            if st.button(("✓ " if added else "＋ ")+p["name"][:11],
                         key=f"p_{scenario.id}_{i}", use_container_width=True,
                         disabled=added, type="secondary"):
                scenario.habits.append(Habit(p["name"],p["cost"],p["freq"]))
                st.rerun()

    st.markdown('<div class="slbl">Add custom habit</div>', unsafe_allow_html=True)
    with st.expander("＋ Custom habit"):
        a,b,c,d = st.columns([3,1,2,1])
        with a: cname = st.text_input("Name", placeholder="e.g. Morning smoothie", key=f"cn_{scenario.id}")
        with b: ccost = st.number_input("$ cost", min_value=0.0, step=0.5, value=5.0, key=f"cc_{scenario.id}")
        with c: cfreq = st.selectbox("Freq", list(FREQ_OPTIONS.keys()), key=f"cf_{scenario.id}")
        with d:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Add ＋", key=f"cadd_{scenario.id}", type="primary"):
                if cname.strip():
                    scenario.habits.append(Habit(cname.strip(), ccost, FREQ_OPTIONS[cfreq]))
                    st.rerun()

    st.markdown('<div class="slbl">Current habits</div>', unsafe_allow_html=True)
    if not scenario.habits:
        st.markdown('<p style="color:#2e2c28;font-style:italic;font-size:.85rem;padding:14px 0">No habits yet.</p>', unsafe_allow_html=True)
    else:
        for habit in list(scenario.habits):
            st.markdown('<div class="hrow">', unsafe_allow_html=True)
            r1,r2,r3,r4,r5 = st.columns([3,1,2,1,.5])
            with r1:
                v = st.text_input("n", value=habit.name, key=f"hn_{habit.id}", label_visibility="collapsed")
                if v!=habit.name: habit.name=v
            with r2:
                v = st.number_input("$", value=float(habit.cost), min_value=0.0, step=.5, key=f"hc_{habit.id}", label_visibility="collapsed")
                if v!=habit.cost: habit.cost=v
            with r3:
                fl = FREQ_LABELS.get(habit.freq,"per month")
                nfl = st.selectbox("f", list(FREQ_OPTIONS.keys()), index=list(FREQ_OPTIONS.keys()).index(fl), key=f"hf_{habit.id}", label_visibility="collapsed")
                nf = FREQ_OPTIONS[nfl]
                if nf!=habit.freq: habit.freq=nf
            with r4:
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:.8rem;color:{scenario.color};padding-top:10px;font-weight:700">{fmt_usd(habit.yearly)}/yr</div>', unsafe_allow_html=True)
            with r5:
                if st.button("✕", key=f"hd_{habit.id}"):
                    scenario.habits=[x for x in scenario.habits if x.id!=habit.id]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── TABS ───────────────────────────────────────────────────────────────────────
t1, t2, t3 = st.tabs(["🧮  Calculator", "📋  Scenarios", "📊  Compare"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — QUICK CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════
with t1:
    st.markdown("""
    <div class="hero">
      <h1>What does your<br>habit really cost?</h1>
      <p>Type in any daily expense and see exactly what it would grow to if you invested it instead.</p>
    </div>
    """, unsafe_allow_html=True)

    i1, i2, i3 = st.columns(3)
    with i1: daily = st.number_input("Daily spend ($)", min_value=0.0, max_value=1000.0, value=6.50, step=0.50)
    with i2: cy    = st.slider("Years to invest", 1, 40, 10)
    with i3: cr    = st.slider("Annual return (%)", 0, 15, 7)

    invested = fv_daily(daily, cy, cr)
    spent    = daily * 365 * cy
    gain     = invested - spent
    yearly   = daily * 365

    st.markdown(f"""
    <div class="calc-box">
      <div class="calc-lbl">💡 if you invested instead of spent</div>
      <div class="calc-nums">
        <div class="calc-num-block">
          <div class="calc-num-sub">invested value</div>
          <div class="calc-num-val gold">{fmt_usd(invested)}</div>
        </div>
        <div class="calc-num-block">
          <div class="calc-num-sub">total spent</div>
          <div class="calc-num-val red">{fmt_usd(spent)}</div>
        </div>
        <div class="calc-num-block">
          <div class="calc-num-sub">opportunity cost</div>
          <div class="calc-num-val teal">{fmt_usd(gain)}</div>
        </div>
      </div>
      <div class="calc-insight">
        Spending <b>{fmt_usd_dec(daily)}/day</b> adds up to
        <span class="hl-gold">{fmt_usd(yearly)}/year</span>.
        Over {cy} years that's <span class="hl-red">{fmt_usd(spent)}</span> out of your pocket —
        but invested at {cr}% annually it would grow to
        <span class="hl-gold">{fmt_usd(invested)}</span>.
        The missed opportunity: <span class="hl-teal">{fmt_usd(gain)}</span>.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Habit comparison examples
    st.markdown('<div class="slbl">Common habits — 10-year comparison at 7% return</div>', unsafe_allow_html=True)
    examples = [
        ("☕ Daily latte",           6.50),
        ("🍔 Lunch out (workdays)",  14.00),
        ("🚬 Pack of cigarettes",    11.00),
        ("🍺 Daily beer",             8.00),
        ("🚕 Uber vs transit",       12.00),
        ("🎮 Gaming microtrans.",     5.00),
    ]
    ec = st.columns(3)
    for i,(name,cost) in enumerate(examples):
        iv = fv_daily(cost, 10, 7)
        sp = cost * 365 * 10
        with ec[i%3]:
            st.markdown(f"""
            <div class="ex-card">
              <div class="ex-name">{name}</div>
              <div class="ex-meta">{fmt_usd_dec(cost)}/day · 10 years · 7% return</div>
              <div class="ex-val">{fmt_usd(iv)}</div>
              <div class="ex-note">vs {fmt_usd(sp)} spent</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════
with t2:
    st.markdown("""
    <div class="hero" style="padding-bottom:20px">
      <h1>Your<br>scenarios</h1>
      <p>Build spending profiles and see their long-term cost.</p>
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([2,2,1])
    with sc1: st.session_state.years = st.slider("Project over (years)", 1, 30, st.session_state.years, key="sy")
    with sc2: st.session_state.rate  = st.slider("Annual return (%)", 0, 12, st.session_state.rate, key="sr")
    with sc3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if len(st.session_state.scenarios)<5:
            if st.button("＋ New", type="primary", use_container_width=True):
                used=[s.color for s in st.session_state.scenarios]
                col=next((c for c in SCENARIO_COLORS if c not in used),SCENARIO_COLORS[0])
                n=len(st.session_state.scenarios)+1
                st.session_state.scenarios.append(Scenario(f"Scenario {n}",col))
                st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if not st.session_state.scenarios:
        st.markdown('<div style="text-align:center;padding:80px 0;color:#2e2c28"><div style="font-size:3rem;margin-bottom:16px">📭</div><p>No scenarios yet.</p></div>', unsafe_allow_html=True)
    else:
        ncols = min(len(st.session_state.scenarios), 3)
        sc_cols = st.columns(ncols, gap="large")
        for i, s in enumerate(st.session_state.scenarios):
            r = calc_scenario(s, st.session_state.years, st.session_state.rate)
            with sc_cols[i % ncols]:
                st.markdown(f"""
                <div class="sc-card">
                  <div class="sc-top-bar" style="background:{s.color}"></div>
                  <div class="sc-hdr">
                    <div class="sc-dot" style="background:{s.color};box-shadow:0 0 10px {s.color}"></div>
                    <div class="sc-nm">{s.name}</div>
                  </div>
                  <div class="sc-grid">
                    <div class="sc-m"><div class="sc-ml">Daily</div><div class="sc-mv">{fmt_usd_dec(r['daily'])}</div></div>
                    <div class="sc-m"><div class="sc-ml">Per year</div><div class="sc-mv">{fmt_usd(r['yearly'])}</div></div>
                    <div class="sc-m big"><div class="sc-ml">💰 {st.session_state.years}yr invested value</div><div class="sc-mv">{fmt_usd(r['invested_value'])}</div></div>
                  </div>
                  <div class="tags">
                    {''.join(f'<span class="tag">{h.name}</span>' for h in s.habits[:4])}
                    {f'<span class="tag">+{len(s.habits)-4} more</span>' if len(s.habits)>4 else ''}
                    {f'<span class="tag" style="color:#2e2c28;font-style:italic">no habits yet</span>' if not s.habits else ''}
                  </div>
                </div>
                """, unsafe_allow_html=True)
                be, bd = st.columns(2)
                with be:
                    if st.button("✏ Edit", key=f"ed_{s.id}", use_container_width=True):
                        st.session_state.editing_id = s.id
                        st.rerun()
                with bd:
                    if st.button("✕ Remove", key=f"rm_{s.id}", use_container_width=True):
                        st.session_state.scenarios=[x for x in st.session_state.scenarios if x.id!=s.id]
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — COMPARE
# ═══════════════════════════════════════════════════════════════════════════════
with t3:
    years = st.session_state.years
    rate  = st.session_state.rate
    scenarios = st.session_state.scenarios

    st.markdown("""
    <div class="hero" style="padding-bottom:20px">
      <h1>Compare<br>scenarios</h1>
      <p>See the long-term financial difference between your choices.</p>
    </div>
    """, unsafe_allow_html=True)

    if not scenarios:
        st.markdown('<div style="text-align:center;padding:80px 0;color:#2e2c28"><div style="font-size:3rem;margin-bottom:16px">📊</div><p>Create scenarios first.</p></div>', unsafe_allow_html=True)
    else:
        cp1, cp2, cp3 = st.columns([2,2,1])
        with cp1: st.session_state.years = st.slider("Years", 1, 30, years, key="cy2"); years=st.session_state.years
        with cp2: st.session_state.rate  = st.slider("Annual return (%)", 0, 12, rate, key="cr2"); rate=st.session_state.rate
        with cp3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.download_button("⬇ CSV", export_csv(scenarios,years,rate), "regret.csv","text/csv", use_container_width=True)

        results = [(s, calc_scenario(s, years, rate)) for s in scenarios]
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Delta
        if len(results)>=2:
            sr = sorted(results, key=lambda x:x[1]["invested_value"], reverse=True)
            bs,br = sr[0]; ws,wr = sr[-1]
            if bs.id != ws.id:
                diff=br["invested_value"]-wr["invested_value"]
                st.markdown(f"""
                <div class="delta">
                  🚀 <strong style="color:{bs.color}">{bs.name}</strong>
                  leaves you <strong style="color:#e8c547;font-family:'JetBrains Mono',monospace">{fmt_usd(diff)}</strong>
                  richer than <strong style="color:{ws.color}">{ws.name}</strong>
                  over {years} years —
                  that's <strong style="color:#3ecfb2;font-family:'JetBrains Mono',monospace">{fmt_usd_dec(diff/years/365)}/day</strong>
                  in compounding difference.
                </div>
                """, unsafe_allow_html=True)

        # Summary cards
        cc = st.columns(min(len(results),3), gap="large")
        for i,(s,r) in enumerate(results):
            rgb=','.join(str(int(s.color.lstrip('#')[j:j+2],16)) for j in (0,2,4))
            with cc[i%3]:
                st.markdown(f"""
                <div class="cmp-card" style="--cc:{s.color}">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
                    <div style="width:8px;height:8px;border-radius:50%;background:{s.color};box-shadow:0 0 10px {s.color}"></div>
                    <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:.92rem">{s.name}</span>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                    <div style="background:rgba(255,255,255,.03);border-radius:9px;padding:10px 12px">
                      <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:#2e2c28;margin-bottom:3px">Daily</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:1.05rem;font-weight:700">{fmt_usd_dec(r['daily'])}</div>
                    </div>
                    <div style="background:rgba(255,255,255,.03);border-radius:9px;padding:10px 12px">
                      <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:#2e2c28;margin-bottom:3px">Per year</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:1.05rem;font-weight:700">{fmt_usd(r['yearly'])}</div>
                    </div>
                    <div style="background:rgba(255,255,255,.03);border-radius:9px;padding:10px 12px">
                      <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:#2e2c28;margin-bottom:3px">Total spent</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:1.05rem;font-weight:700;color:#e85d3c">{fmt_usd(r['total_spent'])}</div>
                    </div>
                    <div style="background:rgba({rgb},.08);border:1px solid rgba({rgb},.2);border-radius:9px;padding:10px 12px">
                      <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:#2e2c28;margin-bottom:3px">{years}yr invested</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:1.05rem;font-weight:700;color:{s.color}">{fmt_usd(r['invested_value'])}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Invested chart
        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-ttl">📈 invested value over {years} years at {rate}% return</div>', unsafe_allow_html=True)
        st.plotly_chart(make_chart([{"label":s.name,"data":r["invest_by_year"],"color":s.color} for s,r in results], years), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Spent chart
        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.markdown('<div class="chart-ttl">💸 total amount spent over time</div>', unsafe_allow_html=True)
        st.plotly_chart(make_chart([{"label":s.name,"data":r["spent_by_year"],"color":s.color} for s,r in results], years, dashed=True), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Habit breakdown
        st.markdown('<div class="slbl">Habit breakdown by scenario</div>', unsafe_allow_html=True)
        bd = st.columns(min(len(results),3), gap="large")
        for i,(s,r) in enumerate(results):
            with bd[i%3]:
                st.markdown(f'<div style="color:{s.color};font-family:Syne,sans-serif;font-size:.75rem;font-weight:700;margin-bottom:12px">{s.name}</div>', unsafe_allow_html=True)
                if not s.habits:
                    st.markdown('<p style="color:#2e2c28;font-size:.8rem">No habits</p>', unsafe_allow_html=True)
                    continue
                sh=sorted(s.habits,key=lambda h:h.yearly,reverse=True)
                mx=sh[0].yearly if sh else 1
                for h in sh:
                    p=int(h.yearly/mx*100)
                    st.markdown(f"""
                    <div style="margin-bottom:11px">
                      <div style="display:flex;justify-content:space-between;font-size:.76rem;margin-bottom:4px">
                        <span style="color:#7a766f">{h.name}</span>
                        <span style="font-family:'JetBrains Mono',monospace;color:{s.color}">{fmt_usd(h.yearly)}/yr</span>
                      </div>
                      <div style="background:rgba(255,255,255,.05);border-radius:4px;height:4px">
                        <div style="width:{p}%;background:linear-gradient(90deg,{s.color},{s.color}88);height:4px;border-radius:4px;transition:width .6s"></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f'<div style="border-top:1px solid rgba(255,255,255,.06);padding-top:9px;display:flex;justify-content:space-between;font-size:.76rem"><span style="color:#3a3733">Total</span><span style="font-family:JetBrains Mono,monospace;color:{s.color};font-weight:700">{fmt_usd(r["yearly"])}/yr</span></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)