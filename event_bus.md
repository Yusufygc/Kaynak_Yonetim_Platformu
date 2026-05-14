# Proje: Kişisel Bilgi Yönetimi (PKM)
# Aşama: Event Bus (Sinyal ve Olay Yönetimi) (Ver. 1.0)

## 1. Event Bus Mimarisi Nedir?
PySide6 arayüz bileşenleri (View veya Controller) birbirlerini KESİNLİKLE doğrudan referans almamalıdır. Bir bileşende durum değişikliği olduğunda (örn: yeni bir kaynak eklendiğinde), bu bileşen sadece merkeze (Event Bus) bir sinyal fırlatır (emit). İlgilenen diğer bileşenler (örn: Grid Listesi) bu merkeze abone (connect) olur ve sinyali dinler.

- **Desen:** Singleton Pattern + Observer Pattern (QObject üzerinden).
- **Dosya Konumu:** `core/events.py`

## 2. Global Event Bus Sınıfı
Yapay zeka, `core/events.py` dosyasını aşağıdaki kurallara ve yapıya uygun şekilde oluşturmalıdır.

```python
# Örnek Şablon (AI bu mantığı uygulamalıdır)
from PySide6.QtCore import QObject, Signal

class _EventBus(QObject):
    # --- Veri (Resource) Sinyalleri ---
    # Yeni kaynak eklendiğinde (Sinyal parametresi kaynağın ID'si veya dict verisi olabilir)
    resource_added = Signal(int)
    resource_updated = Signal(int)
    resource_deleted = Signal(int)

    # --- Kategori ve Etiket Sinyalleri ---
    category_added = Signal(int)
    tag_added = Signal(int)

    # --- UI Etkileşim Sinyalleri ---
    # Kullanıcı listeden bir karta tıkladığında sağ paneli açmak için
    resource_selected = Signal(int)

    # Arama çubuğunda metin değiştiğinde
    search_query_changed = Signal(str)

# Singleton örneği: Tüm uygulama bu instance'ı kullanacak
event_bus = _EventBus()
```

## 3. Kullanım Kuralları (AI İçin Kesin Talimatlar)

### 3.1. Sinyal Fırlatma (Emit)
Bir Controller, Service katmanı üzerinden veritabanına veri ekleme işlemini başarıyla tamamladıktan hemen sonra ilgili sinyali fırlatmalıdır.

Doğru Kullanım:

```python
from core.events import event_bus

# ... servis işlemi başarılı olduktan sonra ...
event_bus.resource_added.emit(new_resource.id)
```

### 3.2. Sinyal Dinleme (Connect / Slot)
Bir View veya bileşen, `__init__` metodunda `event_bus` üzerinden ilgili sinyallere abone olmalıdır.

Doğru Kullanım:

```python
from core.events import event_bus

class GridView(QWidget):
    def __init__(self):
        super().__init__()
        # ... UI kurulumları ...

        # Event Bus'a abone ol
        event_bus.resource_added.connect(self.on_resource_added)
        event_bus.search_query_changed.connect(self.filter_items)

    def on_resource_added(self, resource_id: int):
        # Sadece yeni eklenen veriyi veritabanından çek ve UI'a ekle
        self.refresh_list()
```

## 4. Bellek Yönetimi (Memory Management)
PySide6'da bellek sızıntılarını (memory leak) önlemek için, eğer bir UI bileşeni tamamen kapatılıp siliniyorsa (destroy), event_bus bağlantılarının da düşmesini sağlamak gereklidir. Gerekli durumlarda `disconnect()` kullanılmalı veya PySide6'in parent-child yaşam döngüsüne güvenilmelidir.

---

Bu yapıyı kurduğunuzda; örneğin gelecekte "Günün Özetini Çıkar" diyen yeni bir özellik veya modül eklerseniz, mevcut kodlara hiç dokunmadan o modülün sadece `event_bus.resource_added` sinyalini dinlemesini sağlamanız yeterli olacaktır. Sistem gerçek bir mikroservis gibi modüler hale gelir.
