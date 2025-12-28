import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF

# Dosya adı
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


def doviz_altin_verilerini_al():
    """Canlı Döviz ve Kıymetli Maden verilerini çeker."""
    try:
        # Ücretsiz ve anahtarsız bir API (ExchangeRate-API)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()

        usd_try = data["rates"]["TRY"]
        eur_try = usd_try / data["rates"]["EUR"]

        # Altın ve Gümüş için yaklaşık global ons fiyatları üzerinden TL hesabı (Basit model)
        # Not: Gerçek piyasada bu değerler bankadan bankaya değişir.
        ons_altin_usd = 2050.0  # Örnek sabit ons fiyatı, API'den de çekilebilir
        ons_gumus_usd = 23.5

        gram_altin_try = (ons_altin_usd / 31.1035) * usd_try
        gram_gumus_try = (ons_gumus_usd / 31.1035) * usd_try

        return {
            "USD": usd_try,
            "EUR": eur_try,
            "ALTIN": gram_altin_try,
            "GUMUS": gram_gumus_try
        }
    except:
        return {"USD": 0.0, "EUR": 0.0, "ALTIN": 0.0, "GUMUS": 0.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro Max", page_icon="💎", layout="wide")

if 'veri' not in st.session_state:
    st.session_state.veri = verileri_yukle()

# --- SIDEBAR: PİYASA TAKİP VE GİRİŞ ---
st.sidebar.title("📊 Piyasa Takip")
piyasa = doviz_altin_verilerini_al()

col_p1, col_p2 = st.sidebar.columns(2)
col_p1.metric("🇺🇸 USD", f"{piyasa['USD']:.2f} ₺")
col_p1.metric("🟡 Altın/gr", f"{piyasa['ALTIN']:.0f} ₺")
col_p2.metric("🇪🇺 EUR", f"{piyasa['EUR']:.2f} ₺")
col_p2.metric("⚪ Gümüş/gr", f"{piyasa['GUMUS']:.2f} ₺")

st.sidebar.write("---")
st.sidebar.header("📥 Yeni İşlem")
with st.sidebar.form("pro_form", clear_on_submit=True):
    tip = st.selectbox("Tür", ["Gelir", "Gider"])
    miktar = st.number_input("Miktar (TL)", min_value=0.0)
    kat = st.selectbox("Kategori", ["Eğitim", "Gıda", "Oyun/Hobi", "Ulaşım", "Maaş", "Yatırım", "Diğer"])
    aciklama = st.text_input("Açıklama")
    kaydet = st.form_submit_button("Sisteme İşle")

if kaydet and miktar > 0:
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if tip == "Gelir":
        st.session_state.veri["bakiye"] += miktar
    else:
        st.session_state.veri["bakiye"] -= miktar

    st.session_state.veri["gecmis"].append({
        "tarih": tarih, "tip": tip, "miktar": miktar, "kategori": kat, "aciklama": aciklama
    })
    verileri_kaydet(st.session_state.veri)
    st.rerun()

# --- ANA PANEL ---
st.title("🚀 Finansal Analiz Dashboard")
st.write(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")

# Metrikler
m1, m2, m3 = st.columns(3)
bakiye = st.session_state.veri['bakiye']
m1.metric("💵 Toplam Bakiye", f"{bakiye:.2f} TL")
m2.metric("💰 USD Değeri", f"${(bakiye / piyasa['USD']):.2f}" if piyasa['USD'] > 0 else "0.00")
m3.metric("📊 İşlem Sayısı", len(st.session_state.veri["gecmis"]))

tab1, tab2, tab3 = st.tabs(["📋 İşlem Kayıtları", "📊 Görsel Analiz", "📄 Raporlama"])

with tab1:
    if st.session_state.veri["gecmis"]:
        df = pd.DataFrame(st.session_state.veri["gecmis"])
        st.dataframe(df.sort_values("tarih", ascending=False), use_container_width=True)
    else:
        st.info("Kayıt bulunamadı.")

with tab2:
    if st.session_state.veri["gecmis"]:
        df = pd.DataFrame(st.session_state.veri["gecmis"])
        c1, c2 = st.columns(2)
        c1.write("### Harcama Dağılımı")
        c1.bar_chart(df[df["tip"] == "Gider"].groupby("kategori")["miktar"].sum())
        c2.write("### İşlem Trendi")
        c2.line_chart(df.set_index("tarih")["miktar"])

with tab3:
    st.header("📄 PDF Rapor")
    if st.button("Raporu Hazırla"):
        # Not: Türkçe karakter sorunu olmaması için basit PDF yapısı
        st.success("PDF Raporu hazırlandı. (Simüle edildi)")
        # Burada pdf_cikti kodları devam edebilir