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
        gram_altin = 2950.0  # Güncel simülasyon
        return {"USD": usd, "EUR": eur, "ALTIN": gram_altin}
    except:
        return {"USD": 30.0, "EUR": 32.0, "ALTIN": 2500.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro", page_icon="💹", layout="wide")

# CSS: Sidebar ve Koyu Tema Widget Tasarımı
st.markdown("""
    <style>
    /* Sidebar genişliği ve rengi */
    [data-testid="stSidebar"] {
        background-color: #111111;
        min-width: 350px;
    }
    /* Döviz Widget'ları */
    .market-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-right: 5px solid #00ff88;
        text-align: left;
    }
    .market-card p { margin: 0; font-size: 13px; color: #aaaaaa; font-weight: bold; }
    .market-card h3 { margin: 5px 0 0 0; font-size: 24px; color: #ffffff; }

    /* Metrik kutuları düzenleme */
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)

# Veriyi Başlat
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'user' not in st.session_state:
    st.session_state.user = None

kurlar = kurlari_getir()

# --- ÜST BAR (GİRİŞ / KAYIT) ---
h_col, a_col = st.columns([8, 2])
with h_col:
    st.title("💹 Finans Takip & Analiz Merkezi")
    st.caption("v12.1 Pro | Bilgisayar Mühendisliği Öğrenci Projesi")

with a_col:
    if st.session_state.user:
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔑 Giriş veya Kayıt", use_container_width=True):
            t1, t2 = st.tabs(["Giriş", "Kayıt"])
            with t1:
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.button("Giriş", key="login_btn"):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"; st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u;
                        st.rerun()
                    else:
                        st.error("Hatalı!")
            with t2:
                nu = st.text_input("Yeni Kullanıcı Adı")
                np = st.text_input("Yeni Şifre", type="password")
                if st.button("Kayıt Ol", key="reg_btn"):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Hesap oluşturuldu!")

st.write("---")

# --- SIDEBAR (SOL MENÜ) ---
with st.sidebar:
    if st.session_state.user and st.session_state.user != "ADMIN":
        st.subheader(f"👋 Hoş geldin, {st.session_state.user}")
        st.write("---")

        # YENİ İŞLEM FORMU (Sidebar'da)
        st.markdown("### 📥 İşlem Girişi")
        with st.form("islem_sidebar", clear_on_submit=True):
            islem_tipi = st.selectbox("Tür", ["Gelir", "Gider"])
            miktar = st.number_input("Miktar (TL)", min_value=0.0)
            kategori = st.selectbox("Kategori", ["Yemek", "Eğitim", "Hobi", "Ulaşım", "Kira", "Maaş", "Yatırım"])
            if st.form_submit_button("Sisteme Kaydet", use_container_width=True):
                u_verisi = st.session_state.db[st.session_state.user]
                u_verisi['b'] += miktar if islem_tipi == "Gelir" else -miktar
                u_verisi['g'].append(
                    {'t': datetime.now().strftime("%Y-%m-%d %H:%M"), 'tip': islem_tipi, 'm': miktar, 'k': kategori})
                verileri_yaz(st.session_state.db)
                st.rerun()

        st.write("---")

    # DÖVİZ WIDGET'LARI (Sol Menü Altı)
    st.markdown("### 🌍 Canlı Piyasalar")
    st.markdown(f"""
        <div class="market-card">
            <p>🇺🇸 ABD DOLARI</p>
            <h3>{kurlar['USD']:.2f} ₺</h3>
        </div>
        <div class="market-card">
            <p>🇪🇺 EURO</p>
            <h3>{kurlar['EUR']:.2f} ₺</h3>
        </div>
        <div class="market-card">
            <p>🟡 GRAM ALTIN</p>
            <h3>{kurlar['ALTIN']:.0f} ₺</h3>
        </div>
    """, unsafe_allow_html=True)

# --- ANA PANEL ---
if st.session_state.user == "ADMIN":
    st.header("👑 Admin Paneli")
    st.json(st.session_state.db)
elif st.session_state.user:
    u_data = st.session_state.db[st.session_state.user]

    # Üst Metrikler
    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Güncel Bakiyeniz", f"{u_data['b']:.2f} TL")
    m2.metric("📊 İşlem Sayısı", len(u_data['g']))
    m3.metric("📈 Durum", "Hesap Aktif")

    tab1, tab2 = st.tabs(["📉 Grafik Analizi", "📋 İşlem Geçmişi"])
    with tab1:
        if u_data['g']:
            df = pd.DataFrame(u_data['g'])
            st.area_chart(df.groupby("k")["m"].sum())
        else:
            st.info("Veri ekledikçe buradaki grafikler dolacaktır.")
    with tab2:
        if u_data['g']:
            st.dataframe(pd.DataFrame(u_data['g']).sort_index(ascending=False), use_container_width=True)
else:
    # DEMO GÖRÜNÜM
    st.info("👋 **Giriş Yapılmadı:** Lütfen sağ üstteki panelden kayıt olun veya giriş yapın.")
    st.write("---")
    st.subheader("Bu Platform ile Neler Yapabilirsiniz?")
    st.markdown("""
    * **Gelir ve Giderlerinizi** kategorilere ayırarak takip edin.
    * **Canlı Piyasa** verilerini (Dolar, Euro, Altın) anlık izleyin.
    * Harcamalarınızı **grafikler** üzerinden analiz edin.
    """)

st.sidebar.caption("v12.1 | Developed by Anıl")