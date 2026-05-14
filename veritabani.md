# Proje: Kişisel Bilgi Yönetimi (PKM) ve Kaynak Kütüphanesi
# Aşama: Veritabanı Tasarımı (Ver. 1.0)

## 1. Genel Kurallar ve Teknoloji Yığını
- **Veritabanı:** SQLite
- **ORM:** SQLAlchemy (2.0 tarzı, declarative mapping kullanılacak)
- **Mimari:** Modeller `models/` klasörü altında ayrı dosyalarda tanımlanmalıdır.
- **Tarih/Zaman:** Tüm tarih alanları UTC standartlarında `datetime` objesi olarak tutulmalı ve varsayılan olarak eklendiği anı almalıdır (default=func.now()).

## 2. Temel Tablolar ve Şema Tanımları

### Tablo: categories (Kategoriler)
Kaynakların üst gruplaması (Örn: Makale, Video, GitHub, Ders Notu).
- `id` (Integer, Primary Key)
- `name` (String, Unique, Required): Kategorinin adı.
- `color_hex` (String): Arayüzde gösterilecek renk (örn: #FF0000).
- `icon` (String): Arayüzde gösterilecek ikon kodu veya emoji.

### Tablo: tags (Etiketler)
Mikro kategorizasyon için (Örn: #python, #machine-learning).
- `id` (Integer, Primary Key)
- `name` (String, Unique, Required): Etiket adı (küçük harflerle ve boşluksuz tutulması tavsiye edilir).

### Tablo: resources (Ana Kaynaklar Tablosu)
Sistemdeki her bir içeriğin temel kayıt noktası.
- `id` (Integer, Primary Key)
- `title` (String, Required): Kaynağın başlığı.
- `url` (String, Nullable): Eğer kaynak bir web bağlantısıysa.
- `category_id` (Integer, ForeignKey('categories.id'))
- `status` (Enum): Kaynağın durumu. Değerler: 'PLANNED' (Planlandı), 'IN_PROGRESS' (Devam Ediyor), 'COMPLETED' (Tamamlandı).
- `priority` (Integer): 1 (Düşük), 2 (Orta), 3 (Yüksek). Varsayılan: 2.
- `progress` (Float): 0.0 ile 100.0 arasında ilerleme yüzdesi.
- `is_pinned` (Boolean): Sabitlenmiş mi? Varsayılan: False.
- `content` (Text, Nullable): Kaynağa ait genel notlar (Markdown formatında saklanacak).
- `extra_metadata` (JSON, Nullable): **KRİTİK ALAN.** Kaynağın tipine özel ekstra verilerin esnek bir şekilde tutulacağı alan. (Örn: YouTube ise video süresi, GitHub ise yıldız sayısı, Makale ise yazar adı bu JSON içinde tutulacak).
- `created_at` (DateTime, Default: now)
- `updated_at` (DateTime, Default: now, onupdate: now)

### Tablo: resource_tags_link (N:N İlişki Tablosu)
`resources` ve `tags` tabloları arasındaki Many-to-Many ilişkiyi sağlar.
- `resource_id` (Integer, ForeignKey('resources.id'))
- `tag_id` (Integer, ForeignKey('tags.id'))

## 3. Gelecek Fazlar İçin Hazırlık Tabloları (PDF ve Makale Sistemi)
*Not: Bu tablolar şimdiden oluşturulmalı ancak CRUD servisleri sonra yazılacaktır.*

### Tablo: highlights (Vurgular ve Alıntılar)
PDF veya web makalelerinden seçilip çıkarılan spesifik metinler.
- `id` (Integer, Primary Key)
- `resource_id` (Integer, ForeignKey('resources.id')): Hangi kaynaktan alındığı.
- `content` (Text, Required): Seçilen/vurgulanan metin.
- `page_number` (Integer, Nullable): Eğer bir PDF ise hangi sayfadan alındığı.
- `color` (String): Vurgu rengi (Sarı, Yeşil vb.).
- `created_at` (DateTime, Default: now)

### Tablo: vocabulary (Kelime Dağarcığı / Çeviriler)
Yabancı makalelerden kaydedilen kelimeler.
- `id` (Integer, Primary Key)
- `resource_id` (Integer, ForeignKey('resources.id')): Kelimenin rastlandığı kaynak.
- `word` (String, Required): Orjinal kelime veya kelime öbeği.
- `translation` (String, Required): Çevirisi.
- `context_sentence` (Text, Nullable): Kelimenin içinde geçtiği orjinal cümle (Bağlamı anlamak için).
- `mastery_level` (Integer): Aralıklı tekrar (spaced repetition) için öğrenme seviyesi (0-5 arası).
- `created_at` (DateTime, Default: now)

## 4. Beklenen Çıktı (AI Görevi)
Lütfen yukarıdaki şemaya uygun olarak SQLAlchemy veri modellerini (`models.py` veya `models/` dizini altında) oluştur. İlişkileri (`relationship`) back_populates kullanarak çift yönlü olarak tanımla.

💡 Hap Bilgi: extra_metadata JSON alanı, sisteminizin gelecekteki esnekliğinin anahtarıdır. Yarın bir "Twitter (X) Thread" kaydetmek isterseniz, veritabanı şemasını değiştirmeden sadece bu JSON alanına {"tweet_count": 12, "author": "@kullanici"} verisini gömmeniz yeterli olacaktır. SQLAlchemy JSON tiplerini doğrudan Python sözlükleri (dictionary) olarak harika bir şekilde yönetir.