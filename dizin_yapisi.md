# Proje: Kişisel Bilgi Yönetimi (PKM) - Dizin Yapısı ve Modül Haritası

Bu doküman, projenin fiziksel dosya yapısını ve her bir dizinin sorumluluklarını tanımlar. AI asistanı yeni bir modül veya sınıf oluştururken KESİNLİKLE bu yapıya sadık kalmalıdır.

## Ana Dizin Yapısı (Root Directory)

```text
pkm_app/
│
├── main.py                 # Uygulamanın giriş noktası (Entry point). Sadece başlatma işlemleri.
├── requirements.txt        # Proje bağımlılıkları (PySide6, SQLAlchemy, qtawesome vb.)
├── .env.example            # Örnek ortam değişkenleri dosyası
│
├── assets/                 # Statik dosyalar (UI ile ilgili dış kaynaklar)
│   ├── icons/              # Özel SVG/PNG ikonlar (qtawesome dışında kalanlar)
│   └── styles/             # Modüler .qss dosyaları (Örn: main.qss, card.qss)
│
├── core/                   # Uygulamanın kalbi: Yapılandırma, sabitler ve temel araçlar
│   ├── __init__.py
│   ├── config.py           # Ortam değişkenleri ve veritabanı yolları (Settings)
│   ├── logger.py           # Merkezi loglama yapılandırması
│   ├── exceptions.py       # Projeye özel Custom Exception sınıfları
│   └── constants/          # Merkezi yönetim dosyaları (Hardcoded değerleri önlemek için)
│       ├── strings.py      # Metinler ve mesajlar
│       ├── colors.py       # Renk paleti (HEX kodları)
│       ├── fonts.py        # QFont tanımlamaları
│       └── icons.py        # İkon yolları veya qtawesome referansları
│
├── models/                 # Veritabanı (Domain) Modelleri - Sadece SQLAlchemy sınıfları
│   ├── __init__.py
│   ├── base.py             # SQLAlchemy Declarative Base sınıfı
│   ├── category.py         # Category modeli
│   ├── tag.py              # Tag modeli
│   └── resource.py         # Resource modeli (Ana tablo)
│
├── repositories/           # Veri Erişim Katmanı (Infrastructure)
│   ├── __init__.py
│   ├── base_repository.py  # Ortak CRUD işlemleri (Generic Repository)
│   └── resource_repo.py    # Kaynaklara özel veritabanı sorguları (Filtreleme, arama vb.)
│
├── services/               # İş Mantığı Katmanı (Business Logic)
│   ├── __init__.py
│   ├── resource_service.py # UI'dan gelen istekleri işler, Repository'e iletir
│   └── scraper_service.py  # Gelecekte eklenecek: URL'den meta veri çeken otonom servis
│
├── ui/                     # Sunum Katmanı (Presentation) - Sadece PySide6 kodları
│   ├── __init__.py
│   ├── controllers/        # Arayüz olaylarını (click, text_changed) yakalayan ve Servisleri çağıran mantık
│   │   └── main_controller.py
│   │
│   ├── views/              # Ana ekranlar ve pencereler
│   │   ├── main_window.py  # Ana çerçeve (Layout)
│   │   ├── grid_view.py    # Kaynakların listelendiği orta alan
│   │   └── detail_view.py  # Sağ panel (Detay/Editör alanı)
│   │
│   └── components/         # Tekrar kullanılabilir küçük UI parçacıkları
│       ├── resource_card.py# Grid içindeki tekil kaynak kartı tasarımı
│       ├── sidebar.py      # Sol menü (Kategoriler ve Etiketler)
│       └── search_bar.py   # Üst arama çubuğu
│
├── utils/                  # Her yerden erişilebilen yardımcı ve saf (pure) fonksiyonlar
│   ├── __init__.py
│   ├── date_utils.py       # Tarih formatlama fonksiyonları
│   └── db_utils.py         # Veritabanı oluşturma/bağlanma yardımcıları
│
└── tests/                  # Birim (Unit) ve Entegrasyon Testleri
    ├── test_models/
    ├── test_repositories/
    └── test_services/