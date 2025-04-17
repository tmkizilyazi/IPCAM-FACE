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
    
    # Video bağlantı ayarları
    video_yakala = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    
    # RTSP bağlantı parametreleri
    video_yakala.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Tampon boyutunu azalt
    video_yakala.set(cv2.CAP_PROP_FPS, 15)  # FPS değerini azalt
    
    # Çözünürlüğü düşür (kameraya göre değişebilir)
    # video_yakala.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # video_yakala.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # RTSP için ek bağlantı parametreleri
    # Bazı RTSP hatalarını azaltmak için sürücüye özel parametreler
    # video_yakala.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
    
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
    
    # Video akışında oluşan hataları yönetmek için sayaç
    hata_sayaci = 0
    max_hata = 5
    
    try:
        while True:
            # Kameradan kare oku
            ret, frame = video_yakala.read()
            
            if not ret:
                hata_sayaci += 1
                print(f"Kare alınamadı. Tekrar deneniyor... ({hata_sayaci}/{max_hata})")
                
                # Belirli sayıda hatadan sonra bağlantıyı yenile
                if hata_sayaci >= max_hata:
                    print("Bağlantı yenileniyor...")
                    video_yakala.release()
                    time.sleep(2)
                    video_yakala = kamera_baglantisi_kur()
                    
                    if video_yakala is None:
                        print("Bağlantı yenilenirken hata oluştu. Program sonlandırılıyor.")
                        break
                    
                    hata_sayaci = 0
                
                time.sleep(1)
                continue
            
            # Hata sayacını sıfırla
            hata_sayaci = 0    
                
            # Yüz tanıma işlemi
            try:
                islenmiş_frame, yuz_sayisi = yuz_tanima(frame)
                
                # Yüz sayısını göster
                cv2.putText(islenmiş_frame, f"Tespit Edilen Yuz: {yuz_sayisi}", (10, 30), 
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
        print(f"Hata oluştu: {e}")
    
    finally:
        # Kaynakları serbest bırak
        video_yakala.release()
        cv2.destroyAllWindows()
        print("Program sonlandırıldı.")

if __name__ == "__main__":
    main() 