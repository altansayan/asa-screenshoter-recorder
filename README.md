# ASA-AI Screenshot & Video Tool

> [!WARNING]
> **Sistem Gereksinimi:** Bu araç; Pano (Clipboard) yönetimi, Mutex (Single Instance) ve DPI API'leri doğrudan Windows'un çekirdek kütüphanelerine (Win32) bağlı olduğu için **sadece Windows işletim sistemlerinde** çalışmak üzere tasarlanmıştır. macOS veya Linux'ta çalışmaz.

Bu proje, ASA Intelligence ekosistemi için tasarlanmış yüksek performanslı, arka planda çalışan ve global kısayollarla (Shift+Alt) tetiklenen bir ekran kaydetme (görüntü & video) ve pano (clipboard) otomasyon aracıdır.

## 🚀 Özellikler

- **Hızlı Ekran Görüntüsü (Screenshot):** İstenilen bir ekran bölgesini seçerek yüksek kalitede anında PNG olarak kaydeder.
- **Yüksek Kalite Video Kaydı:** Ekranın sadece belirlediğiniz bir alanını, orijinal çözünürlük oranlarını bozmadan (720p/1080p uyumlu), MP4 formatında saniyede 20 kare (FPS) hızında video olarak çeker.
- **Akıllı Pano (Clipboard) Yönetimi:** Kaydedilen fotoğraf veya videoları hem *dosya (CF_HDROP)* hem de *metin/bağlantı (CF_UNICODETEXT)* olarak panoya kopyalar. Böylece Paint'e veya Word'e `Ctrl+V` yaparsanız dosyayı, VS Code'a yapıştırırsanız dosyanın klasör yolunu elde edersiniz. Telegram, WhatsApp gibi platformlara da doğrudan dosya aktarımı yapar.
- **Single Instance (Tekil Çalışma):** Windows Mutex mekanizması sayesinde sistemde aynı anda sadece tek bir uygulamanın çalışmasına izin verilir. Bu da kaynak israfını ve kısayol çakışmalarını önler.
- **DPI Farkındalığı:** Windows'un ekran ölçeklendirmelerinden (Örn: %125 veya %150) etkilenmez; seçimleri orijinal fiziksel pikseller üzerinden hatasız kaydeder.

## 🛠 Bağımlılıklar (Dependencies)

Sistemin düzgün çalışabilmesi için aşağıdaki kütüphaneler gereklidir. Kurmak için `pip install -r requirements.txt` komutunu veya aşağıdaki komutu kullanabilirsiniz:
`pip install pillow pyperclip keyboard pywin32 mss opencv-python numpy`

### Bağımlılıkların İşlevleri:
1. **`Pillow (PIL)`**: Ekran görüntülerini (screenshot) yakalamak ve hafızada formatlarını dönüştürmek (örneğin PNG'den BMP/DIB'e çevirmek) için kullanılır.
2. **`keyboard`**: İşletim sistemi seviyesinde (global) tuş dinleyicisidir. Hangi uygulamada olursanız olun (oyun, tarayıcı vb.) arka planda bekler ve `Shift + Alt` gibi kısayolların tetiklenmesini sağlar.
3. **`pywin32 (win32clipboard, win32event vb.)`**: Windows'un en alt seviye API'lerine (C kütüphanelerine) Python'dan erişmemizi sağlar. 
   - *Clipboard Yönetimi:* Resim piksellerini (`CF_DIB`) ve video/resim dosya nesnelerini (`CF_HDROP`) panoya kopyalamak için kullanılır. 
   - *Mutex:* Programın ikinci kez çalışmasını engelleyen "Single Instance Lock" yapısını kurar.
4. **`mss`**: Python'daki en hızlı ekran yakalama kütüphanesidir. Saniyede onlarca kare yakalayabildiği için video kaydı sırasında ekranın seçili bölümünü yüksek hızda (sıfır gecikmeyle) kopyalamak için kullanılır.
5. **`opencv-python (cv2)`**: `mss` ile çekilen fotoğrafları peş peşe birleştirerek MP4 kodekli (`mp4v`) bir video dosyasına dönüştürür.
6. **`numpy`**: `mss`'den alınan ham ekran piksellerini (Raw veriyi) `opencv-python`'un anlayabileceği "matris (matrix)" yapısına çevirir.
7. **`pyperclip`**: Sadece düz metin kopyalama işlemlerinde, Windows API hata verirse "Fallback (Yedek)" sistem olarak çalışarak dosya yolunu panoya metin olarak yapıştırır.

## 🕹 Kullanım

1. Terminalde klasör dizinine gidip aracı çalıştırın: `python screenshot_tool.py`
2. **Fotoğraf Çekmek İçin:** İstediğiniz zaman klavyeden `Shift + Alt` tuşlarına aynı anda basın. Ekran hafifçe kararacak, farenizle istediğiniz alanı seçip bırakın.
3. **Video Çekmek İçin:** `Shift + Alt` yaptıktan sonra klavyeden `R` veya `r` tuşuna basın. Seçim ekranı hafif kırmızımsı bir renge döner. Farenizle bölge seçtiğinizde kayıt otomatik başlar.
4. **Kaydı Durdurmak İçin:** Video kaydı başladığında ekranın sağ alt köşesinde çıkan kırmızı **⏹ KAYDI DURDUR** butonuna tıklayın veya `ESC` tuşuna basın.

> **NOT:** Araç, Windows başlangıcında otomatik çalışması için `Startup` klasörüne atılan bir `.vbs` betiği üzerinden yönetilebilir.
