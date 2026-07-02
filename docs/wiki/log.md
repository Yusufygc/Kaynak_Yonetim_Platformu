# Wiki Değişiklik Kayıt Defteri

En yeni girdi her zaman en üstte olmalıdır.

---

## [2026-07-02] KALDIRMA | Fikirler (Idea) modülü projeden çıkarıldı

Fikirler modülü tamamen kaldırıldı: `models/idea.py`, `repositories/idea_repo.py`, `services/idea_service.py`, `ui/views/idea_view.py`, `ui/components/idea_card.py`, `ui/components/idea_form.py` ve ilgili testler silindi. Entegrasyon noktaları temizlendi: sidebar nav item, `content_workspace.py` sayfa route'u, `main_controller.py`'deki `load_ideas`/`add_idea`/`update_idea`/`delete_idea`, `event_bus`'taki `idea_added`/`idea_updated`/`idea_deleted` sinyalleri, `resource_flow.py`'deki bağlantılar, `schemas.py`'deki `IdeaUpdateSchema`, `strings.py`/`icons.py`/`status.py`'deki idea'ya özel sabitler (`PRIORITY_LABELS` dahil — `filter_bar.py`'nin kendi ayrı `_PRIORITY_LABELS` listesi olduğu doğrulandı, dokunulmadı). Yeni Alembic revizyonu (`a7d8ff966efd_ideas_tablosunu_kaldir`) `ideas` tablosunu drop eder; gerçek kullanıcı veritabanında uygulandı (1 fikir kaydı kalıcı silindi), `resources`/`categories`/`tags` verisi değişmeden korundu. Detay: [[veritabani_migrasyonlari]]. 87/87 test yeşil (9 idea testi kaldırıldı).

---

## [2026-07-02] MIGRATION | Alembic'e geçiş

`utils/db_utils.py`'deki `Base.metadata.create_all()` + elle yazılmış `_LIGHTWEIGHT_MIGRATIONS` mekanizması Alembic ile değiştirildi. `pkm_app/alembic.ini` + `pkm_app/migrations/` eklendi; `env.py` modelleri import edip `target_metadata = Base.metadata` yapar, DB URL'ini `core.config.settings`'ten okur. İlk revizyon (`3997fe50be13_baseline`) autogenerate ile üretildi (7 tablo). `init_db()` üç senaryoyu ayırt eder: sıfırdan kurulum (`upgrade head`), Alembic-öncesi legacy DB (`stamp head`, şema değişmez), zaten yönetilen DB (bekleyen migration'lar uygulanır). Gerçek kullanıcı DB'sinin kopyası üzerinde doğrulandı: veri birebir korundu, orijinal dosya MD5 ile değişmedi. Detay: [[veritabani_migrasyonlari]]. `alembic>=1.13.0` bağımlılığı eklendi. 3 yeni test (`test_db_utils.py`), toplam paket 96/96 yeşil.

---

## [2026-07-02] PERF | Kaynak eklerken/güncellerken URL taramasını arka plana alma

`ResourceService` artık `ScraperService`'i doğrudan çağırmıyor (bağımlılık kaldırıldı, `_resolve_extra_metadata` helper'ı silindi). URL metadata çıkarımı `ResourceFlow` içinde `QThreadPool`/`QRunnable` ile arka plan thread'inde yapılıyor; sonuç güvenli (kuyruklu) Qt sinyaliyle ana thread'e taşınıp DB'ye yazılıyor. `ResourceFlow`, kuyruklu bağlantı garantisi için `QObject`'e çevrildi. Yavaş/yanıt vermeyen bir siteye kaynak eklerken arayüz artık donmuyor (`add_resource` ~16ms'de dönüyor, önceden ağ isteği bitene kadar bloklanıyordu). 3 yeni entegrasyon testi (`test_resource_flow.py`, gerçek `QThreadPool` ile).

---

## [2026-07-02] REFACTOR | Kaynak/fikir güncelleme akışını Pydantic şemaya taşıma

`ResourceService.add_new_resource`/`update_resource` ve `IdeaService.update_idea` artık tipsiz `dict` yerine yeni `services/schemas.py` içindeki Pydantic modellerini (`extra="forbid"`) kabul ediyor. Formda yazım hatasıyla girilen alan adı artık sessizce yutulmuyor, açık `ValidationError` olarak `MainController` üzerinden kullanıcıya bildiriliyor. `update_resource()` ayrıca alan bazlı yardımcı metodlara bölündü (cyclomatic complexity düşürüldü); davranış değişmedi.

---

## [2026-07-02] TEST | Servis/repo/controller kapsamı genişletme + SSRF koruması

`CategoryService`, `TagService`, repository katmanı (`base`/`category`/`tag`/`idea`) ve `MainController` için hiç test yoktu; validasyon, duplicate, not-found ve `event_bus` sinyal senaryoları eklendi. `ScraperService.extract_metadata` artık hedef hostname'i çözüp loopback/private/link-local adreslere istek atmıyor (SSRF koruması); mevcut scraper testleri gerçek DNS'e bağımlı kalmasın diye otomatik sahte DNS fixture'ı eklendi.

---

## [2026-07-02] FIX | Fikirler modülünü kaynak modülü standardına çekme

`idea_service.py` artık diğer servisler gibi `log.exception` atıyor ve orijinal exception tipini koruyor (önceden her hata `ValidationError`'a sarılıp loglanmadan yutuluyordu). `idea_card.py` hardcoded HEX renkler yerine `resolve_theme_color` ile tema paletini kullanıyor. `Idea` modeli `Mapped[...]`/`func.now()`/`timezone=True` stiline taşındı (Resource ile tutarlı, önceden naive `datetime.utcnow` kullanıyordu), kullanılmayan `to_dict()` kaldırıldı. Öncelik etiketleri (`Yüksek`/`Orta`/`Düşük`) `core/constants/status.py`'de `PRIORITY_LABELS` ile merkezileştirildi. `.gitignore`'daki genel `*.md`/`docs/` kuralı yüzünden hiç commitlenmemiş olan `CLAUDE.md`/`rules.md` git takibine alındı.

---

## [2026-05-17] FIX | UI layout iyileştirmeleri ve vitrin senkronizasyonu

ContentView ve UrlShowcaseView içerisindeki boş durum (empty state) düzen kaymaları QStackedWidget kullanılarak çözüldü. AccentFrame (ResourceCard ve UrlRichCard tabanı) güncellendi: soldaki kalın durum çizgisi kaldırılarak yerine kategori renginde 1px'lik ince bir çerçeve eklendi ve köşeler daha yumuşak (12px) hale getirildi. Vitrin sayfasındayken kaynak silindiğinde ekranın anında güncellenmemesi sorunu, ResourceFlow'daki `is_content_active` kısıtlamasının kaldırılması ve `ContentWorkspace.refresh()` metodunun `SettingsView` yönlendirmelerini koruyacak şekilde güncellenmesiyle çözüldü.

---

## [2026-05-17] FEATURE | Kategori renk picker + ResourceCard kategori rengi

Kategori renk girişleri görselleştirilerek `ColorPickerButton` bileşeni eklendi ve `QColorDialog` entegrasyonu sağlandı. Ayarlar sayfasındaki düz metin (`QLineEdit`) tabanlı renk alanları bu yeni bileşenle değiştirildi. Kart şerit vurgu rengi (`accent_color`) için yeni kural getirildi: `ResourceCard` sol şerit rengi artık öncelikle kategori rengini kullanır, kategori yoksa veya rengi geçersizse eski davranıştaki gibi durum (status) rengine (`fallback`) döner. Yeni QSS kuralları eklendi.

---

## [2026-05-17] FEATURE | Filtreleme + Pin + Favori sistemi

Üç ayrı yetenek tek pakette: (1) `resources.is_favorite` kolonu eklendi; `utils/db_utils.py` içine idempotent lightweight migration helper'ı geldi (`ALTER TABLE` eksik kolonları ekler). (2) `ResourceRepository.query_filtered()` ile kombinasyonel filtre (statuses, category_id, tag_ids, priorities, favorites_only, urls_only, keyword) tek noktada; tüm sorgular `is_pinned desc, created_at desc` ile sıralanır — pinli kayıtlar her listede üstte. `get_favorites()`, `set_pinned()`, `set_favorite()` eklendi. (3) Yeni `ui/components/filter_bar.py` → kategori dropdown + çoklu etiket dropdown + durum chip'leri + öncelik chip'leri + temizle. `ContentView` ve `UrlShowcaseView` üst kısmına eklendi. `ContentWorkspace` artık `_active_filters` state'i tutar, FilterBar sinyallerini dinler, sidebar değişiminde resetler; kategori/etiket CRUD sonrası FilterBar beslemesi otomatik yenilenir. Sidebar'a "Favoriler" nav item'ı (`fa5s.star`); kart üzerine `PinButton` + `FavoriteButton` (yeni `ui/components/card_icon_button.py`). `MainController.toggle_pin/toggle_favorite` + `load_resources_with_filters`. EventBus'a 3 yeni sinyal (`resource_pin_toggle_requested`, `resource_favorite_toggle_requested`, `filters_changed`). Yeni `assets/styles/filters.qss` (tema token'ları, hardcoded HEX yok). 4 yeni service testi eklendi. Test paketi 40/40 geçti.

---

## [2026-05-17] REFACTOR | UI mimari bölünmesi: ContentWorkspace + ResourceFlow + ResourceDetailPanel

MainWindow ve DetailView üç farklı sorumluluğu karıştırıyordu (compose + filter dispatch + flow). UI üç yatay katmana bölündü: (1) **MainWindow** ~55 satır, sadece Sidebar/Splitter/Workspace/DetailView kompozisyonu yapar. (2) Yeni `ui/views/content_workspace.py` → `ContentWorkspace(QWidget)`: main_stack (ContentView/SettingsView/UrlShowcaseView) + sözlük tabanlı `apply_filter` dispatcher + `refresh()`. (3) Yeni `ui/controllers/resource_flow.py` → `ResourceFlow`: UI olmayan koordinatör, event_bus ve DetailView/Workspace sinyallerini MainController çağrılarına çevirir. DetailView ince stack koordinatörüne indirildi; view-page widget'ları `ui/components/resource_detail_panel.py` (`ResourceDetailPanel`) ve `ui/components/empty_detail.py` (`EmptyDetail`) altına çıkarıldı. Alt panel sinyalleri aynı isimle DetailView'den dışarı relay edilir — dış API kırılmadı. Tüm QSS objectName'ler birebir korundu (DetailTitle, DetailCloseButton, StatusCombo, ProgressSpin, NotesEdit, vb.). `test_ui_style_debt.py` `ResourceDetailPanel` import edecek şekilde güncellendi. Test paketi 36/36 geçti.

---

## [2026-05-17] REFACTOR | Exe-uyumlu path katmanı, TR string düzeltmesi, DRY temizliği

`pkm_app/core/paths.py` eklendi: `resource_path()` (frozen ortamda `sys._MEIPASS`, dev'de pkm_app/ kökü) ve `user_data_dir()` (Windows `%APPDATA%/PKM`, macOS `~/Library/Application Support/PKM`, Linux `$XDG_DATA_HOME/PKM`). `config.py`, `theme_manager.py`, `core/constants/icons.py` ve `main.py` bu helper'a taşındı; SQLite DB ve `app.log` artık kullanıcı veri dizinine yazılır, QSS ve ikon klasörü bundle uyumlu çözülür. `main.py` içindeki `sys.path` enjeksiyonu yalnızca dev modunda çalışır. `strings.py` içindeki 38 UI metni doğru Türkçe diakritiklere (ş, ğ, ü, ö, ı, ç, İ) çevrildi. Küçük DRY refaktörleri: `resource_service._resolve_extra_metadata` helper'ı ile add/update arasındaki metadata merge tekrarı kaldırıldı; `settings_view._reload_rows` generic helper'ı `_reload_categories` ve `_reload_tags`'i sadeleştirdi; `detail_view._signals_blocked` context manager'ı blockSignals çiftlerini sarmaladı; `main_window` ve `resource_form` içindeki inline import'lar dosya başına taşındı. Tüm test paketi (36/36) geçti.

---

## [2026-05-15] FIX | Badge alpha renkleri ve vitrin okunabilirligi

Qt tarafinda `#RRGGBBAA` renklerin yanlis yorumlanmasi duzeltildi; sidebar secili arka plani ve hover arka planlari opak tema tokenlarina tasindi. Durum rozetleri artik dogru alpha ile boyanir. URL vitrin karti buyutuldu; thumbnail, baslik, aciklama ve aksiyon satiri daha okunabilir araliklarla render edilir.

---

## [2026-05-15] FIX | URL etiketleri, metadata ve ilerleme senkronu

Devam Ediyor durum rengi amber yerine violet/indigo palete tasindi. Kartlar kaynak aciklamasini veya metadata aciklamasini gosterecek sekilde genisletildi. Detay panelinde durum secenekleri Turkce label'lara baglandi ve ilerleme alani integer yuzdeye cevrildi. Progress/status senkronu servis katmaninda merkezilestirildi. URL'den platform/domain etiketi turetme eklendi; manuel etiketler korunur. Metadata cikarimi OpenGraph, Twitter Card, canonical/favicon/site_name ve YouTube thumbnail fallback kapsami ile guclendirildi.

---

## [2026-05-15] FIX | ColorBadge font weight enum duzeltmesi

`ColorBadge.paintEvent()` icindeki sayisal `QFont.setWeight(650)` kullanimi PySide6 uyumlu `QFont.Weight.DemiBold` enum degerine cevrildi. UI statik testlerine sayisal font weight kullanimini yakalayan kontrol eklendi.

---

## [2026-05-15] UX | Canli profesyonel tema ve mikro etkilesimler

Dark/light paletler canli ama profesyonel renklerle genisletildi (`accent_secondary`, gradient, hover/elevated surface, focus ring, shadow, success/warning tokenlari). Base/sidebar/cards/detail/settings QSS dosyalari gradient primary aksiyonlar, daha net focus/hover state'leri, daha okunakli font fallback zincirleri ve elevated yuzeylerle yenilendi. `AccentFrame` hoverProgress animasyonu ve shadow/lift hissi kazandi. Sidebar nav item'lari qtawesome ikonlariyla gosterilir ve tema/secim rengine gore guncellenir. Stil borcu testlerine tema token esligi ve icon smoke kontrolleri eklendi.

---

## [2026-05-15] FIX | P3 stil borcu temizligi

Tema sozlukleri semantik tokenlarla genisletildi (`danger_*`, `on_accent`, status renkleri, thumbnail/swatch tokenlari). UI kodundaki inline `setStyleSheet` kullanimlari kaldirildi; kart accent seridi, renk rozetleri ve kategori swatch'i painter tabanli `AccentFrame`, `ColorBadge`, `ColorSwatch` bilesenlerine tasindi. QSS dosyalarinda kalan sabit HEX degerleri tema tokenlarina cevrildi. Statik stil borcu testleri ve offscreen Qt widget smoke testleri eklendi.

---

## [2026-05-15] FIX | Veri guvenligi, etiket senkronizasyonu ve URL metadata

Kategori silme davranisinda `delete-orphan` kaldirildi; kaynaklar silinmeden `category_id` NULL olur. SQLite foreign key pragma acildi. `ResourceService` tag listesini normalize/dedupe eder ve `update_resource(..., tag_names=...)` ile etiket iliskilerini tam senkronize eder. `CategoryService`/`TagService` yazma akislari rollback standardina alindi. `ScraperService.extract_metadata()` OpenGraph title/description/image/favicon cikarir; hata durumunda bos metadata ile devam eder. `UrlRichCard` thumbnail URL'lerini Qt network ile async yukler. Paket import smoke testi icin `pkm_app` uyumluluk aliaslari ve pytest kapsami eklendi.

---

## [2026-05-15] FIX | Sayfa yonlendirme + URL Vitrini + Kaynak duzenleme + Code Review

`ResourceStatus.INBOX` eklendi. `load_resources_by_filter` inbox/planned dallari tamamlandi. `UrlShowcaseView` `main_stack`'e mount edildi (index 2), artik `UrlRichCard` ile gosteriyor. `DetailView`: Düzenle/Sil butonlari + 2-tikli sil onayi + "Notu Kaydet" butonu + `edit_requested`/`delete_requested`/`content_updated`/`status_updated` sinyalleri eklendi. `ResourceForm` edit modu (`load_resource`), status alani, priority sirasi Yüksek→Orta→Düşük. `MainController.update_resource`, `search_resources` eklendi. Leaky `_resource_svc` erisimi controller'a tasindi. URL regex schemesiz pattern kaldirild. Dead code (`_on_search` DB sorgusu, `tag:` hasattr hack) temizlendi. `sidebar.py` `theme_changed` baglantisi `_connect_signals`'e tasindi.

---

## [2026-05-15] BUILD | Ayarlar sayfasi + Kategori/Etiket CRUD

`SettingsView(QTabWidget)` iki sekmeli: Kategoriler + Etiketler. Her sekme scroll listesi, `CategoryRow`/`TagRow` inline edit + 2-tikli silme, alt kisminda yeni kayit formu. `MainWindow` QStackedWidget yapisi: `ContentView` (index 0) + `SettingsView` (index 1). Sidebar "Ayarlar" nav item eklendi. `TagService.create_tag` + `update_tag` eklendi. Controller 6 CRUD metod. `event_bus.tag_updated` sinyali. QDialog/QMessageBox: 0.

---

## [2026-05-15] BUILD | Yeni Ekle formu ve inline banner eklendi

`ResourceForm(QFrame)`: title/url/category/priority/tags/content alanları, `submitted(dict)` + `cancelled()` sinyalleri. `InlineBanner(QLabel)`: auto-hide 3.5sn, severity property ile QSS renk seçimi (error=kırmızı, info=accent). `DetailView` → `QStackedWidget` (empty/view/form 3 sayfa), `show_form(categories)` + `form_submitted(dict)` sinyali. `ContentView` inline banner host. `MainWindow._on_add_requested` + `_on_form_submitted` + `_on_error` dolduruldu. `event_bus.error_occurred(str)` sinyali eklendi. QDialog/QMessageBox kullanımı sıfır.

---

## [2026-05-14] BUILD | Kart bileşenleri, URL Vitrini ve QSS tema dosyaları tamamlandı

ResourceCard (240×160, durum rengi sol kenar, etiket rozetleri), UrlRichCard (260×300, thumbnail, og_title/desc, tarayıcıda aç), UrlShowcaseView (FlowLayout). sidebar.qss, cards.qss, detail.qss — tüm renkler {{degisken}} şablonuyla ThemeManager üzerinden enjekte.

---

## [2026-05-14] BUILD | PySide6 UI iskeleti tamamlandı

FlowLayout, SearchBar, Sidebar, ContentView (boş durum dahil), DetailView (URL/durum/ilerleme/notlar), MainWindow (Three-Pane QSplitter), MainController, main.py (init_db + tema + pencere başlatma).

---

## [2026-05-14] BUILD | Service katmanı (iş mantığı) kodlandı

ResourceService: add_new_resource (URL doğrulama, kategori/etiket kontrolü, commit/rollback), update_resource, update_resource_progress (100→COMPLETED), delete_resource. CategoryService: create (HEX doğrulama, duplikat), update, delete. TagService: get_or_create_tag, delete_tag.

---

## [2026-05-14] BUILD | Repository katmanı kodlandı

BaseRepository[T] (Generic CRUD, flush — commit yok). ResourceRepository: get_by_status, search_by_keyword (ILIKE), get_with_tags, get_by_category, get_pinned, get_urls_only. TagRepository: get_by_name. CategoryRepository: get_by_name.

---

## [2026-05-14] BUILD | SQLAlchemy modelleri ve DB yardimcilari kodlandi

`models/`: Base, Category, Tag, Resource (ResourceStatus enum, extra_metadata JSON, priority, progress, is_pinned), Highlight, Vocabulary. N:N: resource_tags_link. Tüm relationship'ler back_populates ile cift yonlu. `utils/db_utils.py`: engine, SessionLocal, init_db(), get_session().

---

## [2026-05-14] BUILD | core/events.py Event Bus kodlandı

`_EventBus(QObject)` Singleton. Sinyaller: resource (added/updated/deleted), category (added/updated/deleted), tag (added/deleted), resource_selected, search_query_changed, sidebar_filter_changed, theme_changed(dict).

---

## [2026-05-14] BUILD | core/ temel yapı taşları kodlandı

`core/config.py` (Pydantic Settings), `core/logger.py` (RotatingFileHandler), `core/exceptions.py` (5 özel hata sınıfı), `core/constants/` (strings, colors, fonts, icons), `core/themes/dark.py` + `light.py`, `core/theme_manager.py` (Singleton, QSS şablon enjeksiyonu), `assets/styles/base.qss` (dinamik tema şablonu).

---

## [2026-05-14] SCAFFOLD | Proje dizin iskeleti ve stub dosyaları oluşturuldu

`pkm_app/` altında tüm klasörler, `__init__.py` dosyaları ve boş stub modüller oluşturuldu.
Kapsam: `core/`, `models/`, `repositories/`, `services/`, `ui/` (controllers/views/components), `utils/`, `tests/`, `assets/`.
Ek: `.env.example`, `pkm_app/main.py` stub.

---

## [2026-05-14] INIT | Wiki anayasası kuruldu, tüm konsept sayfaları oluşturuldu

Kaynak: `rules.md` (anayasa/çalışma kuralları), kök dizindeki 7 mimari `.md` dosyası.
Oluşturulan sayfalar: `index.md`, `mimari_kurallari.md`, `dizin_yapisi.md`, `veritabani_semasi.md`, `core_servisler.md`, `event_bus.md`, `tema_yonetimi.md`, `ui_layout.md`, `url_vitrin.md`.
Düzeltilen kök dosyalar: `event_bus.md` (fence syntax), `tema_yonetimi.md` (outer markdown fence kaldırıldı).
