import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF

# Veri dosyası
DOSYA_ADI = "finans_verileri.json"


def verileri_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                return json.load(dosya)
        except:
            pass
    return {"bakiye": 0.0, "gecmis": []}


def verileri_kaydet(veri):
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(veri, dosya, indent=4, ensure_ascii=False)


def piyasa_verilerini_al():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        res = requests.get(url)
        data = res.json()
        usd = data["rates"]["TRY"]
        eur = usd / data["rates"]["EUR"]
        ons_altin = 2050.0  # Örnek sabit değer
        gram_altin = (ons_altin / 31.1035) * usd
        return {"USD": usd, "EUR": eur, "ALTIN": gram_altin}
    except:
        return {"USD": 30.0, "EUR": 32.0, "ALTIN": 2000.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro Max", page_icon="💎", layout="wide")

# --- LOGIN SİSTEMİ (BASİT) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Finans Paneli Giriş")
    with st.form("login_form"):
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        btn = st.form_submit_button("Giriş Yap")

        if btn:
            if kullanici == "anil" and sifre == "uskudar2025":  # Burayı istediğin gibi değiştir
                st.session_state.logged_in = True
                st.success("Giriş Başarılı!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop()  # Giriş yapılmadıysa kodun geri kalanını çalıştırma

# --- ANA UYGULAMA (GİRİŞ YAPILDIKTAN SONRA) ---
if 'veri' not in st.session_state:
    st.session_state.veri = verileri_yukle()

# SIDEBAR
st.sidebar.title(f"👋 Hoş geldin, {st.session_state.logged_in}")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
piyasa = piyasa_verilerini_al()
st.sidebar.subheader("🌍 Canlı Piyasalar")
st.sidebar.metric("🇺🇸 USD/TRY", f"{piyasa['USD']:.2f} ₺")
st.sidebar.metric("🇪🇺 EUR/TRY", f"{piyasa['EUR']:.2f} ₺")
st.sidebar.metric("🟡 Altın (gr)", f"{piyasa['ALTIN']:.0f} ₺")

st.sidebar.markdown("---")
with st.sidebar.form("islem_form", clear_on_submit=True):
    t = st.selectbox("Tür", ["Gelir", "Gider"])
    m = st.number_input("Miktar (TL)", min_value=0.0)
    k = st.selectbox("Kategori", ["Eğitim", "Gıda", "Oyun", "Ulaşım", "Maaş", "Yatırım"])
    a = st.text_input("Açıklama")
    if st.form_submit_button("Kaydet"):
        if m > 0:
            st.session_state.veri["bakiye"] += m if t == "Gelir" else -m
            st.session_state.veri["gecmis"].append({
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tip": t, "miktar": m, "kategori": k, "aciklama": a
            })
            verileri_kaydet(st.session_state.veri)
            st.rerun()

# DASHBOARD
st.title("🚀 Kişisel Finans Dashboard v8.0")
c1, c2, c3 = st.columns(3)
bak = st.session_state.veri['bakiye']
c1.metric("💵 Bakiye", f"{bak:.2f} TL")
c2.metric("💰 USD Karşılığı", f"${(bak / piyasa['USD']):.2f}")
c3.metric("📊 Kayıt Sayısı", len(st.session_state.veri['gecmis']))

tab1, tab2, tab3 = st.tabs(["📋 Geçmiş", "📈 Analiz", "📄 Rapor"])

with tab1:
    if st.session_state.veri['gecmis']:
        st.dataframe(pd.DataFrame(st.session_state.veri['gecmis']), use_container_width=True)

with tab2:
    if st.session_state.veri['gecmis']:
        df = pd.DataFrame(st.session_state.veri['gecmis'])
        st.bar_chart(df.groupby("kategori")["miktar"].sum())

with tab3:
    if st.button("PDF Raporu Oluştur"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Finans Raporu", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Bakiye: {bak:.2f} TL", ln=True)

            # PDF'i stream olarak gönder (Hata almamak için latin-1)
            output = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 PDF İndir", data=output, file_name="rapor.pdf")
        except Exception as e:
            st.error(f"PDF Hatası: {e}")