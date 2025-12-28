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
        return {"USD": usd, "EUR": eur, "GBP": gbp, "ALTIN": 2990.0, "GUMUS": 36.20}
    except:
        return {"USD": 30.5, "EUR": 33.0, "GBP": 38.5, "ALTIN": 2600, "GUMUS": 32}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Global Pro", page_icon="💎", layout="wide")

# CSS: Pro-Görünüm ve Widgetlar
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0b0e14; min-width: 320px; }
    .market-card {
        background-color: #1c2128;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #444c56;
        border-left: 6px solid #2ea043;
    }
    .market-card p { margin: 0; font-size: 11px; color: #768390; font-weight: bold; }
    .market-card h3 { margin: 5px 0 0 0; font-size: 20px; color: #adbac7; }
    </style>
    """, unsafe_allow_html=True)

# Oturum Yönetimi
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'user' not in st.session_state:
    st.session_state.user = None

kurlar = kurlari_getir()

# --- HEADER ---
h_col, a_col = st.columns([8, 2])
with h_col:
    st.title("💎 Anıl Finance Global: Ultimate Edition")
    st.caption(f"v13.1 | Üsküdar University CS Project | {datetime.now().strftime('%d.%m.%Y')}")

with a_col:
    if st.session_state.user:
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔐 Panel Girişi", use_container_width=True):
            t1, t2 = st.tabs(["Giriş", "Kayıt"])
            with t1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Login"):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"; st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u;
                        st.rerun()
                    else:
                        st.error("Hatalı!")
            with t2:
                nu = st.text_input("New User")
                np = st.text_input("New Pass", type="password")
                if st.button("Register"):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Kayıt Başarılı!")

st.write("---")

# --- SIDEBAR ---
with st.sidebar:
    if st.session_state.user and st.session_state.user != "ADMIN":
        st.subheader(f"👋 Panel: {st.session_state.user}")
        with st.form("sidebar_form", clear_on_submit=True):
            tip = st.selectbox("İşlem", ["Gelir", "Gider"])
            mik = st.number_input("Tutar (₺)", min_value=0.0)
            kat = st.selectbox("Kategori", ["Gıda", "Eğitim", "Oyun", "Ulaşım", "Maaş", "Yatırım"])
            if st.form_submit_button("Sisteme İşle", use_container_width=True):
                ud = st.session_state.db[st.session_state.user]
                ud['b'] += mik if tip == "Gelir" else -mik
                ud['g'].append({'t': datetime.now().strftime("%m-%d %H:%M"), 'tip': tip, 'm': mik, 'k': kat})
                verileri_yaz(st.session_state.db)
                st.rerun()
        st.write("---")

    st.subheader("🌍 Canlı Piyasalar")
    v_list = [("ABD DOLARI", "USD"), ("EURO", "EUR"), ("STERLİN", "GBP"), ("GR ALTIN", "ALTIN"), ("GR GÜMÜŞ", "GUMUS")]
    for l, k in v_list:
        st.markdown(f"""<div class="market-card"><p>{l}</p><h3>{kurlar[k]:.2f} ₺</h3></div>""", unsafe_allow_html=True)

# --- ANA PANEL ---
if st.session_state.user == "ADMIN":
    st.header("👑 Admin Panel")
    st.json(st.session_state.db)
elif st.session_state.user:
    ud = st.session_state.db[st.session_state.user]

    # AKILLI BÜTÇE ANALİZİ (YENİ ÖZELLİK)
    df = pd.DataFrame(ud['g']) if ud['g'] else pd.DataFrame()
    toplam_gelir = df[df['tip'] == 'Gelir']['m'].sum() if not df.empty else 0
    toplam_gider = df[df['tip'] == 'Gider']['m'].sum() if not df.empty else 0

    if toplam_gider > toplam_gelir and toplam_gelir > 0:
        st.warning(
            f"⚠️ **Bütçe Uyarısı:** Harcamalarınız ({toplam_gider:.2f} ₺) gelirlerinizi ({toplam_gelir:.2f} ₺) aşmış durumda! Tasarruf önerilir.")
    elif toplam_gelir > 0:
        st.success(f"✅ **Bütçe Durumu:** Harika! Gelirleriniz harcamalarınızdan fazla. Bakiye güvenli bölgede.")

    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Bakiye", f"{ud['b']:.2f} ₺")
    m2.metric("📊 İşlem", f"{len(ud['g'])} Adet")
    m3.metric("🇺🇸 USD Değeri", f"${(ud['b'] / kurlar['USD']):.2f}")

    t1, t2 = st.tabs(["📉 Harcama Analizi", "📋 İşlem Geçmişi"])
    with t1:
        if not df.empty: st.area_chart(df.groupby("k")["m"].sum())
    with t2:
        if not df.empty: st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.info("👋 **Giriş Yapılmadı:** Piyasaları soldan takip edebilir, bütçe yönetimi için kayıt olabilirsiniz.")

st.sidebar.caption("Ultimate Build v13.1")