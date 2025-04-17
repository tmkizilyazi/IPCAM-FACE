import cv2
import numpy as np
import time
import imutils
import os
import threading

# IP Kamera URL'si
ip_adresi = "10.34.51.53"
kullanici_adi = "admin"
sifre = "tps2018"

# RTSP URL formatı (kullanıcı adı ve şifre ile)
url = f"rtsp://{kullanici_adi}:{sifre}@{ip_adresi}/live"

# Yüz tanıma için cascade sınıflandırıcısını yükle
yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Alternatif RTSP URL oluşturma fonksiyonu
def rtsp_url_olustur(ip, kullanici="admin", sifre="tps2018", port=554, yol="live"):
    return f"rtsp://{kullanici}:{sifre}@{ip}:{port}/{yol}"

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
            alt_url = rtsp_url_olustur(ip_adresi, kullanici_adi, sifre, yol=yol)
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

# Yüz tanıma işlemi
def yuz_tanima_yap(frame):
    """Verilen karede yüz tespiti yapar."""
    if frame is None:
        return None, 0
        
    # Performans için kareyi yeniden boyutlandır
    frame = imutils.resize(frame, width=640)
    
    # Gri tonlamaya dönüştür
    gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Yüzleri tespit et
    yuzler = yuz_cascade.detectMultiScale(
        gri,
        scaleFactor=1.2,
        minNeighbors=4,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Tespit edilen yüzler için dikdörtgen çiz
    for (x, y, w, h) in yuzler:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
    return frame, len(yuzler)

def main():
    """Ana program fonksiyonu."""
    # Kamera bağlantısını başlat
    video_yakala = gelismis_kamera_baglantisi_kur()
    
    if video_yakala is None:
        print("Program sonlandırıldı.")
        return
    
    # Arka plan kare okuyucuyu başlat (düşük gecikme için)
    okuyucu = VideoOkuyucu(video_yakala)
    
    # Video akışında oluşan hataları yönetmek için sayaç
    hata_sayaci = 0
    max_hata = 10
    son_yuz_sayisi = 0
    
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
                islenmiş_frame, yuz_sayisi = yuz_tanima_yap(frame)
                
                # Yüz tespit edildi mi kontrolü
                if yuz_sayisi > 0:
                    son_yuz_sayisi = yuz_sayisi
                
                # Zaman damgası ekle
                tarih_saat = time.strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(islenmiş_frame, tarih_saat, (10, islenmiş_frame.shape[0] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Yüz sayısını göster
                cv2.putText(islenmiş_frame, f"Tespit Edilen Yuz: {yuz_sayisi}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Görüntüyü göster
                cv2.imshow("IP Kamera Yuz Tanima (Dusuk Gecikme)", islenmiş_frame)
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