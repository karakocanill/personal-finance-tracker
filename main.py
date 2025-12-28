import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Dosya adı
DOSYA_ADI = "finans_verileri.json"


def verileri_yukle():
    """Dosyadan verileri güvenli bir şekilde yükler."""
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                content = dosya.read()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, IOError):
            pass
    return {"bakiye": 0.0, "gecmis": []}


def verileri_kaydet(veri):
    """Verileri JSON dosyasına kaydeder."""
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(veri, dosya, indent=4, ensure_ascii=False)


# --- WEB ARAYÜZÜ AYARLARI ---
st.set_page_config(page_title="Anıl Finans Takip", page_icon="💰", layout="wide")

st.title("💰 Kişisel Finans Takip Sistemi (Web v4.0)")
st.markdown("Üsküdar Üniversitesi - Bilgisayar Mühendisliği Öğrenci Projesi")
st.write("---")

veri = verileri_yukle()

# --- SIDEBAR: YENİ İŞLEM EKLEME ---
st.sidebar.header("📥 Yeni İşlem Kaydı")
with st.sidebar.form("ekleme_formu", clear_on_submit=True):
    tip = st.selectbox("İşlem Türü", ["Gelir", "Gider"])
    miktar = st.number_input("Miktar (TL)", min_value=0.0, step=1.0)
    aciklama = st.text_input("Açıklama", placeholder="Örn: Market, Maaş, Steam")
    kaydet_butonu = st.form_submit_button("Sisteme Kaydet")

if kaydet_butonu:
    if miktar > 0 and aciklama:
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if tip == "Gelir":
            veri["bakiye"] += miktar
        else:
            veri["bakiye"] -= miktar

        veri["gecmis"].append({
            "tarih": tarih,
            "tip": tip,
            "miktar": miktar,
            "aciklama": aciklama
        })
        verileri_kaydet(veri)
        st.sidebar.success("İşlem kaydedildi!")
        st.rerun()
    else:
        st.sidebar.warning("Lütfen miktar ve açıklama girin.")

# --- ANA PANEL: ANALİZ VE ÖZET ---
col1, col2 = st.columns(2)
col1.metric("💵 Güncel Bakiyeniz", f"{veri['bakiye']:.2f} TL")
col2.metric("📊 Toplam İşlem Sayısı", len(veri["gecmis"]))

st.write("### 📋 İşlem Geçmişi ve Analiz")
tab1, tab2 = st.tabs(["İşlem Listesi", "Görsel Grafikler"])

with tab1:
    if veri["gecmis"]:
        df = pd.DataFrame(veri["gecmis"])
        # En yeni işlemi en üstte göster
        st.dataframe(df.sort_values(by="tarih", ascending=False), use_container_width=True)
    else:
        st.info("Henüz bir işlem kaydı yok.")

with tab2:
    if veri["gecmis"]:
        df = pd.DataFrame(veri["gecmis"])
        st.subheader("Harcama/Gelir Grafiği")
        st.bar_chart(data=df, x="aciklama", y="miktar")
    else:
        st.info("Grafik oluşturmak için önce veri ekleyin.")

# Alt Bilgi
st.markdown("---")
st.caption(f"Veriler '{DOSYA_ADI}' dosyasında saklanmaktadır.")