import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Dosya adı
DOSYA_ADI = "finans_verileri.json"


def verileri_yukle():
    """Dosyadan verileri okur, dosya yoksa boş yapı döndürür."""
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                return json.load(dosya)
        except:
            pass
    return {"bakiye": 0.0, "gecmis": []}


def verileri_kaydet(veri):
    """Verileri JSON dosyasına kalıcı olarak yazar."""
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(veri, dosya, indent=4, ensure_ascii=False)


# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Anıl Finans Paneli", page_icon="📈", layout="wide")

# Başlık ve Açıklama
st.title("💰 Kişisel Finans ve Analiz Sistemi")
st.markdown(f"**Geliştirici:** Anıl | **Üniversite:** Üsküdar Üniversitesi Bilgisayar Mühendisliği")
st.write("---")

# Veriyi Başlat (Oturum bazlı yönetim)
if 'veri' not in st.session_state:
    st.session_state.veri = verileri_yukle()

# --- SIDEBAR: VERİ GİRİŞİ ---
st.sidebar.header("📥 Yeni İşlem Ekle")
with st.sidebar.form("islem_formu", clear_on_submit=True):
    tip = st.selectbox("İşlem Türü", ["Gelir", "Gider"])
    miktar = st.number_input("Miktar (TL)", min_value=0.0, step=1.0)
    kategori = st.selectbox("Kategori", ["Eğitim", "Gıda", "Oyun/Hobi", "Ulaşım", "Maaş", "Diğer"])
    aciklama = st.text_input("Açıklama", placeholder="Örn: Market harcaması")
    kaydet = st.form_submit_button("Sisteme İşle")

if kaydet:
    if miktar > 0 and aciklama:
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if tip == "Gelir":
            st.session_state.veri["bakiye"] += miktar
        else:
            st.session_state.veri["bakiye"] -= miktar

        st.session_state.veri["gecmis"].append({
            "tarih": tarih,
            "tip": tip,
            "miktar": miktar,
            "kategori": kategori,
            "aciklama": aciklama
        })
        # Hem dosyaya hem oturuma kaydet
        verileri_kaydet(st.session_state.veri)
        st.toast("İşlem başarıyla kaydedildi!", icon='✅')
        st.rerun()

# --- ANA PANEL: ÖZET VE GRAFİKLER ---
col1, col2, col3 = st.columns(3)
col1.metric("💵 Mevcut Bakiye", f"{st.session_state.veri['bakiye']:.2f} TL")
col2.metric("📊 Toplam İşlem", len(st.session_state.veri["gecmis"]))
col3.metric("💻 Durum", "Çevrimiçi / Yayında")

tab1, tab2 = st.tabs(["📋 İşlem Geçmişi", "📈 Görsel Analiz"])

with tab1:
    if st.session_state.veri["gecmis"]:
        df = pd.DataFrame(st.session_state.veri["gecmis"])
        st.dataframe(df.sort_values(by="tarih", ascending=False), use_container_width=True)
    else:
        st.info("Henüz bir işlem kaydı bulunmuyor. Sol taraftan ekleme yapabilirsiniz.")

with tab2:
    if st.session_state.veri["gecmis"]:
        df = pd.DataFrame(st.session_state.veri["gecmis"])
        st.write("### Harcama Kategorileri Dağılımı")
        st.bar_chart(df.groupby("kategori")["miktar"].sum())
        st.write("### Harcama Zaman Çizelgesi")
        st.line_chart(df.set_index("tarih")["miktar"])