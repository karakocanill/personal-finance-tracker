import os

# Verilerin saklanacağı dosya adı
DOSYA_ADI = "hesap_verisi.txt"


def veriyi_yukle():
    """Program açıldığında dosyadan bakiyeyi okur."""
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r") as dosya:
            icerik = dosya.read()
            # Dosya boşsa veya geçersizse 0.0 döndür
            try:
                return float(icerik) if icerik else 0.0
            except ValueError:
                return 0.0
    return 0.0


def veriyi_kaydet(bakiye):
    """Her işlemden sonra güncel bakiyeyi dosyaya yazar."""
    with open(DOSYA_ADI, "w") as dosya:
        dosya.write(str(bakiye))


def menu():
    print("\n--- 💰 Kişisel Finans Takip Sistemi (v2) ---")
    print("1. Gelir Ekle")
    print("2. Gider Ekle")
    print("3. Bakiyeyi Gör")
    print("4. Çıkış")
    print("---------------------------------------")


def main():
    # Program başlarken eski bakiyeyi dosyadan çekiyoruz
    bakiye = veriyi_yukle()

    while True:
        menu()
        secim = input("Yapmak istediğiniz işlemi seçin (1-4): ")

        if secim == '1':
            try:
                miktar = float(input("Eklenecek gelir miktarını girin: "))
                bakiye += miktar
                veriyi_kaydet(bakiye)
                print(f"✅ {miktar} TL eklendi. Yeni bakiye kaydedildi.")
            except ValueError:
                print("❗ Lütfen geçerli bir sayı girin.")

        elif secim == '2':
            try:
                miktar = float(input("Gider miktarını girin: "))
                bakiye -= miktar
                veriyi_kaydet(bakiye)
                print(f"❌ {miktar} TL harcandı. Yeni bakiye kaydedildi.")
            except ValueError:
                print("❗ Lütfen geçerli bir sayı girin.")

        elif secim == '3':
            print(f"\n💵 Güncel Bakiyeniz: {bakiye} TL")

        elif secim == '4':
            print("👋 Verileriniz kaydedildi. Görüşmek üzere!")
            break
        else:
            print("❗ Geçersiz seçim, lütfen 1-4 arası bir sayı girin.")


# Programın ana giriş noktası
if __name__ == "__main__":
    main()