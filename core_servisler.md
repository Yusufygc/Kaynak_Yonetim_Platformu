# Proje: Kişisel Bilgi Yönetimi (PKM)
# Aşama: Core Servisler ve Repository Katmanı (Ver. 1.0)

## 1. Mimari Beklentiler ve Oturum (Session) Yönetimi
- **Dependency Injection:** Veritabanı oturumu (`Session`) sınıf içinde yaratılmamalı, Repository ve Service sınıflarının `__init__` metodlarına dışarıdan enjekte edilmelidir. Bu, test edilebilirliği (mocking) sağlar.
- **Transaction Yönetimi:** `commit()` ve `rollback()` işlemleri Repository katmanında DEĞİL, Service katmanında yapılmalıdır. Repository sadece sorguyu hazırlar ve `session.add()` yapar. İşlemin bütünlüğü Service katmanının sorumluluğundadır.

## 2. Repository Katmanı (`repositories/`)
Bu katman SADECE SQLAlchemy kullanarak veritabanı ile konuşur. İş mantığı (if/else kuralları) içermez.

### 2.1. BaseRepository (Generic CRUD)
Dosya: `repositories/base_repository.py`
Tüm modellere hizmet edecek jenerik bir sınıf yazılmalıdır (Python `TypeVar` ve `Generic` kullanılarak).
- `get_by_id(id: int) -> Model`
- `get_all() -> list[Model]`
- `create(obj: Model) -> Model`
- `update(obj: Model) -> Model`
- `delete(id: int) -> bool`

### 2.2. ResourceRepository (Özelleşmiş Sorgular)
Dosya: `repositories/resource_repo.py`
`BaseRepository`'den miras almalı ve `resources` tablosuna özel karmaşık sorguları içermelidir:
- `get_by_status(status: Enum) -> list[Resource]`
- `search_by_keyword(keyword: str) -> list[Resource]` (Başlık, URL veya içerikte arama yapmalı - ILIKE veya MATCH)
- `get_with_tags(tag_ids: list[int]) -> list[Resource]`

## 3. Service Katmanı (`services/`)
Bu katman uygulamanın "beynidir". Arayüzden gelen veriyi doğrular (validation), iş kurallarını uygular ve Repository'e iletir. Arayüz (UI) veritabanını hiç bilmez, sadece bu servisleri tanır.

### 3.1. ResourceService
Dosya: `services/resource_service.py`
Bu sınıf, arayüzden gelen `dict` veya `dataclass` formatındaki verileri alıp modeller.
- **Bağımlılıklar:** `ResourceRepository`, `TagRepository`, `CategoryRepository`.
- **Metod: `add_new_resource(data: dict) -> Resource`**
  - **Kural:** Eğer `data` içinde bir URL varsa, geçerli bir URL formatı olup olmadığını regex veya `urllib` ile doğrula. Geçersizse `InvalidURLError` fırlat.
  - **Kural:** Kategori ID gönderilmişse, böyle bir kategorinin var olup olmadığını `CategoryRepository` ile kontrol et. Yoksa `ResourceNotFoundError` fırlat.
  - İşlem başarılıysa `session.commit()` yap. Hata olursa `session.rollback()` yap.
- **Metod: `update_resource_progress(resource_id: int, progress: float)`**
  - **Kural:** Progress 0-100 arasında olmalıdır. Değilse `ValueError` fırlat.
  - Eğer progress 100 ise, kaynağın statüsünü otomatik olarak `COMPLETED` olarak güncelle.

### 3.2. Tag ve Category Services
Dosya: `services/tag_service.py` ve `services/category_service.py`
- `get_or_create_tag(name: str) -> Tag`: Etiketler için sık kullanılan bir işlem. Veritabanında varsa getir, yoksa yarat ve getir.
- `create_category(name: str, color_hex: str, icon: str) -> Category`: Renk kodunun (HEX) doğru formatta (örn: #FFFFFF) olduğunu doğrula.

## 4. Hata Sınıfları (Exceptions)
Dosya: `core/exceptions.py`
Servislerin fırlatacağı hatalar standart `Exception` olmamalı, buradaki sınıfları kullanmalıdır:
- `ValidationError`: Girdi kurallara uymadığında.
- `ResourceNotFoundError`: ID'ye sahip kayıt bulunamadığında.
- `InvalidURLError`: URL formatı bozuk olduğunda.
- `DuplicateRecordError`: Aynı isimde kategori vs. eklenmeye çalışıldığında.