# UAV Yer Kontrol İstasyonu (GCS) Projesi İnceleme Notları

Bu proje, bir İnsansız Hava Aracı (İHA / UAV) için tasarlanmış kapsamlı bir **Yer Kontrol İstasyonu (Ground Control Station - GCS)** yazılımıdır. Python ve **PySide6 (Qt)** tabanlı masaüstü uygulaması olarak geliştirilmiş olup, drone ile haberleşmek için **ROS 2 (Jazzy) ve MAVROS**, harita arayüzü için **Folium/QtWebEngineTools**, video akışı takibi için ise **ROS 2 sensor_msgs/Image** ve **cv_bridge** entegrasyonu barındırmaktadır.

Aşağıda projenin sahip olduğu tüm modüllerin fonksiyonel detayları, birbirleriyle nasıl haberleştikleri ve mimari yapısı en ince ayrıntılarına kadar özetlenmiştir.

---

## 1. Mimari Genel Bakış
Uygulama, temel olarak asenkron ve çoklu iş parçacıklı (multi-threading) bir yapıya sahiptir. Qt Framework'ün `QThread` ve `Signal/Slot` (Sinyal/Yuva) mekanizmaları kullanılarak, arayüzü kilitlemeden arka planda eşzamanlı olarak dronedan konum verilerinin alınması (PyMavlink) ve video akışının çözümlenmesi sağlanır. 
**Temel Haberleşme Döngüsü:**
1. Arka plan thread'lerinden (ROS 2 MAVROS veya Video) veri gelir.
2. Bu veriler (telemetri veya görüntü frame'i), Qt Sinyalleri aracılığı ile fırlatılır (emit edilir).
3. UI (Kullanıcı Arayüzü) modülleri, bu sinyalleri yakalayarak haritayı, hedef sayfalarını ve göstergeleri (Indicators) anlık olarak günceller.

---

## 2. Modüllerin İncelenmesi

### A. Çekirdek ve Arayüz (UI) Modülleri

#### 1. `main.py`
Uygulamanın çalışmaya başladığı başlangıç (entry-point) dosyasıdır. Qapplication nesnesini ayağa kaldırır ve `MainWindow`'u oluşturup ekranda gösterir.

#### 2. `MainWindow.py` (Ana Pencere)
Bütün kullanıcı arayüzü sayfalarının birleştiği omurgadır. 
- **Özellikleri:** Frameless (çerçevesiz ve üst barlara sahip olmayan), özel buton tasarımı, maksimize/minimize özellikleri kendisi tarafından simüle edilen bir yapı.
- **Navigasyon:** QStackedWidget kullanılarak 3 ana panel arasında (`HomePage`, `TargetsPage`, `IndicatorsPage`) geçiş yapılmasını yönetir.
- **Görev:** İHA ile bağlantı kurmayı sağlayan `ArdupilotConnectionThread` nesnesini başlatır. Arayüzdeki (Connect, Takeoff, RTL vb.) aksiyon tuşlarına basıldığında, bunları doğrudan Connection modülünün fonksiyonlarına bağlar.
- **Modülerlik (`AllocateWidget`):** Haritayı veya Kamera ekranını ana pencereden söküp (allocate widget) ayrı ve başıboş (standalone) bir pencere haline getirmeyi veya sonrasında tekrar entegre etmeyi sağlayan bir mekanizması da mevcuttur.

#### 3. `HomePage.py` (Ana Sayfa)
Harita (`MapWidget`) ve Kamera (`CameraWidget`) görüntüleme araçlarını barındırır.
- Kullanıcının dronu komuta ettiği asıl sahadır.
- İşaretçi (Marker), Alan Seçimi (Poligon çizimi) ve Waypoint (Rota) ekleme/çıkarma gibi harita fonksiyonlarını doğrudan barındırır ve Folium/Javascript tabanlı harita üzerindeki fonksiyonları JavaScript enjeksiyonu ile (Örn: `mapwidget.page().runJavaScript(...)`) tetikler.
- Görev onayı (Set Mission) verildiğinde irtifa (altitude) bilgisini alarak `Exploration` ya da normal `Waypoint` uçuşu olarak Drone'a rotayı gönderir.

#### 4. `IndicatorsPage.py` (Göstergeler Paneli)
Drone'un o anki Hız, Dikey Hız (Vertical Speed), Pusula/Yön (Heading), Yükseklik (Altitude) ve İrtifa/Eğim (Attitude - Pitch & Roll) gibi değerlerinin gösterildiği paneldir.
- **Çalışma Prensibi:** `ArdupilotConnectionThread` sınıfından gelen sinyallerdeki verileri alır.
- **Haberleşme/Animasyon:** Cansız çizimler yerine, alınan güncel değerleri `QPropertyAnimation` ile animasyonlu (akıcı ibre dönüşü) olarak yansıtır.

#### 5. `TargetsPage.py` ve `MediaPlayer.py` (Hedef Yönetimi)
Sahada (görüntü işleme üzerinden) veya operasyonda tespit edilen "Hedefleri" (hedeflerin anlık görsellerini) listelemeye, kaydetmeye ve tekrar oynatmaya yarar.
- **TargetsPage:** Ulaşan hedefleri listeler, koordinatlarını çeker ve kaydeder.
- **MediaPlayer:** VLC python wrapper modülüdür. Hedefin tespit edildiği video akışını tekrar oynatmak için özelleştirilmiş, zaman, hız ve ses ayarlarını kontrol edebilen bir medya oynatıcı içerir (`CustomSlider` aracılığı ile kontrol edilir).

#### 6. `MapWidget.py` (Harita Modülü)
- Harita oluşturmak için **Folium** modülü, render edilmesi için ise Qt'un `QtWebEngineCore` sınıfı kullanılmıştır.
- **Haberleşme:** PySide6 ile WebEngine içerisindeki HTML/JS kodları iç içe geçmiş bir hibrid sisteme sahiptir. JS üzerinden yeni varış noktaları işaretlendiğinde konumlar yakalanıp Python ortamına değişken olarak aktarılır. Kullanıcı bir Marker eklediğinde veya Alan Seçimi modunda çizim yaptığında, bu Python tarafından MAVLink komutasyonuna (rota olarak) çevrilir. (UAV ikonları vb. base64 ile kodlanarak gömülmüştür).

#### 7. `CameraWidget.py`
Video panelini kontrol eder. İçerisinde `Database.VideoStream` modülünü başlatır ve ekranda akıcı frame render işlemini yönetir.

---

### B. İletişim, Arka Plan (Background) ve Drone Yönetimi Modülleri

#### 8. `Vehicle/ArdupilotConnection.py` (Drone Haberleşme Merkezi)
Bu sistemin kalbidir. ROS 2 ve MAVROS üzerinden Otopilot (Ardupilot/PX4) ile haberleşmeyi yürütür. Arayüzün kilitlenmemesi için işlemler node olarak başlatılır ve `QThread` alt sınıfında çalıştırılır.
- **Özellikler:** rclpy üzerinden ROS 2 node'u oluşturup MAVROS servis ve topic'lerini kullanır.
- **Dinleme (Telemetry):** Sürekli olarak `/mavros/global_position/global`, `/mavros/vfr_hud`, `/mavros/state`, `/mavros/imu/data` gibi topicleri dinler ve arayüzü günceller.
- **Komut Gönderme:** Arayüzden gelen istekler doğrultusunda MAVROS servisleri arka planda Otopilota gönderilir:
  - Takeoff (Kalkış)
  - RTL (Alandan Kalkışa Dönüş)
  - Move_to/Goto (Belirli Noktaya Gitme `setpoint_position/global` ile)
  - Set ROI (Kameranın belirli noktaya ilgiyle / track edilerek dönmesi)
  - Land (İniş)
  - **Upload Mission:** Görev rotalarını araca yükler (`/mavros/mission/push` ile)

#### 9. `Vehicle/Exploration.py` (Alan Keşif ve Rota Algoritması)
Alan (poligon) seçimi yapılarak "keşif" moduna girildiğinde çalışan matematik/geometri motorudur.
- **Çalışma Prensibi:** Haritada düzensiz iki nokta (dikdörtgen alanı) belirlendiğinde, tarama yapılacak bölgeyi İHA'nın Kamerası FOV (Görüş Açısı - Field of View) limiti ve yüksekliğine (Altitude) bakarak analiz eder.
- **Çıktı:** Bölgeyi tam kapasite tarayabilmek için birbirine eşit mesafeli (Lawn Mower tipi - çim biçme makinesi modeli) koordinat/waypoint izlerini hesaplayarak matematiksel olarak İHA'ya yeni uçuş hedefleri çıkartır. (Haversine vb. küresel trigonometrik formüller içerir).

#### 10. `Database/VideoStream.py`
Fiziksel /Companion Computer üzerinden gelen videoyu alan modüldür. Daha önceki soket bazlı yapının aksine artık doğrudan ROS 2 üzerinden çalışır.
- **İletişim Kuralları:** ROS 2 mekanizması olan `sensor_msgs/Image` tipindeki `/camera/image_raw` topic'ine abone (subscribe) olur, mesajları Node üzerinden dinler.
- Python OpenCV (cv2) ve **cv_bridge** yardımı ile buffer üzerinden görüntüyü QImage formatına dönüştürüp arayüzdeki (CameraWidget) ekrana `ImageUpdate` sinyaliyle gönderir.

---

## 3. Akış Şeması Örneği (Use-Case Senaryosu)
1. Kullanıcı `MainWindow` üzerinden "Connect" tuşuna basıp BaudRate ile sisteme bağlanır.
2. `ArdupilotConnectionThread` ayağa kalkar ve İHA ile karşılıklı Heartbeat yapmaya başlar.
3. Thread'den gelen koordinat verileri `MainWindow` içerisindeki `MapWidget` kısmında Folium marker'ı (İHA Simgesi) pozisyonlayarak anlık drone güncellemelerine başlar.
4. Eşzamanlı atılan sinyalle `IndicatorsPage` tarafındaki Hız/İrtifa gösterge animasyonları da dönmeye başlar.
5. Kullanıcı `CameraWidget` üzerinden "Connect"e basarak `VideoStreamThread`'i aktifleştirir ve canlı dron çekimini ekranda görür.
6. Harita üzerinde `Alan Seçimi (Exploration)` modu seçilip hedefler seçildiğinde ve İrtifa onaylandığında; alan köşe koordinatları `Exploration.py`'ye gönderilir. Formüller aracıyla izlenecek grid yollar (Waypoints) çıkarılıp `ArdupilotConnectionThread` üzerinden MAVLink `MISSION_ITEM` dizisi(list) olarak otopilota (Upload) yazılır ve otonom uçuş başlatılır.
7. Akışta bir anomali durumunda kamerada hedef tespit edildiğinde "Target Detected" uyarılarıyla `TargetsPage`'ye log ve video düşer.

**NOT:** Uygulamanın Core GCS prensipleri tam kapasite Qt ve ROS 2/MAVROS konseptlerine dayandırılarak yüksek esneklik sağlayacak şekilde tasarlanmıştır.
