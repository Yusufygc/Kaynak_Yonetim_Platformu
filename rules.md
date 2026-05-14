# Proje: Kişisel Bilgi Yönetimi (PKM) - Kodlama ve Mimari Kuralları

Bu doküman, projenin geliştirilmesi sırasında uyulması gereken KESİN mimari ve kodlama standartlarını içerir. Tüm kod üretimleri bu kurallara tabi olmalıdır.

proje ortamı:C:\Users\ysfygc\anaconda3\envs\KaynakYonetim

## 1. Yazılım Prensipleri (Software Principles)
- **SOLID:** Tüm sınıflar Tek Sorumluluk (Single Responsibility) ilkesine uymalıdır. Sınıflar genişlemeye açık, değişime kapalı (Open/Closed) olmalıdır. Bağımlılıkların tersine çevrilmesi (Dependency Inversion) için arayüzler/soyut sınıflar (ABC) kullanılacaktır.
- **Clean Code:** Değişken ve fonksiyon isimleri kendi kendini açıklayıcı (self-documenting) olmalıdır. `process_data()` gibi belirsiz isimler yerine `extract_metadata_from_url()` gibi net isimler kullanılmalıdır. Yorum satırları sadece "Neden?" sorusunu cevaplamak için kullanılmalı, "Nasıl?" sorusunu zaten kodun kendisi anlatmalıdır.
- **DRY (Don't Repeat Yourself):** Tekrar eden hiçbir mantık yazılmamalıdır. Ortak fonksiyonlar `utils/` veya `helpers/` dizinlerine taşınmalıdır.
- **Teknik Borç (Technical Debt):** "Şimdilik çalışsın, sonra düzeltiriz" (Hack) yaklaşımları KESİNLİKLE YASAKTIR. Her modül yazıldığında test edilebilir ve izole olmalıdır.

## 2. Merkezi Varlık ve Tema Yönetimi (Central Asset Management)
Tüm UI bileşenleri hard-coded değerler yerine aşağıdaki merkezi dosyalardan beslenmelidir:
- **Stringler:** `core/constants/strings.py` (Gelecekte i18n desteği için tüm metinler buradan çekilecek).
- **Renkler ve Palet:** `core/constants/colors.py` (Örn: `Colors.PRIMARY_BACKGROUND = "#1E1E2E"`).
- **Fontlar:** `core/constants/fonts.py` (Örn: `Fonts.H1 = QFont("Inter", 24, QFont.Bold)`).
- **İkonlar:** Standart ikonlar için `qtawesome` kütüphanesi kullanılacaktır. Özel ikonlar veya logolar `assets/icons/` klasöründe SVG formatında tutulacak ve `core/constants/icons.py` üzerinden yönetilecektir.

## 3. Stil Yönetimi (QSS / Stylesheets)
- Inline styling (kod içinde `setStyleSheet`) KULLANILMAYACAKTIR.
- Stiller `assets/styles/` dizini altında modüler `.qss` dosyaları olarak tutulacaktır.
- Her büyük pencere veya bileşenin kendi QSS dosyası olmalıdır (Örn: `assets/styles/main_window.qss`, `assets/styles/resource_card.qss`).
- Renkler QSS dosyalarına enjekte edilmeden önce `colors.py` üzerinden okunup dinamik olarak formatlanmalıdır.

## 4. Mimari Desenler (Design Patterns)
- **Model-View-Controller (MVC) / Model-View-Presenter (MVP):** UI (View) veritabanı veya iş mantığını (Model) doğrudan ÇAĞIRAMAZ. İletişim her zaman Controller/Presenter veya Servis katmanı üzerinden olmalıdır.
- **Repository Pattern:** Veritabanı sorguları (SQLAlchemy) UI veya Servis koduna karışmamalı, `repositories/` klasörü altındaki sınıflarda (Örn: `ResourceRepository`) izole edilmelidir.
- **Dependency Injection:** Servisler veya UI bileşenleri, ihtiyaç duydukları veritabanı oturumlarını (session) veya bağımlılıkları constructor (`__init__`) üzerinden dışarıdan almalıdır.
- **Event-Driven UI:** Arayüz güncellemeleri için doğrudan metod çağırmak yerine PySide6 `Signal` ve `Slot` yapısı kullanılmalıdır.

## 5. Konfigürasyon, Hata ve Log Yönetimi
- **Konfigürasyon:** Uygulama ayarları (DB yolu, ortam değişkenleri) `core/config.py` üzerinden yönetilecektir (Pydantic BaseSettings veya standart `os.environ` tercih edilebilir).
- **Hata Yönetimi:** Kaba `Exception` yakalamak yerine `core/exceptions.py` içinde tanımlanmış projeye özel özel hata sınıfları (Custom Exceptions) kullanılmalıdır. (Örn: `raise InvalidURLError("URL formatı hatalı")`).
- **Loglama:** Sadece konsola print atmak yasaktır. `core/logger.py` üzerinden yapılandırılmış, hem dosyaya (app.log) hem konsola yazan standart `logging` modülü kullanılmalıdır.

## 6. Wiki dosyaları güncellemesi
her işlemden sonra ilgili wiki dosyası güncellecek.

## 7.Commit
yapılan işlmeler uygun ve detaylı açıklamalarla commit edilecek. Türkçe harflere dikkat et. ve claude code referansı verme.