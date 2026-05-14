# Proje: Kişisel Bilgi Yönetimi (PKM)
# Aşama: Arayüz (UI) İskeleti ve Layout Tasarımı (Ver. 2.0)

## 1. Genel Arayüz Mimarisi (Master-Detail Pattern)
Uygulama ana ekranı (`MainWindow`) modern bir "Three-Pane" (Üç Sütunlu) yapıda olmalıdır. Sütunlar arasında kullanıcıya genişlikleri ayarlama imkanı sunan yatay bir `QSplitter` kullanılacaktır.

- **Sol Sütun:** Navigasyon (Sidebar).
- **Orta Sütun:** Ana İçerik Alanı (Standart Liste veya Bağlantı Vitrini).
- **Sağ Sütun:** Detay Paneli ve Editör.

**ÖNEMLİ:** Arayüz oluştururken hard-coded (sabit) renk veya font kullanmak yasaktır. Tüm görsel değerler `core/constants/` klasöründen veya QSS dosyalarından çekilmelidir.

## 2. Pencereler ve Bileşenler (Components)

### 2.1. Sol Menü - Sidebar (`ui/components/sidebar.py`)
- `QListWidget` veya `QTreeView` kullanılarak tasarlanmalıdır.
- **Üst Kısım:** "Tüm Kaynaklar", "Gelen Kutusu", "Planlananlar" ve **"Bağlantı Vitrini"**.
- **Orta Kısım:** Veritabanından dinamik çekilen Kategoriler (İkon + İsim).
- **Alt Kısım:** Etiketler (Tags) listesi.
- Arka plan rengi, uygulamanın genel arka planından hafifçe farklı bir tonda olmalıdır.

### 2.2. Orta Panel - Ana İçerik Alanı (`ui/views/content_view.py`)
Sol menüdeki seçime göre içeriklerin listelendiği alandır.
- **Üst Bar (Top Bar):** Geniş bir arama çubuğu (`QLineEdit`), "Yeni Ekle" butonu ve görünüm filtreleri.
- **İçerik Alanı (`QScrollArea`):** Kartların listelendiği esnek alan. 
  - *Kritik Kural:* İçerikler pencere genişliğine göre alt satıra geçmelidir (wrap). Bunun için özel bir **`FlowLayout`** sınıfı kullanılacaktır.
  - Kartlar **KESİNLİKLE aynı boyutta (sabit genişlik ve yükseklik) ve standart bir ızgara (uniform grid) hizasında** olmalıdır. Karmaşık asimetrik yapılardan kaçınılacaktır.

## 3. Kart Tasarımları (Card Widgets)
Orta panelde, kaynağın türüne göre iki farklı kart tipinden biri gösterilecektir. İkisi de `QFrame`'den türetilmelidir.

### 3.1. Standart Kaynak Kartı (`ui/components/resource_card.py`)
- Sadece metin veya not içeren standart kaynaklar için kullanılır.
- **İçerik:** Kategori İkonu, Başlık (uzunsa `...` ile kesilmeli), Eklenme Tarihi, Durum Göstergesi ve alt kısımda Etiket rozetleri.

### 3.2. Zengin URL Kartı (`ui/components/url_rich_card.py`)
- Sadece web bağlantısı (URL) içeren ve meta verisi çekilmiş kaynaklar ("Bağlantı Vitrini" görünümü) için kullanılır. Standart karta göre dikeyde daha uzundur.
- **İç Yapısı (Yukarıdan Aşağıya):**
  1. **Kapak Görseli:** Kartın üst yarısını kaplayan resim alanı (Resim yoksa favicon veya ikon).
  2. **Başlık ve Özet:** Sitenin meta başlığı (bold, max 2 satır) ve altında meta açıklaması (description).
  3. **Alt Bar:** Sol tarafta kategori rozeti, sağ tarafta "Tarayıcıda Aç" (External Link) ikonlu buton.
- **Görsel Dinamik (Border Context):** Kartın sol kenarına (örn: `border-left: 4px solid {color}`), o kaynağın ait olduğu **etiketin veya kategorinin ana rengi** dinamik olarak atanmalıdır.
- **Etkileşim:**
  - "Tarayıcıda Aç" butonuna tıklanırsa: İşletim sisteminin varsayılan tarayıcısında URL açılır (`QDesktopServices.openUrl`).
  - Kartın gövdesine tıklanırsa: `event_bus.resource_selected` fırlatılır ve sağ detay paneli açılır.

### 3.3. Hover ve Tıklama Efektleri
Tüm kartlar için fare üzerine geldiğinde hafifçe yukarı kalkma (margin) veya gölgenin (DropShadow) belirginleşmesi gibi QSS bazlı geri bildirimler eklenmelidir.

## 4. Sağ Panel - Detay ve Editör (`ui/views/detail_view.py`)
Kart tıklandığında açılan paneli temsil eder.
- **Üst Kısım (Header):** Başlık, URL bağlantısı (tıklanabilir), Durum (Status) ComboBox'ı ve İlerleme (% olarak) güncelleyici.
- **İçerik/Notlar (Body):** Markdown formatını destekleyen zengin bir metin alanı (`QTextEdit`). 
- **Kapatma:** Sağ üst köşede paneli gizlemek için bir kapatma butonu bulunmalıdır.

## 5. Boş Durumlar (Empty States)
Veritabanında hiç öğe yokken veya filtrelenen kategoride sonuç çıkmadığında ortalanmış, soluk bir ikon ve "Burada henüz bir şey yok. Yeni Ekle'ye basarak ilk kaynağınızı oluşturun." mesajı içeren şık bir widget gösterilmelidir.