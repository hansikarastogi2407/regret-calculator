# ◈ Regret Calculator

> See the true cost of your daily habits — and what they'd be worth if invested instead.

A Streamlit app that lets you build multiple spending scenarios, compare them over time with interactive charts, and export the data.

---

## Features

- **Multiple scenarios** — create up to 5 named scenarios with custom colors
- **Habit builder** — pick from 10 presets (coffee, Netflix, gym, etc.) or add custom habits with any cost and frequency
- **Compare view** — side-by-side summary cards, invested value chart, total spent chart, habit breakdown bars
- **Delta insight** — see exactly how much richer one scenario leaves you vs another
- **Export CSV** — download a year-by-year projection for all scenarios
- **Persistent settings** — years and return rate sliders apply globally

---

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/regret-calculator.git
cd regret-calculator

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch (`main`), and set **Main file path** to `app.py`
5. Click **Deploy** — live in ~60 seconds

---

## Project structure

```
regret-calculator/
├── app.py                  # Main Streamlit app (all pages + UI)
├── calc.py                 # Core calculation logic (Habit, Scenario, FV)
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Theme and server config
└── README.md
```

---

## Tech stack

- [Streamlit](https://streamlit.io) — UI framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [Pandas](https://pandas.pydata.org) — CSV export

---

## Customization tips

- **Add more presets** — edit the `PRESET_HABITS` list in `calc.py`
- **Change default scenarios** — edit `make_default_scenarios()` in `calc.py`
- **Adjust return rate range** — change `st.slider("Annual return (%)", 0, 12, ...)` in `app.py`
- **Theme colors** — edit `.streamlit/config.toml`
