import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF

# Veri dosyası
DOSYA_ADI = "kullanici_verileri.json"


def verileri_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                return json.load(dosya)
        except:
            pass
    return {}


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
        return {"USD": usd, "EUR": eur}
    except:
        return {"USD": 30.0, "EUR": 32.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro Max", page_icon="💎", layout="wide")

# Veri Altyapısını Başlat
if 'tum_veriler' not in st.session_state:
    st.session_state.tum_veriler = verileri_yukle()
if 'user' not in st.session_state:
    st.session_state.user = None

# --- ÜST MENÜ: GİRİŞ / KAYIT ---
piyasa = piyasa_verilerini_al()

# Sağ üst köşede giriş butonu simülasyonu
with st.container():
    col_t, col_l = st.columns([8, 2])
    with col_t:
        st.title("🚀 Global Finans Dashboard")
    with col_l:
        if st.session_state.user:
            st.write(f"👤 {st.session_state.user}")
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()
        else:
            mod = st.selectbox("Hesap İşlemi", ["Görüntüleme Modu", "Giriş Yap", "Kayıt Ol"])

# --- GİRİŞ / KAYIT MANTIĞI ---
if not st.session_state.user:
    if mod == "Giriş Yap":
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                if u in st.session_state.tum_veriler and st.session_state.tum_veriler[u]['sifre'] == p:
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Hatalı bilgiler!")
    elif mod == "Kayıt Ol":
        with st.form("register"):
            new_u = st.text_input("Yeni Kullanıcı Adı")
            new_p = st.text_input("Şifre Belirle", type="password")
            if st.form_submit_button("Hesap Oluştur"):
                if new_u and new_u not in st.session_state.tum_veriler:
                    st.session_state.tum_veriler[new_u] = {"sifre": new_p, "bakiye": 0.0, "gecmis": []}
                    verileri_kaydet(st.session_state.tum_veriler)
                    st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                else:
                    st.error("Bu kullanıcı adı alınmış veya geçersiz.")

# --- ANA PANEL: HERKESE AÇIK KISIM (PİYASALAR) ---
st.write("---")
c1, c2, c3 = st.columns(3)
c1.metric("🇺🇸 USD/TRY", f"{piyasa['USD']:.2f} ₺")
c2.metric("🇪🇺 EUR/TRY", f"{piyasa['EUR']:.2f} ₺")
c3.info("Kendi finansal verilerinizi yönetmek için lütfen giriş yapın.")

# --- KULLANICIYA ÖZEL KISIM ---
if st.session_state.user:
    user_data = st.session_state.tum_veriler[st.session_state.user]

    st.sidebar.header(f"📥 {st.session_state.user} Paneli")
    with st.sidebar.form("islem"):
        tip = st.selectbox("Tür", ["Gelir", "Gider"])
        mik = st.number_input("Miktar", min_value=0.0)
        acik = st.text_input("Açıklama")
        if st.form_submit_button("Kaydet"):
            user_data["bakiye"] += mik if tip == "Gelir" else -mik
            user_data["gecmis"].append(
                {"tarih": datetime.now().strftime("%Y-%m-%d"), "tip": tip, "miktar": mik, "ozet": acik})
            verileri_kaydet(st.session_state.tum_veriler)
            st.rerun()

    st.subheader(f"💰 Bakiyeniz: {user_data['bakiye']:.2f} TL")
    if user_data["gecmis"]:
        st.dataframe(pd.DataFrame(user_data["gecmis"]), use_container_width=True)

        # PDF BUTONU (Hata Alınan Kısım - Try-Except İçinde)
        if st.button("📄 Raporu PDF İndir"):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt=f"{st.session_state.user} Finans Raporu", ln=True, align='C')
                out = pdf.output(dest='S').encode('latin-1')
                st.download_button("İndirmeyi Başlat", data=out, file_name="rapor.pdf")
            except Exception as e:
                st.error(f"PDF kütüphanesi yüklenmemiş olabilir: {e}")
else:
    st.warning("⚠️ Kişisel cüzdanınızı görmek için lütfen sağ üstten giriş yapın.")