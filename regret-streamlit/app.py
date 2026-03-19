"""
Regret Calculator — Streamlit App
See the real cost of daily habits over time.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import uuid
import io

from calc import (
    Habit, Scenario, SCENARIO_COLORS, PRESET_HABITS, FREQ_OPTIONS, FREQ_LABELS,
    calc_scenario, make_default_scenarios, fmt_usd, fmt_usd_dec,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Regret Calculator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; }

/* Logo / title */
.app-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    letter-spacing: -0.02em;
    color: #f0ede6;
    margin-bottom: 0.2rem;
}
.app-tagline { font-size: 0.85rem; color: #9e9b94; margin-bottom: 1.5rem; }

/* Metric cards */
.metric-card {
    background: #1a1a1a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.metric-card.highlight {
    border-color: rgba(232,197,71,0.3);
    background: rgba(232,197,71,0.05);
}
.metric-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #5c5a55;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    color: #f0ede6;
}
.metric-value.accent { color: #e8c547; }

/* Delta banner */
.delta-banner {
    background: rgba(232,197,71,0.06);
    border: 1px solid rgba(232,197,71,0.2);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 0.9rem;
    color: #9e9b94;
    margin-bottom: 1.5rem;
}
.delta-banner strong { color: #f0ede6; }

/* Scenario header strip */
.scenario-strip {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}
.scenario-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
    display: inline-block;
}

/* Habit row */
.habit-tag {
    display: inline-block;
    font-size: 0.72rem;
    padding: 3px 9px;
    background: #1e1e1e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    color: #9e9b94;
    margin: 2px;
}

/* Section divider */
.section-title {
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #5c5a55;
    margin: 1.5rem 0 0.75rem;
}

/* Streamlit overrides */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select {
    background: #1a1a1a !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #f0ede6 !important;
    border-radius: 8px !important;
}
div[data-testid="stSlider"] { padding: 0; }

button[kind="primary"] {
    background: #e8c547 !important;
    color: #000 !important;
    border: none !important;
    font-weight: 500 !important;
}

.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

div[data-testid="stExpander"] {
    background: #1a1a1a;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────────────────────

if "scenarios" not in st.session_state:
    st.session_state.scenarios = make_default_scenarios()
if "years" not in st.session_state:
    st.session_state.years = 10
if "rate" not in st.session_state:
    st.session_state.rate = 7
if "active_page" not in st.session_state:
    st.session_state.active_page = "Scenarios"
if "editing_id" not in st.session_state:
    st.session_state.editing_id = None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="app-logo">◈ Regret Calc</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-tagline">See the true cost of daily habits.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Navigation</div>', unsafe_allow_html=True)
    pages = ["Scenarios", "Compare"]
    for pg in pages:
        active = st.session_state.active_page == pg
        if st.button(pg, use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.active_page = pg
            st.session_state.editing_id = None
            st.rerun()

    st.divider()
    st.markdown('<div class="section-title">Global settings</div>', unsafe_allow_html=True)
    st.session_state.years = st.slider("Years to project", 1, 30, st.session_state.years)
    st.session_state.rate  = st.slider("Annual return (%)", 0, 12, st.session_state.rate)

    st.divider()
    st.markdown('<div class="section-title">Scenarios</div>', unsafe_allow_html=True)
    for s in st.session_state.scenarios:
        dot = f'<span class="scenario-dot" style="background:{s.color}"></span>'
        st.markdown(f'{dot} **{s.name}**  `{fmt_usd(s.yearly_total)}/yr`', unsafe_allow_html=True)

    if len(st.session_state.scenarios) < 5:
        if st.button("＋ New scenario", use_container_width=True):
            used = [s.color for s in st.session_state.scenarios]
            color = next((c for c in SCENARIO_COLORS if c not in used), SCENARIO_COLORS[0])
            n = len(st.session_state.scenarios) + 1
            st.session_state.scenarios.append(Scenario(f"Scenario {n}", color))
            st.rerun()


# ── HELPERS ───────────────────────────────────────────────────────────────────

def metric_card(label, value, accent=False):
    cls = "metric-card highlight" if accent else "metric-card"
    val_cls = "metric-value accent" if accent else "metric-value"
    st.markdown(f"""
    <div class="{cls}">
        <div class="metric-label">{label}</div>
        <div class="{val_cls}">{value}</div>
    </div>""", unsafe_allow_html=True)


def make_chart(datasets, years, title, dashed=False):
    fig = go.Figure()
    xs = [f"Yr {i+1}" for i in range(years)]
    for ds in datasets:
        line = dict(color=ds["color"], width=2)
        if dashed:
            line["dash"] = "dot"
        fig.add_trace(go.Scatter(
            x=xs, y=ds["data"], name=ds["label"],
            mode="lines", fill="tozeroy" if not dashed else None,
            fillcolor=ds["color"] + "18" if not dashed else None,
            line=line,
            hovertemplate="%{fullData.name}: <b>$%{y:,.0f}</b><extra></extra>",
        ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#9e9b94"), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#9e9b94", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(size=11)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(size=11),
                   tickprefix="$", tickformat=",.0f"),
    )
    return fig


def export_csv(scenarios, years, rate):
    rows = []
    for i in range(years):
        yr = i + 1
        row = {"Year": yr}
        for s in scenarios:
            r = calc_scenario(s, yr, rate)
            row[f"{s.name} — Spent"]    = round(r["total_spent"])
            row[f"{s.name} — Invested"] = round(r["invested_value"])
        rows.append(row)
    df = pd.DataFrame(rows)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


# ── PAGE: SCENARIOS ───────────────────────────────────────────────────────────

def page_scenarios():
    if st.session_state.editing_id:
        page_editor(st.session_state.editing_id)
        return

    st.markdown('<h1 class="app-logo" style="font-size:2.2rem">Your scenarios</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-tagline" style="margin-bottom:2rem">Build spending scenarios and compare them side by side.</p>', unsafe_allow_html=True)

    scenarios = st.session_state.scenarios
    if not scenarios:
        st.info("No scenarios yet. Click '＋ New scenario' in the sidebar.")
        return

    cols = st.columns(min(len(scenarios), 3), gap="medium")
    for i, s in enumerate(scenarios):
        r = calc_scenario(s, st.session_state.years, st.session_state.rate)
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border-top:2px solid {s.color};background:#1a1a1a;border-radius:12px;padding:16px 18px;margin-bottom:8px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
                    <span style="width:8px;height:8px;border-radius:50%;background:{s.color};display:inline-block;flex-shrink:0"></span>
                    <span style="font-weight:500;font-size:0.9rem">{s.name}</span>
                </div>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                metric_card("Daily cost", fmt_usd_dec(r["daily"]))
            with c2:
                metric_card("Per year", fmt_usd(r["yearly"]))
            metric_card(f"{st.session_state.years}yr invested", fmt_usd(r["invested_value"]), accent=True)

            # Habit pills
            if s.habits:
                pills = " ".join(f'<span class="habit-tag">{h.name}</span>' for h in s.habits[:5])
                if len(s.habits) > 5:
                    pills += f'<span class="habit-tag">+{len(s.habits)-5} more</span>'
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.markdown('<span style="font-size:0.8rem;color:#5c5a55;font-style:italic">No habits yet</span>', unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            ec, dc = st.columns(2)
            with ec:
                if st.button("✏ Edit", key=f"edit_{s.id}", use_container_width=True):
                    st.session_state.editing_id = s.id
                    st.rerun()
            with dc:
                if st.button("✕ Remove", key=f"del_{s.id}", use_container_width=True):
                    st.session_state.scenarios = [x for x in st.session_state.scenarios if x.id != s.id]
                    st.rerun()
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ── PAGE: EDITOR ──────────────────────────────────────────────────────────────

def page_editor(scenario_id):
    scenario = next((s for s in st.session_state.scenarios if s.id == scenario_id), None)
    if not scenario:
        st.session_state.editing_id = None
        st.rerun()
        return

    if st.button("← Back to scenarios"):
        st.session_state.editing_id = None
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_name, col_color, col_total = st.columns([3, 2, 1])
    with col_name:
        new_name = st.text_input("Scenario name", value=scenario.name, label_visibility="collapsed",
                                  placeholder="Scenario name")
        if new_name != scenario.name:
            scenario.name = new_name

    with col_color:
        color_map = {"🟡 Gold": "#e8c547","🟢 Teal": "#3ecfb2","🔵 Blue": "#4a9eff",
                     "🩷 Pink": "#e85d8a","🟣 Purple": "#b88aff"}
        cur_label = next((k for k,v in color_map.items() if v == scenario.color), "🟡 Gold")
        chosen = st.selectbox("Color", list(color_map.keys()), index=list(color_map.keys()).index(cur_label),
                               label_visibility="collapsed")
        scenario.color = color_map[chosen]

    with col_total:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:1.5rem;font-weight:500;color:{scenario.color};padding-top:4px">{fmt_usd(scenario.yearly_total)}<span style="font-size:0.8rem;color:#5c5a55">/yr</span></div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="section-title">Add habits from presets</div>', unsafe_allow_html=True)
    preset_cols = st.columns(5)
    for i, p in enumerate(PRESET_HABITS):
        with preset_cols[i % 5]:
            already = any(h.name == p["name"] for h in scenario.habits)
            label = f"✓ {p['name'].split('/')[0].strip()}" if already else f"＋ {p['name'].split('/')[0].strip()}"
            if st.button(label, key=f"preset_{scenario_id}_{p['name']}", use_container_width=True,
                         disabled=already):
                scenario.habits.append(Habit(p["name"], p["cost"], p["freq"]))
                st.rerun()

    st.markdown('<div class="section-title">Habits</div>', unsafe_allow_html=True)

    # Add custom habit
    with st.expander("＋ Add custom habit"):
        cc1, cc2, cc3, cc4 = st.columns([3, 1, 2, 1])
        with cc1: cname = st.text_input("Name", placeholder="e.g. Morning juice", key=f"cname_{scenario_id}")
        with cc2: ccost = st.number_input("$ cost", min_value=0.0, step=0.50, value=5.0, key=f"ccost_{scenario_id}")
        with cc3: cfreq_label = st.selectbox("Frequency", list(FREQ_OPTIONS.keys()), key=f"cfreq_{scenario_id}")
        with cc4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Add", key=f"cadd_{scenario_id}", type="primary"):
                if cname.strip():
                    scenario.habits.append(Habit(cname.strip(), ccost, FREQ_OPTIONS[cfreq_label]))
                    st.rerun()

    if not scenario.habits:
        st.markdown('<p style="color:#5c5a55;font-style:italic;font-size:0.85rem;padding:20px 0">No habits yet. Add from presets above or create a custom one.</p>', unsafe_allow_html=True)
    else:
        for habit in list(scenario.habits):
            h1, h2, h3, h4, h5 = st.columns([3, 1, 2, 1, 0.5])
            with h1:
                new_hname = st.text_input("Name", value=habit.name, key=f"hname_{habit.id}",
                                           label_visibility="collapsed")
                if new_hname != habit.name: habit.name = new_hname
            with h2:
                new_cost = st.number_input("Cost", value=float(habit.cost), min_value=0.0, step=0.5,
                                            key=f"hcost_{habit.id}", label_visibility="collapsed")
                if new_cost != habit.cost: habit.cost = new_cost
            with h3:
                freq_label = FREQ_LABELS.get(habit.freq, "per month")
                new_freq_label = st.selectbox("Freq", list(FREQ_OPTIONS.keys()),
                                               index=list(FREQ_OPTIONS.keys()).index(freq_label),
                                               key=f"hfreq_{habit.id}", label_visibility="collapsed")
                new_freq = FREQ_OPTIONS[new_freq_label]
                if new_freq != habit.freq: habit.freq = new_freq
            with h4:
                st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:0.85rem;color:{scenario.color};padding-top:10px">{fmt_usd(habit.yearly)}/yr</div>', unsafe_allow_html=True)
            with h5:
                if st.button("✕", key=f"hdel_{habit.id}"):
                    scenario.habits = [x for x in scenario.habits if x.id != habit.id]
                    st.rerun()


# ── PAGE: COMPARE ─────────────────────────────────────────────────────────────

def page_compare():
    years = st.session_state.years
    rate  = st.session_state.rate
    scenarios = st.session_state.scenarios

    st.markdown('<h1 class="app-logo" style="font-size:2.2rem">Compare</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-tagline" style="margin-bottom:1.5rem">See how your scenarios play out over time.</p>', unsafe_allow_html=True)

    if not scenarios:
        st.info("Add at least one scenario in the Scenarios tab.")
        return

    results = [(s, calc_scenario(s, years, rate)) for s in scenarios]

    # Export CSV button
    csv_data = export_csv(scenarios, years, rate)
    st.download_button(
        label="⬇ Export CSV",
        data=csv_data,
        file_name="regret-calculator.csv",
        mime="text/csv",
    )

    # Delta callout
    if len(results) >= 2:
        sorted_r = sorted(results, key=lambda x: x[1]["invested_value"], reverse=True)
        best_s, best_r = sorted_r[0]
        worst_s, worst_r = sorted_r[-1]
        if best_s.id != worst_s.id:
            diff = best_r["invested_value"] - worst_r["invested_value"]
            st.markdown(f"""
            <div class="delta-banner">
                ↑ <strong style="color:{best_s.color}">{best_s.name}</strong>
                leaves you <strong style="color:{best_s.color}">{fmt_usd(diff)}</strong>
                richer than <strong style="color:{worst_s.color}">{worst_s.name}</strong>
                over {years} years.
            </div>""", unsafe_allow_html=True)

    # Summary cards
    cols = st.columns(min(len(results), 3), gap="medium")
    for i, (s, r) in enumerate(results):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border-top:2px solid {s.color};background:#1a1a1a;border-radius:12px;padding:14px 16px;margin-bottom:4px">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                    <span style="width:6px;height:6px;border-radius:50%;background:{s.color};display:inline-block"></span>
                    <span style="font-size:0.85rem;font-weight:500">{s.name}</span>
                </div>
            </div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                metric_card("Daily", fmt_usd_dec(r["daily"]))
                metric_card("Total spent", fmt_usd(r["total_spent"]))
            with c2:
                metric_card("Per year", fmt_usd(r["yearly"]))
                metric_card(f"{years}yr invested", fmt_usd(r["invested_value"]), accent=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Invested value chart
    invest_datasets = [{"label": s.name, "data": r["invest_by_year"], "color": s.color}
                       for s, r in results]
    st.plotly_chart(
        make_chart(invest_datasets, years, f"If invested at {rate}% annually"),
        use_container_width=True
    )

    # Spent chart
    spent_datasets = [{"label": s.name, "data": r["spent_by_year"], "color": s.color}
                      for s, r in results]
    st.plotly_chart(
        make_chart(spent_datasets, years, "Total spent over time", dashed=True),
        use_container_width=True
    )

    # Habit breakdown tables
    st.markdown('<div class="section-title">Habit breakdown by scenario</div>', unsafe_allow_html=True)
    bcols = st.columns(min(len(results), 3), gap="medium")
    for i, (s, r) in enumerate(results):
        with bcols[i % 3]:
            st.markdown(f'<div style="color:{s.color};font-size:0.8rem;font-weight:500;margin-bottom:8px">{s.name}</div>', unsafe_allow_html=True)
            if not s.habits:
                st.markdown('<p style="color:#5c5a55;font-size:0.8rem">No habits</p>', unsafe_allow_html=True)
                continue
            sorted_habits = sorted(s.habits, key=lambda h: h.yearly, reverse=True)
            max_y = sorted_habits[0].yearly if sorted_habits else 1
            for h in sorted_habits:
                pct = int(h.yearly / max_y * 100)
                st.markdown(f"""
                <div style="margin-bottom:8px">
                    <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#9e9b94;margin-bottom:3px">
                        <span>{h.name}</span><span style="font-family:DM Mono,monospace">{fmt_usd(h.yearly)}/yr</span>
                    </div>
                    <div style="background:#272727;border-radius:3px;height:4px">
                        <div style="width:{pct}%;background:{s.color};height:4px;border-radius:3px"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="border-top:1px solid rgba(255,255,255,0.07);margin-top:8px;padding-top:8px;display:flex;justify-content:space-between;font-size:0.78rem;color:#5c5a55">
                <span>Total</span>
                <span style="font-family:DM Mono,monospace;color:{s.color}">{fmt_usd(r['yearly'])}/yr</span>
            </div>""", unsafe_allow_html=True)


# ── ROUTER ────────────────────────────────────────────────────────────────────

if st.session_state.active_page == "Scenarios":
    page_scenarios()
elif st.session_state.active_page == "Compare":
    page_compare()
