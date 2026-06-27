# Otopark Plaka Tanıma ve Giriş/Çıkış Takip Sistemi

Bu proje, bir otopark giriş/çıkış kontrol sistemi geliştirerek araçların plakalarını tanır, giriş ve çıkış saatlerini kaydeder ve otopark doluluk durumunu takip eder. Python ile geliştirilmiştir ve bilgisayarda çalışan bir arayüz içerir.

## 🧠 Kullanılan Teknolojiler ve Kütüphaneler

* Python 3.x
* OpenCV
* PyQT
* pytesseract (OCR)
* EasyOCR
* datetime
* os
* tkinter
* PIL (Pillow)

## 🚀 Kurulumu

```bash
git clone https://github.com/selimttasdemir/PlakaTanimaOtoparkKontrolSistemi.git
cd PlakaTanimaOtoparkKontrolSistemi
```

## 🧪 Kullanım

```bash
python plaka_arayuz.py
```

Arayüz açıldığında:

<img src="plaka_tanima.gif" width="800" />

* Görüntüden plaka tanıma yapılır
* Giriş/çıkış saatleri otomatik olarak kaydedilir
* GUI üzerinden anlık doluluk oranı görüntülenir

## 💡 Özellikler

* Kamera üzerinden canlı plaka tanıma (OCR ile)
* Araç giriş/çıkış zamanlarını kaydetme
* Otopark kapasite kontrolü
* Kullanıcı dostu GUI (tkinter)

## 🧾 Notlar

* Proje demo amaçlıdır. Plaka tespiti kısmı basitleştirilmiştir, doğrudan OCR uygulanır.
* Daha yüksek doğruluk için YOLOv8 veya benzeri bir tespit modeli eklenebilir.

## 📅 Gelecek Planları

* SQLite veritabanı desteği
* Web arayüzü (Flask veya Django ile)
* Araç tipi sınıflandırması için YOLOv8 modeli entegrasyonu
