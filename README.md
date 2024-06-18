
# Kimlik Kontrol Uygulaması

Bu proje, tkinter, OpenCV, face_recognition gibi kütüphaneler kullanılarak geliştirilmiş bir kimlik kontrol uygulamasıdır. Uygulama, kişileri kaydetme, silme, tanıma ve veritabanında listeleme gibi işlevleri içermektedir. Ayrıca, yüz tanıma teknolojisi kullanılarak kaydedilmiş kişileri kameradan tanıyabilir.


## Özellikler

- Kamera Entegrasyonu: OpenCV kullanılarak kameradan video akışı alınır.
- Yüz Tanıma: face_recognition kütüphanesiyle kameradan algılanan yüzler tanınır.
- SQLite Veritabanı: Kişilerin adı, soyadı, kimlik numarası ve yüz vektörleri SQLite veritabanında saklanır.
- Tkinter Arayüzü: Kullanıcı arayüzü olarak tkinter kullanılmıştır.
- Kişi Kaydetme ve Silme: Yeni kişiler kaydedilebilir ve var olan kayıtlar silinebilir.
- Kişi Listeleme: Veritabanındaki kayıtlı kişilerin listesi görüntülenebilir.

  
## Kullanım

Uygulamayı çalıştırdığınızda ana pencereye erişebilirsiniz. Farklı sekme seçenekleri arasında geçiş yaparak işlemlerinizi gerçekleştirebilirsiniz

  - Kontrol Sekmesi: Kameradan gelen görüntü üzerinde yüz tanıma işlemi yapabilirsiniz.
  - Kayıt Sekmesi: Yeni kişileri veritabanına kaydedebilirsiniz.
  - Liste Sekmesi: Veritabanındaki kayıtlı kişilerin listesini görüntüleyebilirsiniz.
  - Sil Sekmesi: Veritabanından kişileri kimlik numarası ile aratarak silebilirsiniz.

## Kurulum

Python 3.x'i yükleyin.

Gerekli kütüphaneleri yüklemek için terminalde veya komut isteminde komutları çalıştırın.

```bash
  conda install -c conda-forge dlib
```
```bash
  pip install cmake
```
```bash
  pip install opencv-python 
```
```bash
  pip install numpy 
```
```bash
  pip install face_recognition 
```

Uygulamayı başlatmak için ana dizinde şu komutu çalıştırın.

```bash
  python main.py
```


  
## Bağımlılıklar

- Python 3.x
- opencv-python
- numpy
- face-recognition
- pillow

  