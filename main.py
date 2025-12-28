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


def doviz_kuru_al():
    """Canlı döviz kuru çeker (Ücretsiz API)."""
    try:
        # Örnek bir ücretsiz API (Key gerektirmeyen basit bir yapı)
        url = "https://api.exchangerate-api.com/v4/latest/TRY"
        response = requests.get(url)
        data = response.json()
        return {
            "USD": 1 / data["rates"]["USD"],
            "EUR": 1 / data["rates"]["EUR"]
        }
    except:
        return {"USD": 0.0, "EUR": 0.0}


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro Max", page_icon="💎", layout="wide")

if 'veri' not in st.session_state:
    st.session_state.veri = verileri_yukle()

# --- SIDEBAR: İŞLEM VE DÖVİZ ---
st.sidebar.header("📥 İşlem Merkezi")
with st.sidebar.form("pro_form", clear_on_submit=True):
    tip = st.selectbox("İşlem Türü", ["Gelir", "Gider"])
    miktar = st.number_input("Miktar (TL)", min_value=0.0, format="%.2f")
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

# Canlı Döviz Bilgisi
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Canlı Döviz Kurları")
kurlar = doviz_kuru_al()
st.sidebar.write(f"🇺🇸 USD/TRY: **{kurlar['USD']:.2f}**")
st.sidebar.write(f"🇪🇺 EUR/TRY: **{kurlar['EUR']:.2f}**")

# --- ANA PANEL ---
st.title("📈 Profesyonel Finans Yönetimi v7.0")

# Üst Metrikler
m1, m2, m3, m4 = st.columns(4)
bakiye = st.session_state.veri['bakiye']
m1.metric("💵 Toplam Bakiye", f"{bakiye:.2f} TL")
m2.metric("🇺🇸 Dolar Karşılığı", f"${(bakiye / kurlar['USD']):.2f}" if kurlar['USD'] > 0 else "0.00")
m3.metric("📊 İşlem Sayısı", len(st.session_state.veri["gecmis"]))
m4.metric("📅 Tarih", datetime.now().strftime("%d.%m.%Y"))

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
        col_l, col_r = st.columns(2)
        with col_l:
            st.write("### Harcama Dağılımı")
            st.bar_chart(df[df["tip"] == "Gider"].groupby("kategori")["miktar"].sum())
        with col_r:
            st.write("### İşlem Trendi")
            st.line_chart(df.set_index("tarih")["miktar"])

with tab3:
    st.header("📄 PDF Rapor Oluştur")
    if st.button("Finansal Özeti PDF Olarak Hazırla"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="Kisisel Finans Raporu", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Tarih: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Toplam Bakiye: {bakiye:.2f} TL", ln=True, align='L')

        # PDF dosyasını kaydet ve indirilebilir yap
        pdf_cikti = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 PDF Raporu İndir",
                           data=pdf_cikti,
                           file_name="finans_raporu.pdf",
                           mime="application/pdf")