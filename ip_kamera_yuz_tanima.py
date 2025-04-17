import cv2
import numpy as np
import time
import imutils

# IP Kamera URL'si
ip_adresi = "10.34.51.53"

# Kullanıcı adı ve şifre için yapılandırma
kullanici_adi = "admin"  # Varsayılan kullanıcı adı, değiştirebilirsiniz
sifre = "tps2018"         # Varsayılan şifre, değiştirebilirsiniz

# RTSP URL formatı (kullanıcı adı ve şifre ile)
url = f"rtsp://{kullanici_adi}:{sifre}@{ip_adresi}/live"

# Alternatif URL formatları:
# url = f"http://{kullanici_adi}:{sifre}@{ip_adresi}/video"
# url = f"rtsp://{ip_adresi}/live"  # Kimlik doğrulaması olmadan

# Yüz tanıma için cascade sınıflandırıcısını yükle
yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def kamera_baglantisi_kur():
    """IP kameraya bağlanır ve video akışını başlatır."""
    print(f"Kameraya bağlanılıyor: {url}")
    video_yakala = cv2.VideoCapture(url)
    
    # Bağlantı kontrolü
    if not video_yakala.isOpened():
        print("Kamera bağlantısı başarısız!")
        return None
    
    print("Kamera bağlantısı başarılı.")
    return video_yakala

def yuz_tanima(frame):
    """Verilen karede yüz tespiti yapar."""
    # Performans için kareyi yeniden boyutlandır
    frame = imutils.resize(frame, width=800)
    
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
    
    # Tespit edilen yüzler için dikdörtgen çiz
    for (x, y, w, h) in yuzler:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
    return frame, len(yuzler)

def main():
    """Ana program fonksiyonu."""
    # Kamera bağlantısını başlat
    video_yakala = kamera_baglantisi_kur()
    
    if video_yakala is None:
        print("Program sonlandırıldı.")
        return
    
    try:
        while True:
            # Kameradan kare oku
            ret, frame = video_yakala.read()
            
            if not ret:
                print("Kare alınamadı. Tekrar deneniyor...")
                time.sleep(1)
                continue
                
            # Yüz tanıma işlemi
            islenmiş_frame, yuz_sayisi = yuz_tanima(frame)
            
            # Yüz sayısını göster
            cv2.putText(islenmiş_frame, f"Tespit Edilen Yuz: {yuz_sayisi}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Görüntüyü göster
            cv2.imshow("IP Kamera Yuz Tanima", islenmiş_frame)
            
            # 'q' tuşuna basılırsa döngüden çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Hata oluştu: {e}")
    
    finally:
        # Kaynakları serbest bırak
        video_yakala.release()
        cv2.destroyAllWindows()
        print("Program sonlandırıldı.")

if __name__ == "__main__":
    main() 