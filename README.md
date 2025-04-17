# IP Kamera Yüz Tanıma Sistemi

Bu proje, IP kameralar üzerinden gerçek zamanlı yüz tanıma işlemi yapan bir sistemdir. Sistem, önceden tanıtılan kişilerin yüzlerini tanır, kamera görüş alanından geçtiğinde bildirim verir ve isteğe bağlı olarak bu görüntüleri kaydeder.

## Programlar

Sistem iki ana programdan oluşmaktadır:

1. **`yuz_tanimlama.py`**: Tanınması istenen kişilerin yüzlerini sisteme tanıtmak için kullanılır.
2. **`ip_kamera_yuz_tanima_canli.py`**: IP kamera üzerinden canlı yüz tanıma yapar.

## Kurulum

### Gereksinimler

```
pip install -r requirements.txt
```

requirements.txt dosyası aşağıdaki paketleri içermektedir:
- opencv-python
- opencv-contrib-python
- numpy
- imutils

### IP Kamera Ayarları

Varsayılan IP kamera ayarları:
- IP: 10.34.51.53
- Kullanıcı adı: admin
- Şifre: tps2018

Farklı bir kamera kullanıyorsanız, `ip_kamera_yuz_tanima_canli.py` dosyasındaki aşağıdaki satırları düzenleyin:

```python
ip_adresi = "10.34.51.53"
kullanici_adi = "admin"
sifre = "tps2018"
```

## Kullanım

### 1. Kişi Tanıtma

İlk olarak, tanımak istediğiniz kişileri sisteme tanıtın:

```
python yuz_tanimlama.py
```

- "1) Yeni yüz ekle" seçeneğini seçin
- Kişinin adını girin
- Kamera veya dosyadan yüz resimleri ekleyin
- Program, bu yüzleri kaydedecek ve tanıma modelini eğitecektir

### 2. Canlı Yüz Tanıma

Kişileri tanıttıktan sonra, canlı yüz tanıma programını çalıştırın:

```
python ip_kamera_yuz_tanima_canli.py
```

Program çalıştığında:
- IP kameraya bağlanır
- Kamera görüntüsündeki yüzleri tespit eder
- Tanınan kişileri yeşil çerçeve içinde gösterir
- Tanınmayan kişileri kırmızı çerçeve içinde "Bilinmeyen" olarak işaretler
- Konsola tanınan kişilerin bilgilerini yazdırır

## Özellikler

- Kameradan geçen tanıdık yüzleri gerçek zamanlı olarak tespit eder
- Yüzleri %70 ve üzeri benzerlik oranıyla tanır
- Tanınan kişilerin isimlerini ve benzerlik yüzdesini gösterir
- Tanınan kişilerin görüntülerini kaydetme seçeneği
- Güvenilir RTSP bağlantısı ve düşük gecikme
- Bağlantı sorunlarında otomatik yeniden bağlanma
- Farklı RTSP URL formatlarını deneme

## Detaylı Kullanım Kılavuzu

Daha detaylı kullanım bilgileri için `kullanim_klavuzu.md` dosyasına bakınız.

## Sorun Giderme

- Kamera bağlantı sorunu yaşıyorsanız IP, kullanıcı adı ve şifre bilgilerini kontrol edin
- Tanıma kalitesini artırmak için daha fazla ve farklı açılardan yüz örnekleri ekleyin
- H.264 kodek hataları için RTSP bağlantı parametrelerini ayarlayın

## Not

Bu sistem, genel güvenlik ve tanıma amaçlı kullanılmak üzere tasarlanmıştır. Kişisel verilerin gizliliği ve güvenliği göz önünde bulundurulmalıdır. 