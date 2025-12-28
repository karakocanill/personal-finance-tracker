import os
import json
from datetime import datetime

# Verilerin saklanacağı modern JSON formatı
# Bu dosya, bakiye ve işlem geçmişini bir arada tutar.
DOSYA_ADI = "finans_verileri.json"


def verileri_yukle():
    """Dosyadan bakiye ve işlem geçmişini yükler."""
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            try:
                return json.load(dosya)
            except json.JSONDecodeError:
                pass
    # Dosya yoksa veya bozuksa başlangıç değerleri döndürülür
    return {"bakiye": 0.0, "gecmis": []}


def verileri_kaydet(veri):
    """Bakiye ve işlem geçmişini dosyaya düzenli bir şekilde kaydeder."""
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        # indent=4 verinin okunabilir (yakışıklı) görünmesini sağlar
        json.dump(veri, dosya, indent=4, ensure_ascii=False)


def menu():
    print("\n" + "=" * 45)
    print(" 💰 KİŞİSEL FİNANS VE İŞLEM TAKİBİ (v3.0)")
    print("=" * 45)
    print("1. Gelir Ekle")
    print("2. Gider Ekle")
    print("3. İşlem Geçmişini Gör")
    print("4. Güncel Bakiyeyi Sorgula")
    print("5. Çıkış")
    print("-" * 45)


def main():
    # Program başlarken verileri yüklüyoruz
    veri = verileri_yukle()

    while True:
        menu()
        secim = input("Yapmak istediğiniz işlemi seçin (1-5): ")

        if secim in ['1', '2']:
            islem_tipi = "Gelir" if secim == '1' else "Gider"
            try:
                miktar = float(input(f"{islem_tipi} miktarını girin: "))
                if miktar <= 0:
                    print("❗ Miktar sıfırdan büyük olmalıdır.")
                    continue

                aciklama = input("İşlem açıklaması (örn: Market, Maaş, Steam): ")
                # İşlemin yapıldığı anı kaydetmek için datetime kullanıyoruz
                tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Bakiyeyi güncelle
                if secim == '1':
                    veri["bakiye"] += miktar
                else:
                    veri["bakiye"] -= miktar

                # Yeni işlemi bir sözlük olarak geçmiş listesine ekle
                yeni_islem = {
                    "tarih": tarih,
                    "tip": islem_tipi,
                    "miktar": miktar,
                    "aciklama": aciklama
                }
                veri["gecmis"].append(yeni_islem)

                # Her işlemden sonra dosyaya kaydet
                verileri_kaydet(veri)
                print(f"✅ {islem_tipi} başarıyla kaydedildi.")

            except ValueError:
                print("❗ Hata: Lütfen geçerli bir sayı girin (Örn: 150.50).")

        elif secim == '3':
            print("\n--- 📋 İŞLEM GEÇMİŞİ ---")
            if not veri["gecmis"]:
                print("Henüz bir işlem kaydı bulunmuyor.")
            else:
                for islem in veri["gecmis"]:
                    sembol = "+" if islem["tip"] == "Gelir" else "-"
                    print(f"[{islem['tarih']}] {islem['tip']}: {sembol}{islem['miktar']} TL ({islem['aciklama']})")

        elif secim == '4':
            print(f"\n💵 GÜNCEL BAKİYENİZ: {veri['bakiye']:.2f} TL")

        elif secim == '5':
            print("👋 Verileriniz JSON formatında saklandı. İyi günler!")
            break
        else:
            print("❗ Geçersiz seçim, lütfen 1-5 arası bir rakam girin.")


if __name__ == "__main__":
    main()