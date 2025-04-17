import cv2
import numpy as np
import os
import pickle
import time
import imutils
import threading
from datetime import datetime

# IP Kamera Ayarları
ip_adresi = "10.34.51.53"
kullanici_adi = "admin"
sifre = "tps2018"
url = f"rtsp://{kullanici_adi}:{sifre}@{ip_adresi}/live"

# Yüz tanıma eğitim verileri klasörü
YUZLER_KLASOR = "bilinen_yuzler"

# Tanınacak yüzlerin bilgileri
yuz_taniyici = cv2.face.LBPHFaceRecognizer_create()
yuz_tanimlari = {}  # {id: isim} şeklinde eşleşme
yuz_isimleri = []   # İsimlerin listesi

# OpenCV için yüz tespiti cascade sınıflandırıcısı
yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Kayıt ayarları
kayit_yapilsin_mi = False
kayit_klasoru = "kayitlar"

# OpenCV için çeşitli RTSP protokol seçenekleri
def rtsp_secenekleri_uygula(cap):
    # FFMPEG tabanlı yakalama için kullanılır
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|analyzeduration;1000000|reorder_queue_size;10000|buffer_size;10000000|max_delay;500000"
    
    # Tampon boyutunu azalt, gecikmeli kare sayısını düşür
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  
    
    return cap

# Gelişmiş RTSP bağlantısı 
def gelismis_kamera_baglantisi_kur():
    print(f"Kameraya bağlanılıyor: {url}")
    
    # FFMPEG yakalama motorunu kullan
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap = rtsp_secenekleri_uygula(cap)
    
    # Bağlantı kontrolü
    if not cap.isOpened():
        print("Standart bağlantı başarısız, alternatif URL formatları deneniyor...")
        
        # Alternatif RTSP yolları
        alternatif_yollar = ["av_stream", "h264", "live/h264", "stream", "Streaming/Channels/1", "cam/realmonitor"]
        
        for yol in alternatif_yollar:
            alt_url = f"rtsp://{kullanici_adi}:{sifre}@{ip_adresi}/{yol}"
            print(f"Deneniyor: {alt_url}")
            
            cap = cv2.VideoCapture(alt_url, cv2.CAP_FFMPEG)
            cap = rtsp_secenekleri_uygula(cap)
            
            if cap.isOpened():
                print("Bağlantı başarılı!")
                return cap
                
        print("Tüm bağlantı denemeleri başarısız!")
        return None
    
    print("Kamera bağlantısı başarılı.")
    return cap

# Bir kare geçerli mi kontrolü
def kare_gecerli_mi(frame):
    if frame is None:
        return False
    h, w = frame.shape[:2]
    return h > 60 and w > 60  # Minimum boyut kontrolü

# Arka plan iş parçacığında kare okuma
class VideoOkuyucu:
    def __init__(self, video_yakala):
        self.video_yakala = video_yakala
        self.current_frame = None
        self.ret = False
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        
    def _update(self):
        while self.running:
            ret, frame = self.video_yakala.read()
            if ret and kare_gecerli_mi(frame):
                with self.lock:
                    self.current_frame = frame
                    self.ret = True
            time.sleep(0.01)  # CPU kullanımını düşürmek için kısa bekleme
    
    def read(self):
        with self.lock:
            return self.ret, self.current_frame.copy() if self.ret else None
            
    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

# Kayıt klasörünü kontrol et
def klasor_kontrol():
    # Yüz tanıma klasörleri
    if not os.path.exists(YUZLER_KLASOR):
        os.makedirs(YUZLER_KLASOR)
        print(f"{YUZLER_KLASOR} klasörü oluşturuldu.")
    
    veri_klasor = os.path.join(YUZLER_KLASOR, "egitim_verileri")
    if not os.path.exists(veri_klasor):
        os.makedirs(veri_klasor)
        print(f"{veri_klasor} klasörü oluşturuldu.")
    
    # Kayıt klasörü
    if not os.path.exists(kayit_klasoru):
        os.makedirs(kayit_klasoru)
        print(f"{kayit_klasoru} klasörü oluşturuldu.")
    
    return veri_klasor

# Yüz verilerini yükle
def yuz_veri_yukle():
    """Önceden kaydedilmiş yüz verilerini yükler."""
    global yuz_taniyici, yuz_tanimlari, yuz_isimleri
    
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
            
        print(f"Yüz verileri yüklendi: {len(yuz_isimleri)} kişi tanımlanmış.")
        return True
    else:
        print("Kaydedilmiş yüz verisi bulunamadı.")
        print("Lütfen önce 'yuz_tanimlama.py' programı ile tanıtmak istediğiniz kişileri ekleyin.")
        return False

# Yüz tanıma işlemi
def yuz_tanima_yap(frame):
    """Verilen karede yüz tespiti ve tanıma yapar."""
    if frame is None:
        return None, []
        
    # Performans için kareyi yeniden boyutlandır
    frame = imutils.resize(frame, width=640)
    
    # Gri tonlamaya dönüştür
    gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Yüzleri tespit et
    yuzler = yuz_cascade.detectMultiScale(
        gri,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Tanınan kişilerin listesi
    taninan_kisiler = []
    
    # Tespit edilen her yüzü tanımla
    for (x, y, w, h) in yuzler:
        yuz_kesit = gri[y:y+h, x:x+w]
        
        # Tanıma işlemi
        id, guven = yuz_taniyici.predict(yuz_kesit)
        
        # Güven değeri düşükse (daha iyi eşleşme)
        if guven < 70:
            isim = yuz_tanimlari.get(id, "Bilinmeyen")
            guven_text = f"{int(100 - guven)}%"
            renk = (0, 255, 0)  # Yeşil
            taninan_kisiler.append(isim)
        else:
            isim = "Bilinmeyen"
            guven_text = f"{int(100 - guven)}%"
            renk = (0, 0, 255)  # Kırmızı
        
        # Dikdörtgen ve isim göster
        cv2.rectangle(frame, (x, y), (x+w, y+h), renk, 2)
        
        # Metin için arka plan
        cv2.rectangle(frame, (x, y+h), (x+w, y+h+30), renk, cv2.FILLED)
        cv2.putText(frame, f"{isim} ({guven_text})", (x+2, y+h+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return frame, taninan_kisiler

# Kare kaydetme fonksiyonu
def kareyi_kaydet(frame, isimler):
    """Tanınan kişi olduğunda kareyi kaydeder."""
    if not kayit_yapilsin_mi or len(isimler) == 0:
        return
        
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    isim_liste = "_".join(isimler)
    dosya_adi = os.path.join(kayit_klasoru, f"{isim_liste}_{zaman}.jpg")
    cv2.imwrite(dosya_adi, frame)
    print(f"Tanınan kişi(ler) kaydedildi: {isim_liste} -> {dosya_adi}")

def main():
    """Ana program."""
    print("\n===== IP Kamera Üzerinden Yüz Tanıma Sistemi =====")
    
    global kayit_yapilsin_mi
    
    # Klasör kontrolü
    klasor_kontrol()
    
    # Yüz verilerini yükle
    if not yuz_veri_yukle():
        input("Program sonlandırılıyor. Devam etmek için Enter tuşuna basın...")
        return
        
    # Kayıt ayarları
    kayit_secim = input("Tanınan kişilerin görüntülerini kaydetmek ister misiniz? (e/h): ")
    kayit_yapilsin_mi = kayit_secim.lower() == 'e'
    
    # Kamera bağlantısını başlat
    video_yakala = gelismis_kamera_baglantisi_kur()
    
    if video_yakala is None:
        print("Kamera bağlantısı başarısız. Program sonlandırılıyor.")
        return
    
    # Arka plan kare okuyucuyu başlat (düşük gecikme için)
    okuyucu = VideoOkuyucu(video_yakala)
    
    # Video akışında oluşan hataları yönetmek için sayaç
    hata_sayaci = 0
    max_hata = 10
    
    # Son tanınan kişiler ve zaman
    son_taninan = set()
    son_tanima_zamani = time.time()
    
    print("\nYüz tanıma başlatıldı. Çıkmak için 'q' tuşuna basın.")
    print("Tanınan kişiler ekranda yeşil çerçeve ile gösterilecektir.")
    
    try:
        while True:
            # Arka plan iş parçacığından kare oku
            ret, frame = okuyucu.read()
            
            if not ret:
                hata_sayaci += 1
                print(f"Kare alınamadı. Tekrar deneniyor... ({hata_sayaci}/{max_hata})")
                
                # Belirli sayıda hatadan sonra bağlantıyı yenile
                if hata_sayaci >= max_hata:
                    print("Bağlantı yenileniyor...")
                    okuyucu.stop()
                    video_yakala.release()
                    time.sleep(2)
                    video_yakala = gelismis_kamera_baglantisi_kur()
                    
                    if video_yakala is None:
                        print("Bağlantı yenilenirken hata oluştu. Program sonlandırılıyor.")
                        break
                    
                    okuyucu = VideoOkuyucu(video_yakala)
                    hata_sayaci = 0
                
                time.sleep(0.5)
                continue
            
            # Hata sayacını sıfırla
            hata_sayaci = 0    
                
            # Yüz tanıma işlemi
            try:
                islenmiş_frame, taninan_kisiler = yuz_tanima_yap(frame)
                
                # Tanınan kişiler değiştiyse veya belirli süre geçtiyse bildirim yap
                suanki_taninan = set(taninan_kisiler)
                suanki_zaman = time.time()
                
                if (suanki_taninan != son_taninan) or (suanki_zaman - son_tanima_zamani > 10):
                    if len(suanki_taninan) > 0:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Tanınan kişiler: {', '.join(suanki_taninan)}")
                        # Kareyi kaydet
                        kareyi_kaydet(islenmiş_frame, taninan_kisiler)
                        
                    son_taninan = suanki_taninan
                    son_tanima_zamani = suanki_zaman
                
                # Zaman damgası ekle
                tarih_saat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(islenmiş_frame, tarih_saat, (10, islenmiş_frame.shape[0] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Yüz sayısını göster
                cv2.putText(islenmiş_frame, f"Tespit Edilen Yuz: {len(taninan_kisiler)}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Görüntüyü göster
                cv2.imshow("IP Kamera Yuz Tanima", islenmiş_frame)
            except Exception as e:
                print(f"Kare işlenirken hata: {e}")
                continue
            
            # 'q' tuşuna basılırsa döngüden çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Genel hata oluştu: {e}")
    
    finally:
        # Kaynakları serbest bırak
        if 'okuyucu' in locals():
            okuyucu.stop()
        
        if 'video_yakala' in locals() and video_yakala is not None:
            video_yakala.release()
            
        cv2.destroyAllWindows()
        print("Program sonlandırıldı.")

if __name__ == "__main__":
    main() 