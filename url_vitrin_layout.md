# Proje: Kişisel Bilgi Yönetimi (PKM)
# Modül: URL Vitrini ve Görsel Kart Sistemi (Bağımsız Eklenti)

## 1. Modülün Amacı (Konsept)
Sisteme kaydedilen web bağlantılarının (URL), sadece metin tabanlı bir listede kaybolmasını önlemek amacıyla; sitenin meta verilerinden (OpenGraph, Title, Description, Kapak Görseli) beslenen zengin içerikli "Görsel Kartlar" oluşturulacaktır. Bu kartlar, uygulamanın "Bağlantı Vitrini" (URL Showcase) adındaki ayrı bir sekmesinde sergilenecektir.

## 2. Arayüz Bileşenleri (UI Components)

### 2.1. URL Vitrin Sekmesi (`ui/views/url_showcase_view.py`)
- Ana ekranın sol menüsünden (Sidebar) "Bağlantı Vitrini" seçildiğinde açılacak özel bir sayfadır.
- **Düzen (Layout):** İçerikler yan yana dizilen, ekran genişliğine göre alt satıra esnek bir şekilde kayan (FlowLayout veya Masonry düzeni) bir `QScrollArea` içerisinde sergilenmelidir.
- Sadece `url` alanı dolu olan ve meta verisi çekilmiş (işlenmiş) kaynaklar burada listelenmelidir.

### 2.2. Zengin URL Kartı (`ui/components/url_rich_card.py`)
Bu kart, standart kaynak kartından (`resource_card.py`) farklı, daha büyük ve görsel odaklı özel bir widget (`QFrame` veya `QWidget`) olmalıdır.

**Kartın İç Yapısı (Yukarıdan Aşağıya):**
1. **Kapak Görseli (Thumbnail):** Kartın üst yarısını kaplayan, yuvarlatılmış köşelere sahip (border-radius) resim alanı. (Resim yoksa, sitenin favicon'u veya kategorinin ikonu büyük ve soluk bir şekilde ortalanmalıdır).
2. **Başlık ve Özet:** Sitenin meta başlığı (bold ve en fazla 2 satır) ve altında gri tonda kısa meta açıklaması (description - elips ile kesilmiş).
3. **Alt Bar (Aksiyon ve Etiketler):** - Sol tarafta ait olduğu kategori/etiket rozeti.
   - Sağ tarafta "Tarayıcıda Aç" (External Link) ikonlu belirgin bir buton.

## 3. Görsel Dinamikler ve Renk Kodlaması
- **Dinamik Çerçeve (Border Context):** Kartın tamamına veya sol kenarına (Örn: `border-left: 4px solid {color}`), o kaynağın ait olduğu **etiketin veya kategorinin merkez rengi** atanmalıdır. Böylece kullanıcı vitrine baktığında hangi rengin hangi konuya (Örn: Mavi=Yazılım, Yeşil=Finans) ait olduğunu göz ucuyla ayırt edebilir.
- **Hover Efekti:** Fare ile kartın üzerine gelindiğinde, kart hafifçe yukarı kalkmalı (margin/padding oyunları ile) veya gölgesi (DropShadow) belirginleşmelidir.

## 4. Etkileşim ve Olay Yönetimi (Interaction & Logic)
- **Tarayıcıda Aç Butonu:** Kartın üzerindeki özel butona tıklandığında, PySide6'in yerleşik aracı olan `QDesktopServices.openUrl(QUrl(url_string))` veya Python'un `webbrowser` modülü kullanılarak link KESİNLİKLE kullanıcının varsayılan işletim sistemi tarayıcısında (Chrome, Edge vb.) yeni sekmede açılmalıdır.
- **Detaya Git:** Kartın resmine veya gövdesine tıklandığında ise (butona değil), ana sistemdeki `event_bus.resource_selected` sinyali fırlatılarak kaynağın sağ paneldeki detay görünümü tetiklenmelidir.