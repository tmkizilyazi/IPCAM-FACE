# IP Kamera Yüz Tanıma Uygulaması

Bu uygulama, belirtilen IP adresi üzerinden kamera görüntüsüne erişerek yüz tanıma işlemi yapar.

## Gereksinimler

Aşağıdaki kütüphanelerin kurulu olması gerekmektedir:

```
pip install -r requirements.txt
```

## Kullanım

İki farklı program bulunmaktadır:

### 1. Sabit Ayarlı Program

Sabit IP ve kullanıcı bilgileriyle çalışır:

```
python ip_kamera_yuz_tanima.py
```

Bu program dosyada tanımlanmış varsayılan ayarları kullanır.

### 2. Etkileşimli Program (Önerilen)

Kullanıcıdan bağlantı bilgilerini alarak çalışır:

```
python ip_kamera_baglanti.py
```

Bu program size soracağı bilgilerle kameraya bağlanma denemesi yapar:
- IP adresi (varsayılan: 10.34.51.53)
- Kullanıcı adı (varsayılan: admin)
- Şifre (varsayılan: admin)
- URL formatı (RTSP, HTTP veya özel format)

Bağlantı başarısız olursa, farklı format ve bilgilerle yeniden deneme seçeneği sunar.

## Ayarlar

Sabit ayarları değiştirmek isterseniz, `ip_kamera_yuz_tanima.py` dosyasındaki şu satırları düzenleyin:

```python
ip_adresi = "10.34.51.53"
kullanici_adi = "admin"
sifre = "admin"
url = f"rtsp://{kullanici_adi}:{sifre}@{ip_adresi}/live"
```

## Sorun Giderme

- 401 Unauthorized hatası alırsanız, doğru kullanıcı adı ve şifre bilgilerini kullandığınızdan emin olun.
- Farklı kamera modelleri farklı URL formatları kullanabilir, kamera dokümanlarınızı kontrol edin.
- Etkileşimli programı kullanarak farklı URL formatlarını deneyebilirsiniz. 