# Fikirler Modülü (Ideas Module)

Uygulamanın ana "Kaynaklar" (Resources) yapısından tamamen izole, bağımsız olarak tasarlanmış bir modüldür. Temel amacı, kullanıcıların projeleriyle veya içerikleriyle ilgili aklına gelen ham fikirleri, hızlıca kaydedip Kanban usulüyle süreçlerini yönetmelerini sağlamaktır.

## Temel Bileşenler

- **Model:** `Idea` (`models/idea.py`). Başlık (`title`), isteğe bağlı detaylı açıklama (`description`), statü (`status` -> `IdeaStatus` Enum) ve öncelik derecesi (`priority`) içerir.
- **Veri Katmanı:** `IdeaRepository` (`repositories/idea_repo.py`) üzerinden veritabanı ile konuşulur. BaseRepository'den miras alır.
- **İş Mantığı:** `IdeaService` (`services/idea_service.py`), boş başlık gibi girdileri doğrular, CRUD operasyonlarını yapar ve Event Bus üzerinden arayüze sinyaller fırlatır.
- **Arayüz (UI):**
  - `IdeaView`: 4 sütunlu (Yeni, Değerlendiriliyor, Kabul Edildi, Reddedildi) Kanban panosu görünümünü sunar. İçerisinde yeni fikir eklemek için bir Stack yapısıyla Form alanını barındırır.
  - `IdeaCard`: Fikri gösteren, üzerinde ileri/geri taşıma, silme ve düzenleme butonları bulunan kart bileşenidir. Önceliğe göre rengi (accent_color) değişir.
  - `IdeaForm`: Yeni fikir eklemek veya olanı düzenlemek için kullanılan basit giriş formudur.

## İlişkiler ve İletişim

Fikirler modülü kendi repository'sine ve tablosuna sahip olduğu için silinen/eklenen bir fikir doğrudan diğer kaynakları (Resource) etkilemez.
`core/events.py` dosyasında `idea_added`, `idea_updated`, `idea_deleted` isimli özel sinyaller tanımlanmıştır. `resource_flow.py` içindeki `_on_idea_changed` metodu, bu sinyalleri dinleyerek ekranı yenilemek için `ContentWorkspace.refresh()` çağrısı yapar.

## Öncelik (Priority) ve Renkler

Kartların sol şerit renkleri (AccentFrame üzerinden verilir) fikrin önceliğine göre otomatik atanır. Renkler `ui/theme_utils.resolve_theme_color()` ile aktif temadan okunur (hardcoded HEX yok, `event_bus.theme_changed`'a abone olup tema değişince yeniden boyanır):
- Öncelik 1 (Yüksek): `Colors.DANGER`
- Öncelik 2 (Orta): `Colors.ACCENT`
- Öncelik 3 (Düşük) / diğer: `Colors.TEXT_SECONDARY`

Metin etiketleri (`Yüksek`/`Orta`/`Düşük`) `core/constants/status.py` içindeki `PRIORITY_LABELS`/`priority_label()` üzerinden merkezi olarak yönetilir; `idea_card.py` ve `idea_form.py` bu tek kaynağı kullanır.
