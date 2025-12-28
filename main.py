import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime

# PDF kütüphanesini hata vermeden yükleme denemesi
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
        return {"USD": d["rates"]["TRY"], "EUR": d["rates"]["TRY"] / d["rates"]["EUR"]}
    except:
        return {"USD": 30.0, "EUR": 32.0}


# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Anıl Finance v10", page_icon="📈", layout="wide")

# Oturum yönetimi
if 'db' not in st.session_state:
    st.session_state.db = verileri_oku()
if 'kullanici' not in st.session_state:
    st.session_state.kullanici = None

kurlar = kurlari_getir()

# --- HEADER VE AUTH ---
c_baslik, c_giris = st.columns([3, 1])
with c_baslik:
    st.title("🌐 Anıl Global Finans Paneli")
    st.caption("v10.0 Stable Build | Multi-User SaaS")

with c_giris:
    if st.session_state.kullanici:
        st.write(f"👤 **{st.session_state.kullanici}**")
        if st.button("Çıkış"):
            st.session_state.kullanici = None
            st.rerun()
    else:
        secenek = st.radio("Hesap", ["İncele", "Giriş", "Kayıt"], horizontal=True)

# Auth İşlemleri
if not st.session_state.kullanici:
    if secenek == "Giriş":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Giriş Yap"):
            if u in st.session_state.db and st.session_state.db[u]['s'] == p:
                st.session_state.kullanici = u
                st.rerun()
            else:
                st.error("Hatalı!")
    elif secenek == "Kayıt":
        nu = st.text_input("New User")
        np = st.text_input("New Pass", type="password")
        if st.button("Kayıt Ol"):
            if nu and nu not in st.session_state.db:
                st.session_state.db[nu] = {'s': np, 'b': 0.0, 'g': []}
                verileri_yaz(st.session_state.db)
                st.success("Hesap açıldı!")

# --- PİYASA EKRANI (HERKESE AÇIK) ---
st.write("---")
col1, col2, col3 = st.columns(3)
col1.metric("🇺🇸 Dolar", f"{kurlar['USD']:.2f} TL")
col2.metric("🇪🇺 Euro", f"{kurlar['EUR']:.2f} TL")
col3.info("Detaylı analiz için giriş yapın.")

# --- KULLANICI PANELİ ---
if st.session_state.kullanici:
    u_verisi = st.session_state.db[st.session_state.kullanici]

    st.sidebar.header("İşlem Ekle")
    with st.sidebar.form("ekle"):
        tip = st.selectbox("Tip", ["Gelir", "Gider"])
        mik = st.number_input("Tutar", min_value=0.0)
        kat = st.selectbox("Kat", ["Gıda", "Eğitim", "Hobi", "Ulaşım", "Maaş"])
        if st.form_submit_button("Ekle"):
            u_verisi['b'] += mik if tip == "Gelir" else -mik
            u_verisi['g'].append({'t': datetime.now().strftime("%Y-%m-%d"), 'tip': tip, 'm': mik, 'k': kat})
            verileri_yaz(st.session_state.db)
            st.rerun()

    st.subheader(f"💰 Cüzdan Bakiyesi: {u_verisi['b']:.2f} TL")
    t1, t2 = st.tabs(["Geçmiş", "Rapor"])

    with t1:
        if u_verisi['g']: st.dataframe(pd.DataFrame(u_verisi['g']), use_container_width=True)

    with t2:
        if not PDF_DESTEGI:
            st.warning("PDF sistemi hazır değil, bekleyiniz...")
        elif st.button("PDF İndir"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt=f"Rapor: {st.session_state.kullanici}", ln=True, align='C')
            st.download_button("Download", pdf.output(dest='S').encode('latin-1'), "rapor.pdf")