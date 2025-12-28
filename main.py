import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

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


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finance Pro", page_icon="💎", layout="wide")

# Veriyi Başlat
if 'veri' not in st.session_state:
    st.session_state.veri = verileri_yukle()

# --- SIDEBAR: VERİ GİRİŞİ ---
st.sidebar.header("📥 İşlem Merkezi")
with st.sidebar.form("pro_form", clear_on_submit=True):
    tip = st.selectbox("İşlem Türü", ["Gelir", "Gider"])
    miktar = st.number_input("Miktar (TL)", min_value=0.0, format="%.2f")
    kat = st.selectbox("Kategori", ["Eğitim", "Gıda", "Oyun/Hobi", "Ulaşım", "Maaş", "Yatırım", "Diğer"])
    aciklama = st.text_input("Açıklama", placeholder="İşlem detayı...")
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
    st.toast(f"{tip} başarıyla kaydedildi!", icon='🚀')
    st.rerun()

# --- ANA PANEL ---
st.title("📈 Finansal Dashboard v6.0")
st.write(f"Hoş geldin Anıl! İşte finansal durumunun özeti:")

# Metrikler
m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Toplam Bakiye", f"{st.session_state.veri['bakiye']:.2f} TL")
m2.metric("📊 İşlem Sayısı", len(st.session_state.veri["gecmis"]))

# Basit bir analiz: En çok harcanan kategori
if st.session_state.veri["gecmis"]:
    df = pd.DataFrame(st.session_state.veri["gecmis"])
    giderler = df[df["tip"] == "Gider"]
    if not giderler.empty:
        en_cok_kat = giderler.groupby("kategori")["miktar"].sum().idxmax()
        m3.metric("⚠️ En Yüksek Gider", en_cok_kat)
        m4.metric("📈 Ortalama İşlem", f"{df['miktar'].mean():.2f} TL")

tab1, tab2, tab3 = st.tabs(["📋 İşlem Kayıtları", "📊 Görsel Analiz", "⚙️ Veri Yönetimi"])

with tab1:
    if st.session_state.veri["gecmis"]:
        df = pd.DataFrame(st.session_state.veri["gecmis"])
        # Filtreleme seçeneği
        filtre = st.multiselect("Kategoriye Göre Filtrele", df["kategori"].unique())
        if filtre:
            df = df[df["kcategory"].isin(filtre)]
        st.dataframe(df.sort_values("tarih", ascending=False), use_container_width=True)
    else:
        st.info("Kayıt bulunamadı.")

with tab2:
    if st.session_state.veri["gecmis"]:
        df = pd.DataFrame(st.session_state.veri["gecmis"])
        c_left, c_right = st.columns(2)
        with c_left:
            st.write("### Harcama Dağılımı")
            st.bar_chart(df[df["tip"] == "Gider"].groupby("kategori")["miktar"].sum())
        with c_right:
            st.write("### Gelir/Gider Dengesi")
            st.pie_chart = st.area_chart(df.groupby("tip")["miktar"].sum())

with tab3:
    st.write("### Veri Yedekleme")
    st.download_button("Verileri JSON Olarak İndir",
                       data=json.dumps(st.session_state.veri, indent=4),
                       file_name="finans_yedek.json",
                       mime="application/json")
    if st.button("🔴 Tüm Verileri Sıfırla"):
        if st.checkbox("Evet, tüm verilerimi silmek istiyorum"):
            st.session_state.veri = {"bakiye": 0.0, "gecmis": []}
            verileri_kaydet(st.session_state.veri)
            st.rerun()