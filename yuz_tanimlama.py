import cv2
import numpy as np
import os
import pickle
from datetime import datetime

# Yüz tanıma eğitim verileri klasörü
YUZLER_KLASOR = "bilinen_yuzler"

# Tanınacak yüzlerin bilgileri
yuz_taniyici = cv2.face.LBPHFaceRecognizer_create()
yuz_tanimlari = {}  # {id: isim} şeklinde eşleşme
yuz_isimleri = []   # İsimlerin listesi
yuk_id = 0          # Yüz ID'leri

# OpenCV için yüz tespiti cascade sınıflandırıcısı
yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def klasor_kontrol():
    """Gerekli klasörlerin oluşturulmasını sağlar."""
    if not os.path.exists(YUZLER_KLASOR):
        os.makedirs(YUZLER_KLASOR)
        print(f"{YUZLER_KLASOR} klasörü oluşturuldu.")
    
    veri_klasor = os.path.join(YUZLER_KLASOR, "egitim_verileri")
    if not os.path.exists(veri_klasor):
        os.makedirs(veri_klasor)
        print(f"{veri_klasor} klasörü oluşturuldu.")
    
    return veri_klasor

def yuz_veri_yukle(veri_klasor):
    """Önceden kaydedilmiş yüz verilerini yükler."""
    global yuz_taniyici, yuz_tanimlari, yuz_isimleri, yuk_id
    
    # Tanımlayıcı model dosyası
    model_dosya = os.path.join(YUZLER_KLASOR, "taniyici_model.yml")
    tanimlar_dosya = os.path.join(YUZLER_KLASOR, "yuz_tanimlari.pkl")
    
    # Eğitim verileri ve tanımlamaları yükle
    if os.path.exists(model_dosya) and os.path.exists(tanimlar_dosya):
        yuz_taniyici.read(model_dosya)
        
        with open(tanimlar_dosya, 'rb') as f:
            veri = pickle.load(f)
            yuz_tanimlari = veri["tanimlar"]
            yuz_isimleri = veri["isimler"]
            yuk_id = veri["son_id"]
            
        print(f"Yüz verileri yüklendi: {len(yuz_isimleri)} kişi tanımlanmış.")
        return True
    else:
        print("Kaydedilmiş yüz verisi bulunamadı.")
        return False

def yuz_verileri_kaydet():
    """Yüz verilerini diske kaydeder."""
    model_dosya = os.path.join(YUZLER_KLASOR, "taniyici_model.yml")
    tanimlar_dosya = os.path.join(YUZLER_KLASOR, "yuz_tanimlari.pkl")
    
    # Eğitim verileri ve tanımlamaları kaydet
    yuz_taniyici.write(model_dosya)
    
    veri = {
        "tanimlar": yuz_tanimlari,
        "isimler": yuz_isimleri,
        "son_id": yuk_id
    }
    
    with open(tanimlar_dosya, 'wb') as f:
        pickle.dump(veri, f)
    
    print(f"Yüz verileri kaydedildi: {len(yuz_isimleri)} kişi.")

def yeni_yuz_ekle():
    """Kameradan veya dosyadan yeni yüz ekler."""
    global yuk_id, yuz_tanimlari, yuz_isimleri
    
    print("\n===== Yeni Yüz Ekleme =====")
    isim = input("Tanımlanacak kişinin adı: ")
    
    secim = input("Yöntem seçin:\n1) Kameradan\n2) Dosyadan\nSeçiminiz: ")
    
    egitim_resimleri = []
    if secim == "1":
        # Kameradan yüz ekle
        print("Kamera açılıyor... Çıkmak için 'q' tuşuna basın.")
        print("Yüzü kaydetmek için 'k' tuşuna basın.")
        
        cap = cv2.VideoCapture(0)
        sayac = 0
        max_ornek = 10
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Kamera erişim hatası!")
                break
                
            # Görüntüyü yeniden boyutlandırma
            frame = cv2.resize(frame, (640, 480))
            gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Yüzleri tespit et
            yuzler = yuz_cascade.detectMultiScale(
                gri, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            # Yüzleri çiz
            for (x, y, w, h) in yuzler:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Bilgi göster
            metin = f"Yakalanan: {sayac}/{max_ornek} - Kaydetmek için 'k' tuşuna basın"
            cv2.putText(frame, metin, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow("Yüz Ekleme", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('k') and len(yuzler) == 1:
                # Yüzü kaydet
                x, y, w, h = yuzler[0]
                yuz_resmi = gri[y:y+h, x:x+w]
                egitim_resimleri.append(yuz_resmi)
                sayac += 1
                print(f"Yüz örneği alındı: {sayac}/{max_ornek}")
                
                if sayac >= max_ornek:
                    break
        
        cap.release()
        cv2.destroyAllWindows()
    
    elif secim == "2":
        # Dosyadan yüz ekle
        dosya_yolu = input("Resim dosyasının yolunu girin: ")
        if not os.path.exists(dosya_yolu):
            print("Dosya bulunamadı!")
            return
        
        # Resmi yükle
        resim = cv2.imread(dosya_yolu)
        if resim is None:
            print("Resim yüklenemedi!")
            return
            
        # Yüzleri tespit et
        gri = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
        yuzler = yuz_cascade.detectMultiScale(
            gri, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        if len(yuzler) == 0:
            print("Resimde yüz tespit edilemedi!")
            return
        
        # İşaretli resmi göster
        for (x, y, w, h) in yuzler:
            cv2.rectangle(resim, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        cv2.imshow("Tespit Edilen Yüzler", resim)
        
        secilen_yuz = 0
        if len(yuzler) > 1:
            secilen_yuz = int(input(f"{len(yuzler)} yüz tespit edildi. Hangisini eklemek istersiniz (0-{len(yuzler)-1})? "))
            
        # Seçilen yüzü 10 örnek olarak ekle
        x, y, w, h = yuzler[secilen_yuz]
        yuz_resmi = gri[y:y+h, x:x+w]
        
        for _ in range(10):
            egitim_resimleri.append(yuz_resmi)
            
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    else:
        print("Geçersiz seçim!")
        return
    
    # Yeterli örnek alındıysa eğitim verisine ekle
    if len(egitim_resimleri) > 0:
        # Yeni ID atama
        yeni_id = yuk_id
        yuk_id += 1
        
        # Veri klasörüne kaydet
        veri_klasor = os.path.join(YUZLER_KLASOR, "egitim_verileri")
        for i, yuz_resmi in enumerate(egitim_resimleri):
            dosya = os.path.join(veri_klasor, f"{isim}_{yeni_id}_{i}.jpg")
            cv2.imwrite(dosya, yuz_resmi)
        
        # Tanımlama verilerini güncelle
        yuz_tanimlari[yeni_id] = isim
        yuz_isimleri.append(isim)
        
        # Tanımlayıcıyı eğit
        ids = []
        samples = []
        
        for klasor, alt_klasorler, dosyalar in os.walk(veri_klasor):
            for dosya in dosyalar:
                if dosya.endswith(".jpg") or dosya.endswith(".png"):
                    yol = os.path.join(klasor, dosya)
                    
                    # Dosya adından ID'yi çıkar
                    kisi_id = int(dosya.split("_")[1])
                    
                    # Resmi yükle
                    img = cv2.imread(yol, cv2.IMREAD_GRAYSCALE)
                    ids.append(kisi_id)
                    samples.append(img)
        
        # Tanımlayıcıyı eğit
        yuz_taniyici.train(samples, np.array(ids))
        
        # Verileri kaydet
        yuz_verileri_kaydet()
        
        print(f"\nYeni yüz başarıyla eklendi: {isim}")
    else:
        print("Yüz örnekleri alınamadı!")

def fotograf_yuz_tanima(dosya_yolu):
    """Belirtilen fotoğraftaki yüzleri tanımlar ve gösterir."""
    # Yüz verileri yüklenmiş mi kontrol et
    if len(yuz_isimleri) == 0:
        print("Tanımlanmış yüz verisi yok! Önce yüz ekleyin.")
        return
    
    # Dosyayı yükle
    if not os.path.exists(dosya_yolu):
        print("Dosya bulunamadı!")
        return
        
    resim = cv2.imread(dosya_yolu)
    if resim is None:
        print("Resim yüklenemedi!")
        return
    
    # Görüntüyü işle
    gri = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
    
    # Yüzleri tespit et
    yuzler = yuz_cascade.detectMultiScale(
        gri, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30)
    )
    
    if len(yuzler) == 0:
        print("Resimde yüz tespit edilemedi!")
        return
    
    # Tespit edilen her yüzü tanımla
    for (x, y, w, h) in yuzler:
        yuz_kesit = gri[y:y+h, x:x+w]
        
        # Tanıma işlemi
        id, guven = yuz_taniyici.predict(yuz_kesit)
        
        # Güven değeri düşükse (daha iyi eşleşme)
        if guven < 70:
            isim = yuz_tanimlari.get(id, "Bilinmeyen")
            guven_text = f"{int(100 - guven)}%"
        else:
            isim = "Bilinmeyen"
            guven_text = f"{int(100 - guven)}%"
        
        # Dikdörtgen ve isim göster
        renk = (0, 255, 0) if isim != "Bilinmeyen" else (0, 0, 255)
        cv2.rectangle(resim, (x, y), (x+w, y+h), renk, 2)
        
        # Metin için arka plan
        cv2.rectangle(resim, (x, y+h), (x+w, y+h+30), renk, cv2.FILLED)
        cv2.putText(resim, f"{isim} ({guven_text})", (x+2, y+h+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Sonucu göster
    cv2.imshow("Yüz Tanıma Sonucu", resim)
    
    # Kaydetmek istiyor musunuz?
    print("\nSonuç görüntüleniyor. Kaydetmek için 's' tuşuna basın, çıkmak için herhangi bir tuşa basın.")
    key = cv2.waitKey(0) & 0xFF
    
    if key == ord('s'):
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        sonuc_dosya = f"tanima_sonucu_{zaman}.jpg"
        cv2.imwrite(sonuc_dosya, resim)
        print(f"Sonuç kaydedildi: {sonuc_dosya}")
    
    cv2.destroyAllWindows()

def main():
    """Ana program."""
    print("\n===== Yüz Tanıma Sistemi =====")
    
    # Gerekli klasörleri kontrol et
    veri_klasor = klasor_kontrol()
    
    # Varsa yüz verilerini yükle
    yuz_veri_yukle(veri_klasor)
    
    while True:
        print("\nYapmak istediğiniz işlemi seçin:")
        print("1) Yeni yüz ekle")
        print("2) Fotoğraftan yüz tanıma")
        print("3) Çıkış")
        
        secim = input("\nSeçiminiz: ")
        
        if secim == "1":
            yeni_yuz_ekle()
        elif secim == "2":
            dosya_yolu = input("Tanımlanacak fotoğrafın dosya yolunu girin: ")
            fotograf_yuz_tanima(dosya_yolu)
        elif secim == "3":
            break
        else:
            print("Geçersiz seçim!")
    
    print("Program sonlandırıldı.")

if __name__ == "__main__":
    main() 