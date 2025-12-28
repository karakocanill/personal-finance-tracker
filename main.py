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
        gram_altin = (2050.0 / 31.1035) * usd  # Ons Altın simülasyonu
        return {"USD": usd, "EUR": eur, "ALTIN": gram_altin}
    except:
        return {"USD": 30.50, "EUR": 33.10, "ALTIN": 2050.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Dashboard", page_icon="📈", layout="wide")

# CSS ile Estetik Dokunuşlar (Döviz Widget'ı için)
st.markdown("""
    <style>
    .market-widget {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        text-align: center;
    }
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
    st.title("💰 Kişisel Finans ve Analiz Portalı")
    st.caption("v11.0 | Streamlit Dashboard")

with auth_col:
    if st.session_state.user:
        st.write(f"👤 **{st.session_state.user}**")
        if st.button("Güvenli Çıkış"):
            st.session_state.user = None
            st.rerun()
    else:
        with st.popover("🔑 Giriş veya Kayıt"):
            tab_l, tab_r = st.tabs(["Giriş", "Kayıt"])
            with tab_l:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Giriş Yap"):
                    if u == "admin" and p == "12345":  # ADMIN HESABI
                        st.session_state.user = "ADMIN"
                        st.rerun()
                    elif u in st.session_state.db and st.session_state.db[u]['s'] == p:
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("Hatalı!")
            with tab_r:
                nu = st.text_input("New User")
                np = st.text_input("New Pass", type="password")
                if st.button("Kayıt Ol"):
                    if nu and nu not in st.session_state.db:
                        st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                        verileri_yaz(st.session_state.db)
                        st.success("Kayıt Başarılı!")

st.write("---")

# --- ANA PANEL (DEMO MODU / GİRİŞSİZ) ---
if st.session_state.user == "ADMIN":
    st.header("👑 Yönetici Paneli")
    st.write("Sistemdeki tüm kullanıcıların listesi ve verileri:")
    st.json(st.session_state.db)
    if st.button("Veritabanını Sıfırla (Kritik)"):
        st.session_state.db = {}
        verileri_yaz({})
        st.rerun()

else:
    # Sol Taraf: Finansal İşlemler (Giriş yapılmışsa aktif)
    # Orta Taraf: Grafikler ve Özet
    main_col, side_col = st.columns([7, 3])

    with main_col:
        if st.session_state.user:
            u_data = st.session_state.db[st.session_state.user]
            st.subheader(f"💵 Bakiyeniz: {u_data['b']:.2f} TL")

            t1, t2 = st.tabs(["📊 Analiz Grafiği", "📋 İşlem Geçmişi"])
            with t1:
                if u_data['g']:
                    df = pd.DataFrame(u_data['g'])
                    st.area_chart(df.groupby("k")["m"].sum())
            with t2:
                if u_data['g']:
                    st.dataframe(pd.DataFrame(u_data['g']), use_container_width=True)
        else:
            st.info(
                "⚠️ **Demo Modu:** Kendi cüzdanınızı yönetmek için sağ üstten giriş yapın. Şu an sadece genel piyasaları görüyorsunuz.")
            st.write("### Neden Kayıt Olmalısınız?")
            st.write("- Harcamalarınızı kategorize edin\n- PDF raporları alın\n- Geçmişinizi asla kaybetmeyin")

    # Sağ Taraf: Döviz Widget'ı (Senin istediğin 3'lü estetik alan)
    with side_col:
        st.subheader("🌍 Piyasa Verileri")
        st.markdown(f"""
            <div class="market-widget">
                <p>🇺🇸 <b>Dolar:</b> {kurlar['USD']:.2f} TL</p>
            </div><br>
            <div class="market-widget">
                <p>🇪🇺 <b>Euro:</b> {kurlar['EUR']:.2f} TL</p>
            </div><br>
            <div class="market-widget">
                <p>🟡 <b>Gram Altın:</b> {kurlar['ALTIN']:.0f} TL</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.user:
            st.write("---")
            st.subheader("📥 İşlem Girişi")
            with st.form("islem_formu"):
                tip = st.selectbox("Tür", ["Gelir", "Gider"])
                mik = st.number_input("Miktar", min_value=0.0)
                kat = st.selectbox("Kategori", ["Gıda", "Eğitim", "Oyun", "Ulaşım", "Maaş"])
                if st.form_submit_button("Kaydet"):
                    u_data['b'] += mik if tip == "Gelir" else -mik
                    u_data['g'].append({'t': datetime.now().strftime("%Y-%m-%d"), 'tip': tip, 'm': mik, 'k': kat})
                    verileri_yaz(st.session_state.db)
                    st.rerun()

# Alt Bilgi
st.write("---")
st.caption("Developed by Anıl | Üsküdar University Computer Engineering")