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
    """Genişletilmiş Piyasa Verileri (USD, EUR, GBP, Gold, Silver)"""
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        d = r.json()
        usd = d["rates"]["TRY"]
        eur = usd / d["rates"]["EUR"]
        gbp = usd / d["rates"]["GBP"]
        # Simüle edilmiş değerli maden verileri (Anlık Ons bazlı hesaplanabilir)
        return {
            "USD": usd, "EUR": eur, "GBP": gbp,
            "ALTIN": 2980.0, "GUMUS": 35.50
        }
    except:
        return {"USD": 30.0, "EUR": 32.5, "GBP": 38.0, "ALTIN": 2500, "GUMUS": 30}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Global", page_icon="💹", layout="wide")

# CSS: Yüksek Kontrastlı Pro Widget Tasarımı
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0d1117; min-width: 320px; }
    .market-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
        border-left: 5px solid #238636;
    }
    .market-card p { margin: 0; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase; }
    .market-card h3 { margin: 5px 0 0 0; font-size: 22px; color: #f0f6fc; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Oturum Yönetimi
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'user' not in st.session_state:
    st.session_state.user = None

kurlar = kurlari_getir()

# --- HEADER (AUTH & TITLE) ---
h_col, a_col = st.columns([8, 2])
with h_col:
    st.title("💹 Anıl Global Finans Merkezi")
    st.caption("v13.0 | Multi-User Market Analysis Platform")

with a_col:
    if st.session_state.user:
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔐 Giriş / Kayıt", use_container_width=True):
            t1, t2 = st.tabs(["Giriş", "Kayıt"])
            with t1:
                u = st.text_input("Kullanıcı")
                p = st.text_input("Şifre", type="password")
                if st.button("Giriş", key="l_btn"):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"; st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u;
                        st.rerun()
                    else:
                        st.error("Hatalı!")
            with t2:
                nu = st.text_input("Yeni Kullanıcı")
                np = st.text_input("Yeni Şifre", type="password")
                if st.button("Kaydet", key="r_btn"):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Hesap açıldı!")

st.write("---")

# --- SIDEBAR (MARKET & INPUT) ---
with st.sidebar:
    if st.session_state.user and st.session_state.user != "ADMIN":
        st.subheader(f"👋 Panel: {st.session_state.user}")
        with st.form("islem_sidebar", clear_on_submit=True):
            tip = st.selectbox("Tür", ["Gelir", "Gider"])
            mik = st.number_input("Miktar (₺)", min_value=0.0)
            kat = st.selectbox("Kategori", ["Gıda", "Eğitim", "Ulaşım", "Kira", "Maaş", "Yatırım"])
            if st.form_submit_button("KAYDET", use_container_width=True):
                ud = st.session_state.db[st.session_state.user]
                ud['b'] += mik if tip == "Gelir" else -mik
                ud['g'].append({'t': datetime.now().strftime("%Y-%m-%d %H:%M"), 'tip': tip, 'm': mik, 'k': kat})
                verileri_yaz(st.session_state.db)
                st.rerun()
        st.write("---")

    st.subheader("🌍 Canlı Piyasalar")
    # Genişletilmiş Piyasa Kartları
    v_list = [("ABD DOLARI", "USD"), ("EURO", "EUR"), ("İNG. STERLİNİ", "GBP"), ("GRAM ALTIN", "ALTIN"),
              ("GRAM GÜMÜŞ", "GUMUS")]
    for label, key in v_list:
        st.markdown(f"""<div class="market-card"><p>{label}</p><h3>{kurlar[key]:.2f} ₺</h3></div>""",
                    unsafe_allow_html=True)

# --- ANA PANEL ---
if st.session_state.user == "ADMIN":
    st.header("👑 Yönetici İzleme Ekranı")
    st.json(st.session_state.db)
elif st.session_state.user:
    ud = st.session_state.db[st.session_state.user]
    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Toplam Bakiye", f"{ud['b']:.2f} ₺")
    m2.metric("📊 Toplam İşlem", f"{len(ud['g'])} Adet")
    m3.metric("🇺🇸 Dolar Bazında", f"${(ud['b'] / kurlar['USD']):.2f}")

    t1, t2 = st.tabs(["📉 Harcama Analizi", "📋 Kayıt Geçmişi"])
    with t1:
        if ud['g']:
            df = pd.DataFrame(ud['g'])
            st.area_chart(df.groupby("k")["m"].sum())
    with t2:
        if ud['g']:
            st.dataframe(pd.DataFrame(ud['g']).sort_index(ascending=False), use_container_width=True)
else:
    st.info("💡 **Giriş Yapılmadı:** Bütçenizi yönetmek için sağ üstten kayıt olun. Şu an demo piyasa modundasınız.")
    st.markdown("### Özellikler:\n- Multi-User Kayıt Sistemi\n- Canlı Döviz & Maden Takibi\n- Grafiksel Analizler")

st.sidebar.caption("v13.0 | Anıl Finance Global")