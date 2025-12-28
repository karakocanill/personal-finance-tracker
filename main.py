import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime

# Securely attempt to load the PDF library
try:
    from fpdf import FPDF

    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# File Paths
DATA_FILE = "kullanici_verileri.json"


def load_data():
    """Loads all user data from the local JSON storage."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_data(data):
    """Saves all user data to the local JSON storage."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def fetch_market_rates():
    """Fetches real-time market data (USD, EUR, GBP, Gold, Silver)."""
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        d = r.json()
        usd_try = d["rates"]["TRY"]
        eur_try = usd_try / d["rates"]["EUR"]
        gbp_try = usd_try / d["rates"]["GBP"]
        return {
            "USD": usd_try,
            "EUR": eur_try,
            "GBP": gbp_try,
            "GOLD": 2998.50,
            "SILVER": 36.80
        }
    except:
        return {"USD": 30.5, "EUR": 33.2, "GBP": 38.8, "GOLD": 2700, "SILVER": 33}


# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Anıl Finance Global", page_icon="💹", layout="wide")

# CSS: High-Contrast Professional UI
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0d1117; min-width: 330px; }
    .market-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #238636;
    }
    .market-card p { margin: 0; font-size: 11px; color: #8b949e; font-weight: 700; text-transform: uppercase; }
    .market-card h3 { margin: 5px 0 0 0; font-size: 21px; color: #f0f6fc; }
    .stMetric { border-radius: 12px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'db' not in st.session_state:
    st.session_state.db = load_data()
if 'user' not in st.session_state:
    st.session_state.user = None

market_data = fetch_market_rates()

# --- HEADER SECTION ---
h_col, a_col = st.columns([8, 2])
with h_col:
    st.title("💹 Anıl Finance: Global Analytics")
    st.caption(f"Computer Engineering Portfolio Project | v14.0 Launch Build")

with a_col:
    if st.session_state.user:
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔐 Access Portal", use_container_width=True):
            t1, t2 = st.tabs(["Sign In", "Create Account"])
            with t1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Log In", use_container_width=True):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"
                        st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("Authentication failed.")
            with t2:
                nu = st.text_input("Choose Username")
                np = st.text_input("Set Password", type="password")
                if st.button("Register", use_container_width=True):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        save_data(st.session_state.db)
                        st.success("Account created successfully!")

st.write("---")

# --- SIDEBAR: TRANSACTION & MARKET ---
with st.sidebar:
    if st.session_state.user and st.session_state.user != "ADMIN":
        st.subheader(f"Account: {st.session_state.user}")
        with st.form("transaction_form", clear_on_submit=True):
            t_type = st.selectbox("Transaction Type", ["Income", "Expense"])
            amount = st.number_input("Amount (TRY)", min_value=0.0, format="%.2f")
            category = st.selectbox("Category",
                                    ["Education", "Food", "Leisure", "Travel", "Rent", "Salary", "Investment"])
            note = st.text_input("Notes")
            if st.form_submit_button("Submit Record", use_container_width=True):
                ud = st.session_state.db[st.session_state.user]
                ud['b'] += amount if t_type == "Income" else -amount
                ud['g'].append({
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'type': t_type,
                    'amount': amount,
                    'cat': category,
                    'note': note
                })
                save_data(st.session_state.db)
                st.rerun()
        st.write("---")

    st.subheader("🌍 Live Market Indices")
    indices = [("USD / TRY", "USD"), ("EUR / TRY", "EUR"), ("GBP / TRY", "GBP"), ("GOLD / gr", "GOLD"),
               ("SILVER / gr", "SILVER")]
    for label, key in indices:
        st.markdown(f"""<div class="market-card"><p>{label}</p><h3>{market_data[key]:.2f} ₺</h3></div>""",
                    unsafe_allow_html=True)

# --- MAIN DASHBOARD PANEL ---
if st.session_state.user == "ADMIN":
    st.header("👑 Global Administrator Panel")
    st.json(st.session_state.db)
elif st.session_state.user:
    ud = st.session_state.db[st.session_state.user]
    df = pd.DataFrame(ud['g']) if ud['g'] else pd.DataFrame()

    # Smart Budget Analysis
    if not df.empty:
        total_inc = df[df['type'] == 'Income']['amount'].sum()
        total_exp = df[df['type'] == 'Expense']['amount'].sum()
        if total_exp > total_inc and total_inc > 0:
            st.warning(
                "💡 **Financial Insight:** Your expenditures are currently exceeding your total income. Re-evaluating your budget is recommended.")
        elif total_inc > 0:
            st.success("✅ **Status:** Your financial status is healthy. Income remains above expenditures.")

    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Net Balance", f"{ud['b']:.2f} ₺")
    m2.metric("📊 Records", f"{len(ud['g'])} Items")
    m3.metric("🇺🇸 USD Value", f"${(ud['b'] / market_data['USD']):.2f}")

    tab_graph, tab_table = st.tabs(["📉 Visual Analytics", "📋 Transaction History"])
    with tab_graph:
        if not df.empty: st.area_chart(df.groupby("cat")["amount"].sum())
    with tab_table:
        if not df.empty: st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.info("👋 **Welcome!** Please sign in to manage your personal wallet. You are currently in Demo View.")
    st.markdown(
        "### Platform Features:\n- Multi-User Cloud Data Management\n- Real-Time Global Market API Tracking\n- Automated Fiscal Health Analysis")

st.sidebar.caption("v14.0 Global Build | Built by Anıl")