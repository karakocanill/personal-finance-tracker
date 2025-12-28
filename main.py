import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime

# PDF kütüphanesini güvenli yükleme
try:
    from fpdf import FPDF

    PDF_DESTEGI = True
except ImportError:
    PDF_DESTEGI = False

# Dosya yolları
DOSYA_YOLU = "kullanici_verileri.json"


def verileri_oku():
    if os.path.exists(DOSYA_YOLU):
        try:
            with open(DOSYA_YOLU, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def verileri_yaz(data):
    with open(DOSYA_YOLU, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def kurlari_getir():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        d = r.json()
        usd = d["rates"]["TRY"]
        eur = usd / d["rates"]["EUR"]
        gbp = usd / d["rates"]["GBP"]
        return {"USD": usd, "EUR": eur, "GBP": gbp, "ALTIN": 2995.0, "GUMUS": 36.50}
    except:
        return {"USD": 30.5, "EUR": 33.0, "GBP": 38.5, "ALTIN": 2600, "GUMUS": 32}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro", page_icon="💹", layout="wide")

# CSS: Profesyonel ve Sade Tasarım
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0d1117; min-width: 320px; }
    .market-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #238636;
    }
    .market-card p { margin: 0; font-size: 11px; color: #8b949e; font-weight: bold; text-transform: uppercase; }
    .market-card h3 { margin: 5px 0 0 0; font-size: 20px; color: #f0f6fc; }
    </style>
    """, unsafe_allow_html=True)

# Oturum Yönetimi
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'user' not in st.session_state:
    st.session_state.user = None

kurlar = kurlari_getir()

# --- HEADER (BAŞLIK DÜZELTİLDİ) ---
h_col, a_col = st.columns([8, 2])
with h_col:
    st.title("💹 Anıl Finance: Professional Analytics")
    st.caption(f"Computer Engineering Project | {datetime.now().strftime('%Y')} Build")

with a_col:
    if st.session_state.user:
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔐 Access Portal", use_container_width=True):
            t1, t2 = st.tabs(["Login", "Sign Up"])
            with t1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Sign In", use_container_width=True):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"; st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u;
                        st.rerun()
                    else:
                        st.error("Authentication Failed.")
            with t2:
                nu = st.text_input("New Username")
                np = st.text_input("Set Password", type="password")
                if st.button("Create Account", use_container_width=True):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Account created successfully!")

st.write("---")

# --- SIDEBAR ---
with st.sidebar:
    if st.session_state.user and st.session_state.user != "ADMIN":
        st.subheader(f"User: {st.session_state.user}")
        with st.form("action_form", clear_on_submit=True):
            tip = st.selectbox("Transaction Type", ["Gelir", "Gider"])
            mik = st.number_input("Amount (TRY)", min_value=0.0)
            kat = st.selectbox("Category", ["Gıda", "Eğitim", "Oyun", "Ulaşım", "Kira", "Maaş", "Yatırım"])
            not_al = st.text_input("Note")
            if st.form_submit_button("Submit Record", use_container_width=True):
                ud = st.session_state.db[st.session_state.user]
                ud['b'] += mik if tip == "Gelir" else -mik
                ud['g'].append(
                    {'t': datetime.now().strftime("%Y-%m-%d %H:%M"), 'tip': tip, 'm': mik, 'k': kat, 'n': not_al})
                verileri_yaz(st.session_state.db)
                st.rerun()
        st.write("---")

    st.subheader("🌍 Live Market Indices")
    indices = [("USD / TRY", "USD"), ("EUR / TRY", "EUR"), ("GBP / TRY", "GBP"), ("Gold / gr", "ALTIN"),
               ("Silver / gr", "GUMUS")]
    for label, key in indices:
        st.markdown(f"""<div class="market-card"><p>{label}</p><h3>{kurlar[key]:.2f} ₺</h3></div>""",
                    unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
if st.session_state.user == "ADMIN":
    st.header("👑 Administrator Panel")
    st.json(st.session_state.db)
elif st.session_state.user:
    ud = st.session_state.db[st.session_state.user]

    # Bütçe Analizi (Daha Kibar Bir Dil)
    df = pd.DataFrame(ud['g']) if ud['g'] else pd.DataFrame()
    if not df.empty:
        gelir = df[df['tip'] == 'Gelir']['m'].sum()
        gider = df[df['tip'] == 'Gider']['m'].sum()
        if gider > gelir and gelir > 0:
            st.warning(
                f"💡 **Analysis:** Monthly expenses are currently exceeding income. Consider reviewing discretionary spending.")
        elif gelir > 0:
            st.success("✅ **Status:** Financial health is stable. Income currently exceeds total expenditures.")

    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Net Balance", f"{ud['b']:.2f} ₺")
    m2.metric("📊 Records", f"{len(ud['g'])} Items")
    m3.metric("🇺🇸 Valuation (USD)", f"${(ud['b'] / kurlar['USD']):.2f}")

    t1, t2 = st.tabs(["📉 Analytics", "📋 Transaction History"])
    with t1:
        if not df.empty: st.area_chart(df.groupby("k")["m"].sum())
    with t2:
        if not df.empty: st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.info("👋 **Public Mode:** Please sign in to manage your personal wallet and view detailed analytics.")
    st.markdown(
        "### Platform Capability:\n- Secure Multi-User Cloud Storage\n- Automated Budget Status Monitoring\n- Real-time Global Market API Integration")

st.sidebar.caption("Project v13.2 | Built by Anıl")