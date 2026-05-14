# Proje: Kişisel Bilgi Yönetimi (PKM)
# Modül: Dinamik Tema Yönetimi (Dark/Light ve Genişletilebilir Yapı)

## 1. Mimari Yaklaşım (Dinamik QSS Enjeksiyonu)
PySide6'da tema yönetimi, sabit renklerin kod içine yazılmasıyla değil, merkezi bir `ThemeManager` sınıfı üzerinden yönetilmelidir. Gelecekte "Ocean", "Dracula" veya "Solarized" gibi yeni temaların eklenebilmesi için renkler bir sözlük (dictionary) veya JSON yapısında tutulacaktır.

- **Dosya Konumu:** `core/theme_manager.py` ve `core/themes/` dizini.
- **Mantık:** QSS dosyalarında doğrudan HEX kodları (örn: `#FFFFFF`) yazmak YASAKTIR. Bunun yerine değişkenler (örn: `{{ bg_primary }}`) kullanılacak, `ThemeManager` tema değiştiğinde bu değişkenleri o anki temanın renkleriyle değiştirip (string replace) derlenmiş QSS'i ana uygulamaya (`QApplication`) basacaktır.

Daha önce kurduğumuz **Event Bus** mimarisi bu iş için biçilmiş kaftan. Tema değiştiğinde merkezden bir sinyal fırlatılacak ve tüm arayüz anında yeni renklere bürünecek.

## 2. Tema Veri Yapısı (Theme Definitions)
`core/themes/` klasörü altında her tema için bir Python sözlüğü (veya dataclass) oluşturulmalıdır.

```python
# Örnek: core/themes/dark.py
DARK_THEME = {
    "name": "dark",
    "bg_primary": "#1E1E2E",      # Ana arka plan
    "bg_secondary": "#2A2A3C",    # Kart ve panel arka planı
    "text_primary": "#FFFFFF",    # Ana metin rengi
    "text_secondary": "#A0A0B0",  # Alt başlık ve tarihler
    "accent_color": "#82AAFF",    # Vurgu (butonlar, aktif menüler)
    "border_color": "#3B3B54",    # Çizgiler ve ayırıcılar
    "icon_color": "#E0E0E0"       # qtawesome vb. için ikon rengi
}
# Light tema için de tam zıttı renklerle LIGHT_THEME oluşturulmalıdır.
```

## 3. ThemeManager Sınıfı (`core/theme_manager.py`)

Bu sınıf bir Singleton olarak tasarlanmalıdır.

* **Görev 1:** Aktif temayı hafızada tutmak.
* **Görev 2:** `apply_theme(theme_name: str)` metodu çağrıldığında, `assets/styles/` altındaki base QSS dosyalarını okumak, `{{ degisken }}` kısımlarını temanın renkleriyle değiştirmek ve uygulamanın ana stili olarak (`setStyleSheet`) ayarlamak.
* **Görev 3:** Event Bus üzerinden tüm uygulamaya temanın değiştiğini haber vermek.

## 4. Event Bus Entegrasyonu ve İkonların Güncellenmesi

Tema değiştiğinde sadece arka plan ve metinler (QSS ile) değişmekle kalmaz; kod içinde `qtawesome` ile oluşturulmuş ikonların renklerinin de yeniden çizilmesi gerekir.

* AI, `core/events.py` içindeki `_EventBus` sınıfına şu sinyali KESİNLİKLE eklemelidir:

```python
theme_changed = Signal(dict)  # Aktif temanın renk sözlüğünü (dict) fırlatır
```

* **UI Bileşenlerinin Reaksiyonu:**
Bir arayüz bileşeni (Örn: `Sidebar` veya `ResourceCard`) kendi içinde `qtawesome` ikonu barındırıyorsa, `__init__` metodunda `event_bus.theme_changed` sinyaline abone olmalıdır.
Sinyal tetiklendiğinde çalışan Slot fonksiyonu, ikonları yeni temanın `icon_color` veya `accent_color` verisine göre tekrar oluşturmalıdır.

*Doğru Kullanım Örneği:*

```python
def on_theme_changed(self, theme_data: dict):
    # İkonu yeni temanın rengine göre güncelle
    new_icon = qtawesome.icon('fa5s.book', color=theme_data["icon_color"])
    self.my_button.setIcon(new_icon)
```

## 5. Kullanıcı Deneyimi (UI/UX)

* Sol menünün (Sidebar) en altında "Tema Değiştir" (Ay veya Güneş ikonu) adında bir buton bulunmalıdır.
* Butona tıklandığında `ThemeManager.toggle_theme()` tarzı bir metod çağrılarak Dark ve Light mod arasında geçiş yapılmalıdır. Son seçilen tema kullanıcının yerel ayarlarına (`QSettings` veya `config.json`) kaydedilmelidir ki uygulama bir sonraki açılışta aynı temayla başlasın.
