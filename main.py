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
        gram_altin = (2800.0)  # Manuel simülasyon veya API'den çekilebilir
        return {"USD": usd, "EUR": eur, "ALTIN": gram_altin}
    except:
        return {"USD": 30.50, "EUR": 33.10, "ALTIN": 2500.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Dashboard", page_icon="📈", layout="wide")

# CSS GÜNCELLEMESİ: Yazıları koyu ve görünür yaptık
st.markdown("""
    <style>
    .market-widget {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #007bff;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .market-widget p { 
        margin: 0; 
        font-size: 14px; 
        color: #495057 !important; /* Koyu Gri Yazı */
        font-weight: bold;
    }
    .market-widget h4 { 
        margin: 5px 0 0 0; 
        color: #212529 !important; /* Siyah Yazı */
        font-size: 22px;
    }
    </style>
    """, unsafe_allow_html=True)

# Veriyi Başlat
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'user' not in st.session_state:
    st.session_state.user = None

kurlar = kurlari_getir()

# --- ÜST BAR ---
header_col, auth_col = st.columns([8, 2])

with header_col:
    st.title("💰 Kişisel Finans ve Analiz Portalı")
    st.caption("v11.1 | Visibility Patch")

with auth_col:
    if st.session_state.user:
        st.write(f"👤 **{st.session_state.user}**")
        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔑 Giriş veya Kayıt", use_container_width=True):
            tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
            with tab_l:
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.button("Giriş", use_container_width=True):
                    if u == "admin" and p == "12345":
                        st.session_state.user = "ADMIN"
                        st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("Hatalı!")
            with tab_r:
                nu = st.text_input("Yeni Kullanıcı Adı")
                np = st.text_input("Yeni Şifre", type="password")
                if st.button("Hesap Oluştur", use_container_width=True):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Kayıt Başarılı!")

st.write("---")

# --- ANA PANEL ---
if st.session_state.user == "ADMIN":
    st.header("👑 Sistem Yönetici Paneli")
    st.json(st.session_state.db)
else:
    main_col, side_col = st.columns([7, 3])

    with main_col:
        if st.session_state.user:
            u_data = st.session_state.db[st.session_state.user]
            st.subheader(f"💵 Mevcut Bakiyeniz: {u_data['b']:.2f} TL")
            t1, t2 = st.tabs(["📊 Harcama Analizi", "📋 İşlem Geçmişi"])
            with t1:
                if u_data['g']:
                    df = pd.DataFrame(u_data['g'])
                    st.area_chart(df.groupby("k")["m"].sum())
            with t2:
                if u_data['g']:
                    st.dataframe(pd.DataFrame(u_data['g']).sort_index(ascending=False), use_container_width=True)
        else:
            st.info("👋 **Demo Modu:** Kendi cüzdanınızı yönetmek için sağ üstten giriş yapın.")
            st.write("---")
            st.subheader("💡 Neden Üye Olmalısınız?")
            st.markdown("* 💰 **Cüzdan Takibi**\n* 📉 **Grafiksel Analiz**\n* 📄 **PDF Raporu**")

    # SAĞ TARAF: DÜZELTİLEN WIDGET'LAR
    with side_col:
        st.subheader("🌍 Piyasa Göstergeleri")
        st.markdown(f"""
            <div class="market-widget">
                <p>🇺🇸 ABD DOLARI</p>
                <h4>{kurlar['USD']:.2f} TL</h4>
            </div>
            <div class="market-widget">
                <p>🇪🇺 EURO</p>
                <h4>{kurlar['EUR']:.2f} TL</h4>
            </div>
            <div class="market-widget">
                <p>🟡 GRAM ALTIN</p>
                <h4>{kurlar['ALTIN']:.0f} TL</h4>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.user:
            st.write("---")
            st.subheader("📥 Yeni İşlem Ekle")
            with st.form("hizli_islem", clear_on_submit=True):
                tip = st.selectbox("İşlem Tipi", ["Gelir", "Gider"])
                mik = st.number_input("Miktar", min_value=0.0)
                kat = st.selectbox("Kategori", ["Gıda", "Eğitim", "Oyun/Hobi", "Ulaşım", "Kira", "Maaş"])
                if st.form_submit_button("Sisteme İşle", use_container_width=True):
                    u_data['b'] += mik if tip == "Gelir" else -mik
                    u_data['g'].append({'t': datetime.now().strftime("%Y-%m-%d %H:%M"), 'tip': tip, 'm': mik, 'k': kat})
                    verileri_yaz(st.session_state.db)
                    st.rerun()

st.write("---")
st.caption("Developed by Anıl | Visibility Patch v11.1")