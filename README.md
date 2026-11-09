# MIL-STD-2525E Sembol Görselleştirici ve Link 16 Teşhis Dönüştürücü

30 haneli **MIL-STD-2525E SIDC** kodlarını oluşturan, çözümleyen ve sembolünü çizen bir masaüstü (Tkinter) uygulaması. SIDC ile **STANAG 5516 Ed.9 (Link 16)** 5 harfli teşhis kodu arasında iki yönlü dönüşüm yapar.

> ⚠️ **Doğrulama notu:** Link 16 platform/activity harf kodları (FT, CP, TK…) STANAG 5516 ile karşılaştırılmamıştır. Operasyonel kullanımdan önce standart dokümanıyla doğrulayın. Ayrıntı için [Bilinen sınırlamalar](#bilinen-sınırlamalar).

## Özellikler

- **SIDC oluşturma:** 30 hanenin tamamı (Set A / B / C) açılır menülerle seçilir. Entity araması ve hızlı tarama listesi vardır.
- **SIDC çözümleme:** 30 haneli bir kodu yapıştırın, menüler otomatik dolar.
- **Sembol önizleme:** [milsymbol](https://pypi.org/project/milsymbol/) ile çizilir, SVG veya PNG olarak kaydedilebilir.
- **SIDC → Link 16:** SIDC her değiştiğinde 5 harfli teşhis kodu, J mesajı ve açıklaması hesaplanır (ör. `FFTCP`).
- **Link 16 → SIDC:** 5 harfli koddan önerilen SIDC üretilir ve sembol çizilir. Tatbikat kodları desteklenir: `K` = Faker, `J` = Joker.
- **CSV dışa aktarma:** Tüm ortamlar (Air, Surf, Subsurf, Gnd, Space) için Link 16 ↔ SIDC eşleme tabloları.

## Kurulum

Sistem paketleri (Debian/Ubuntu):

```bash
sudo apt install python3-tk python3-venv libcairo2
```

Sanal ortam ve Python paketleri:

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
source .env/bin/activate
python visualizerGrk.py
```

`python milstd2525e_visualizer.py` da aynı uygulamayı açar (eski giriş noktası). SIDC oluşturucuyu sembol önizlemesi olmadan açmak için: `python milstd2525e_sidc.py`.

## Kullanım

| İşlem | Nasıl |
|---|---|
| SIDC oluştur | Sol paneldeki menülerden seçim yapın. SIDC ve Link 16 kodu anında güncellenir. |
| SIDC çözümle | "SIDC Çözümle" kutusuna 30 haneli kodu yazıp **Çözümle**'ye basın. |
| Link 16 → SIDC | Sağ alttaki kutuya 5 harfli kodu (ör. `HDDSU`) yazıp **Enter**'a veya **SIDC'ye Dönüştür**'e basın. |
| Dışa aktar | **SVG Kaydet** / **PNG Kaydet**. Dosya adı `SIDC_TEŞHİS` biçiminde önerilir. |
| Kopyala | **Panoya Kopyala** (SIDC) / **Kodu Kopyala** (Link 16). |

Link 16 teşhis kodunun yapısı:

```
  H   FT   CP
  │   │    └─ Activity (görev)
  │   └────── Platform
  └────────── Kimlik: P U A F N S H, tatbikat için K (Faker) / J (Joker)
```

## Eşleme tabloları (CSV)

| Dosya | İçerik |
|---|---|
| `link16_sidc_eslesme.csv` | Platform/Activity ↔ Symbol Set / Entity / Mod1 / Mod2 (kimlikten bağımsız) |
| `link16_kimlik.csv` | 1. harf ↔ SIDC Context (Poz 3) + Identity (Poz 4) |
| `link16_sidc_tum_kimlikler.csv` | İkisinin birleşimi: her eşleme × 9 kimlik, hazır teşhis kodu ve hazır SIDC |

`Yon` sütunu eşlemenin hangi yönde geçerli olduğunu gösterir:

- **İki yönlü:** İki yönde de birbirine dönüşür.
- **Yalnızca SIDC → Link16:** Aynı teşhis kodu birden fazla SIDC'den çıkabilir. Ters dönüşümde "İki yönlü" satırdaki SIDC üretilir.
- **Yalnızca Link16 → SIDC:** 2525E'de karşılığı olmayan kodlar (LS, MP).

CSV'ler koddaki tablolardan üretilir. Tabloları değiştirdikten sonra yeniden üretmek için:

```bash
python tools/export_link16_csv.py            # proje köküne yazar
python tools/export_link16_csv.py çıktı/     # başka klasöre yazar
```

Dosyalar virgülle ayrılmıştır ve UTF-8 (BOM'lu) kaydedilir. Türkçe Excel'de tek sütun görünürse **Veri → Metinden/CSV'den** ile içe aktarıp ayraç olarak virgülü seçin.

## Proje yapısı

```
├── visualizerGrk.py            Ana uygulama: arayüz, sembol önizleme, Link 16 paneli
├── milstd2525e_sidc.py         SIDC menü tabloları + temel oluşturucu/çözümleyici arayüz
├── link16_ed9.py               Link 16 ↔ SIDC dönüşüm motoru (GUI'den bağımsız)
├── milstd2525e_visualizer.py   Geriye dönük uyumluluk giriş noktası
├── tools/export_link16_csv.py  CSV eşleme tablolarını üretir
├── tests/test_link16_ed9.py    Birim ve tutarlılık testleri
└── requirements.txt
```

### Link 16 tablolarını düzenleme

Eşlemeler `link16_ed9.py` içindeki sözlüklerde tutulur:

| Sözlük | Kapsam |
|---|---|
| `AIR_ENTITY_MAP`, `AIR_MOD1_MAP`, `AIR_MOD2_MAP` | Hava (Set 01) |
| `SURFACE_ENTITY_MAP` | Suüstü (Set 30) |
| `SUBSURFACE_ENTITY_MAP` | Sualtı (Set 35) |
| `LAND_UNIT_MAP` / `LAND_EQUIPMENT_MAP` | Kara birlik (Set 10) / teçhizat (Set 15) |
| `MOD2_OVERRIDES` | Sector 2 modifier'ın platformu belirlediği durumlar (Fast Patrol, SSN/SSK) |
| `REVERSE_ONLY` | Yalnızca Link 16 → SIDC yönünde kullanılan kodlar |

Anahtarlar `milstd2525e_sidc.py` menü tablosundaki kodlarla **aynı** olmalıdır. Bunu testlerdeki tutarlılık kontrolü denetler; menüde olmayan bir kod eklerseniz test hata verir.

Bir SIDC kodu tabloda tam olarak yoksa üst seviyeye düşülür (ör. `120206` → `120200`).

## Testler

```bash
python -m unittest discover -s tests
```

Testler şunları kapsar: dönüşüm kuralları, Link 16 ↔ SIDC gidiş-dönüş tutarlılığı, Link 16 tablolarının SIDC menüsüyle uyumu ve üretilen CSV satırlarının dönüştürücüyle birebir aynı olması.

## Bilinen sınırlamalar

- **Link 16 harf kodları doğrulanmamıştır.** Kod yorumlarında atıf yapılan `env.txt` kaynağı projede yoktur.
- **2525D çizimi:** milsymbol 0.2.0 30 haneli 2525E kodlarını tanımadığı için sembol 20 haneli 2525D biçimine düşülerek çizilir. Durum satırında "2525D Uyumluluk" olarak görünür.
- **Kapsam:** Link 16 tablosu yalnızca yaygın platformları içerir. Space için yalnızca genel `SV OR` kodu vardır.
- **Tabloda olmayan kodlar:** Çözümlenen SIDC menüde olmayan bir kod içerirse menüye geçici olarak `(Tabloda yok)` seçeneği eklenir ve SIDC değişmeden korunur.

## Sorun giderme

**`No module named 'milsymbol'` veya `pip` çalışmıyor:** Sistem Python'u güncellendiyse (ör. 3.12 → 3.14) sanal ortam bozulur. Ortamı yeniden oluşturun:

```bash
rm -rf .env
python3 -m venv .env
.env/bin/pip install -r requirements.txt
```

VS Code'da ardından `Ctrl+Shift+P` → **Python: Select Interpreter** → `.env/bin/python` seçin.

**Önizleme yerine "cairosvg + Pillow gerekli" yazıyor:** `libcairo2` sistem paketinin kurulu olduğundan emin olun.
