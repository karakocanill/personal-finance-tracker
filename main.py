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
        gram_altin = (2850.0)  # Manuel simülasyon
        return {"USD": usd, "EUR": eur, "ALTIN": gram_altin}
    except:
        return {"USD": 30.50, "EUR": 33.10, "ALTIN": 2500.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro", page_icon="💹", layout="wide", initial_sidebar_state="expanded")

# CSS: Sidebar ve Widget'lar için Özel Tasarım
st.markdown("""
    <style>
    /* Sidebar Arka Planı */
    [data-testid="stSidebar"] {
        background-color: #1e1e2e;
        color: white;
    }
    /* Özel Döviz Widget'ları (Sol Menü İçin) */
    .market-box {
        background-color: #2b2b3b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #7f5af0;
        text-align: left;
    }
    .market-box p { margin: 0; font-size: 12px; color: #94a1b2; }
    .market-box h3 { margin: 5px 0 0 0; font-size: 18px; color: #fffffe; }

    /* Ana Panel Yazı Renkleri */
    .stMarkdown p { color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# Veriyi Başlat
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'user' not in st.session_state:
    st.session_state.user = None

kurlar = kurlari_getir()

# --- ÜST BAR (GİRİŞ / KAYIT) ---
header_col, auth_col = st.columns([8, 2])
with header_col:
    st.title("💹 Kişisel Finans ve Analiz Portalı")
    st.caption("v12.0 Pro Build | Sidebar Management Enabled")

with auth_col:
    if st.session_state.user:
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔑 Giriş / Kayıt", use_container_width=True):
            t_in, t_up = st.tabs(["Giriş", "Kayıt"])
            with t_in:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Giriş", use_container_width=True):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"; st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u;
                        st.rerun()
                    else:
                        st.error("Hatalı!")
            with t_up:
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                if st.button("Hesap Oluştur", use_container_width=True):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Başarılı!")

st.write("---")

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    if st.session_state.user and st.session_state.user != "ADMIN":
        st.header(f"👋 Merhaba, {st.session_state.user}")
        st.write("---")

        # GELİR - GİDER FORMU (Tıpkı yeni sohbet gibi)
        st.subheader("➕ Yeni İşlem Ekle")
        with st.form("islem_formu", clear_on_submit=True):
            tip = st.selectbox("İşlem Tipi", ["Gelir", "Gider"])
            mik = st.number_input("Tutar (TL)", min_value=0.0, format="%.2f")
            kat = st.selectbox("Kategori", ["Gıda", "Eğitim", "Hobi", "Ulaşım", "Kira", "Maaş", "Yatırım"])
            not_bilgi = st.text_input("Açıklama / Not")
            if st.form_submit_button("Sisteme Kaydet", use_container_width=True):
                u_data = st.session_state.db[st.session_state.user]
                u_data['b'] += mik if tip == "Gelir" else -mik
                u_data['g'].append(
                    {'t': datetime.now().strftime("%Y-%m-%d %H:%M"), 'tip': tip, 'm': mik, 'k': kat, 'n': not_bilgi})
                verileri_yaz(st.session_state.db)
                st.rerun()

        st.write("---")

    # ÖZEL DÖVİZ WIDGETLARI (Sol Menüde En Altta)
    st.subheader("🌍 Piyasa Verileri")
    st.markdown(f"""
        <div class="market-box">
            <p>ABD DOLARI</p>
            <h3>{kurlar['USD']:.2f} ₺</h3>
        </div>
        <div class="market-box">
            <p>EURO</p>
            <h3>{kurlar['EUR']:.2f} ₺</h3>
        </div>
        <div class="market-box">
            <p>GRAM ALTIN</p>
            <h3>{kurlar['ALTIN']:.0f} ₺</h3>
        </div>
    """, unsafe_allow_html=True)

# --- ANA PANEL ---
if st.session_state.user == "ADMIN":
    st.header("👑 Admin Panel")
    st.json(st.session_state.db)
elif st.session_state.user:
    u_data = st.session_state.db[st.session_state.user]

    # Dashboard Metrikleri
    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Güncel Bakiyeniz", f"{u_data['b']:.2f} TL")
    c2.metric("📊 Toplam İşlem", len(u_data['g']))
    c3.metric("🇺🇸 Dolar Karşılığı", f"${(u_data['b'] / kurlar['USD']):.2f}")

    t1, t2 = st.tabs(["📉 Grafiksel Analiz", "📋 İşlem Geçmişi"])
    with t1:
        if u_data['g']:
            df = pd.DataFrame(u_data['g'])
            st.area_chart(df.groupby("k")["m"].sum())
    with t2:
        if u_data['g']:
            st.dataframe(pd.DataFrame(u_data['g']).sort_index(ascending=False), use_container_width=True)
else:
    # DEMO GÖRÜNÜM
    st.info("👋 **Demo Modu:** Bütçenizi yönetmek için sağ üstten giriş yapın.")
    st.write("---")
    st.subheader("Neden Kayıt Olmalısınız?")
    st.markdown(
        "* Harcamalarınızı sol menüden saniyeler içinde kaydedin.\n* Grafiklerle paranızın nereye gittiğini görün.\n* Döviz widget'ları ile piyasayı takip edin.")

st.sidebar.caption("v12.0 Build | Developed by Anıl")