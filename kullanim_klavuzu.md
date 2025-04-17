# IP Kamera Canlı Kişi Tanıma Sistemi - Kullanım Kılavuzu

## Sistem Hakkında

Bu sistem IP kamera üzerinden gerçek zamanlı olarak yüz tanıma işlemi gerçekleştirir. Önceden tanıtılmış kişilerin kamera görüş alanına girmesi durumunda onları tespit ederek isimlerini gösterir ve isteğe bağlı olarak bu görüntüleri kaydeder.

## Program Akışı

1. Öncelikle tanınmasını istediğiniz kişilerin yüzlerini sisteme tanıtın (`yuz_tanimlama.py`)
2. Ardından IP kamera üzerinden canlı kişi tanıma programını çalıştırın (`ip_kamera_yuz_tanima_canli.py`)
3. Sistem, kameradan geçen tanıdığı kişileri otomatik olarak tespit edecek ve rapor edecektir

## Kullanım Adımları

### 1. Kişileri Sisteme Tanıtma

Programı ilk kez kullanıyorsanız, tanınması gereken kişileri önce sisteme tanıtmalısınız:

```
python yuz_tanimlama.py
```

Açılan programda:
- "1) Yeni yüz ekle" seçeneğini seçin
- Kişinin adını girin
- Kameradan veya dosyadan yüz resmi ekleyin
- Birden fazla kişi eklemek için bu işlemi tekrarlayın

### 2. Canlı Kişi Tanıma Programını Çalıştırma

Kişiler sisteme tanıtıldıktan sonra canlı tanıma programını çalıştırın:

```
python ip_kamera_yuz_tanima_canli.py
```

Program otomatik olarak:
- IP kameranıza bağlanacak
- Kameradaki görüntüde yüzleri tespit edecek
- Tanınan kişilerin isimlerini yeşil çerçeve içinde gösterecek
- Tanınmayan kişileri kırmızı çerçeve içinde "Bilinmeyen" olarak işaretleyecek
- Tanınan kişiler ekranda belirdiğinde bunu konsola yazacak
- İsteğe bağlı olarak bu görüntüleri kaydedecek

### 3. Tanınan Kişi Görüntülerini Kaydetme

Program başlatıldığında size tanınan kişilerin görüntülerini kaydetmek isteyip istemediğiniz sorulacaktır. 
- "e" yanıtı verirseniz, sistem tanıdığı kişilerin görüntülerini "kayitlar" klasörüne kaydedecektir
- Her kayıt, tanınan kişilerin isimleri ve tarih/saat bilgisiyle isimlendirilir

## Önemli Noktalar

1. Program, herhangi bir tanıdığı kişiyle %70 ve üzerinde benzerlik bulursa o kişiyi tanıdığını kabul eder
2. Tanınan kişiler yeşil çerçeve ile, tanınmayanlar kırmızı çerçeve ile gösterilir
3. Tanınan kişilerin ismi ve eşleşme yüzdesi görüntü üzerinde gösterilir
4. Program, aynı kişileri her 10 saniyede bir tekrar rapor eder (gereksiz tekrarı önlemek için)
5. Çıkmak için görüntü penceresindeyken "q" tuşuna basın

## Sorun Giderme

- **Yüz tanıyamıyorsam:** Daha fazla ve farklı açılardan yüz örnekleri ekleyin
- **Kamera bağlantı sorunu:** Doğru IP adresi, kullanıcı adı ve şifre bilgilerini kontrol edin
- **Yanlış kişileri tanıma:** Daha fazla yüz örneği ekleyerek modeli iyileştirin
- **H.264 hataları:** RTSP bağlantı ayarlarını değiştirin veya kameranızın çözünürlüğünü düşürün 