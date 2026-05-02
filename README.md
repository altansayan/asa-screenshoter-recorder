# ASA Screenshot & Video Tool

*( [🇬🇧 Go to English Version](#english-version) | [🇹🇷 Türkçe Okumaya Devam Et](#turkish-version) )*

---

<a id="turkish-version"></a>
## 🇹🇷 ASA Screenshot & Video Tool (Türkçe)

> [!WARNING]
> **Sistem Gereksinimi:** Bu araç; Pano (Clipboard) yönetimi, Mutex (Single Instance) ve DPI API'leri doğrudan Windows'un çekirdek kütüphanelerine (Win32) bağlı olduğu için **sadece Windows işletim sistemlerinde** çalışmak üzere tasarlanmıştır. macOS veya Linux'ta çalışmaz.

> [!TIP]
> ⚡ **Yapay Zeka (AI) ve Terminal (CLI) Araçları İçin Üretildi!** Kaydedilen görsellerin dosya yolları anında panoya düşer. Terminalinize veya yapay zeka asistanınıza saniyeler içinde yapıştırın ve geliştirme hızınızı (workflow) ikiye katlayın! Sadece (Ctrl+V)

Bu proje, ASA Intelligence ekosistemi için tasarlanmış yüksek performanslı, arka planda çalışan ve global kısayollarla (Shift+Alt) tetiklenen bir ekran kaydetme (görüntü & video) ve pano (clipboard) otomasyon aracıdır.

### 🚀 Özellikler
- **Hızlı Ekran Görüntüsü (Screenshot):** İstenilen bir ekran bölgesini seçerek yüksek kalitede anında PNG olarak kaydeder.
- **Yüksek Kalite Video Kaydı:** Ekranın sadece belirlediğiniz bir alanını, orijinal çözünürlük oranlarını bozmadan (720p/1080p uyumlu), MP4 formatında saniyede 25 kare (FPS - Avrupa/Türkiye TV Standardı) hızında video olarak çeker.
- **Akıllı Pano (Clipboard) Yönetimi:** Kaydedilen fotoğraf veya videoları hem *dosya (CF_HDROP)* hem de *metin/bağlantı (CF_UNICODETEXT)* olarak panoya kopyalar.
- **Single Instance (Tekil Çalışma):** Windows Mutex mekanizması sayesinde sistemde aynı anda sadece tek bir uygulamanın çalışmasına izin verilir.
- **DPI Farkındalığı:** Windows'un ekran ölçeklendirmelerinden etkilenmez; seçimleri orijinal fiziksel pikseller üzerinden kaydeder.

### 🛠 Kurulum ve Bağımlılıklar
Sistemin düzgün çalışabilmesi için öncelikle bilgisayarınızda **Python 3.x** ve **pip** paket yöneticisinin yüklü olması gerekir. 
*Eğer yüklü değilse:* [Python.org](https://www.python.org/downloads/windows/) adresinden Python'u indirin ve kurulum ekranındaki **"Add python.exe to PATH"** kutucuğunu **kesinlikle işaretleyin**. Bu adım, `pip` komutunun terminalde tanınmasını sağlar.

Ardından gerekli kütüphaneleri kurmak için terminalde (CMD veya PowerShell) aşağıdaki komutu çalıştırın:
```bash
pip install pillow pyperclip keyboard pywin32 mss opencv-python numpy
```

**Bağımlılıkların İşlevleri:**
1. **Pillow (PIL)**: Ekran görüntülerini yakalamak ve formatlarını dönüştürmek için.
2. **keyboard**: Arka planda klavye kısayollarını (`Shift+Alt`) dinlemek için.
3. **pywin32**: Windows API erişimi (Pano yönetimi ve Mutex kilitleri) için.
4. **mss**: Video kaydı için ekranı sıfır gecikmeyle (ultra hızlı) kopyalamak için.
5. **opencv-python**: Kareleri birleştirip MP4 formatında video kodlamak için.
6. **numpy**: Ham pikselleri OpenCV matrisine çevirmek için.
7. **pyperclip**: Pano işlemleri başarısız olursa dosya yolunu düz metin olarak kopyalamak için yedek (fallback) sistem.

### 🕹 Kullanım
1. Terminalde klasör dizinine gidip aracı çalıştırın: `python screenshot_tool.py`
2. **Fotoğraf Çekmek İçin:** Klavyeden `Shift + Alt` tuşlarına aynı anda basın. Alanı seçin.
3. **Video Çekmek İçin:** `Shift + Alt` yaptıktan sonra `R` tuşuna basın. Alanı seçtiğiniz an kayıt başlar.
4. **Kaydı Durdurmak İçin:** Ekranın sağ alt köşesinde çıkan **⏹ STOP** butonuna tıklayın veya `ESC` tuşuna basın.

### ⚙️ Windows Başlangıcında Otomatik Çalıştırma (VBScript)
Aracın siyah terminal penceresi görünmeden arka planda tamamen gizli (stealth) çalışması için bir VBScript oluşturabilirsiniz.
1. Bilgisayarınızda `asa_screenshot_tool.vbs` adında yeni bir metin dosyası oluşturun.
2. İçine şu kodları yapıştırın (Dosya yolunu kendi sisteminize göre düzenleyin):
```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\SeninAdin\repos\asa-screenshoter"
WshShell.Run "pythonw.exe screenshot_tool.py", 0, False
```
3. Klavyeden `Win + R` tuşlarına basıp açılan kutuya `shell:startup` yazın. Açılan Başlangıç (Startup) klasörünün içine bu `.vbs` dosyasını atın. Artık bilgisayarınız her açıldığında araç arka planda hazır olacaktır.

### 🛠️ Özelleştirme Ayarları (Ayarları Değiştirme)
Uygulamanın varsayılan ayarlarını (FPS ve Kayıt Yeri) kendi isteğinize göre `screenshot_tool.py` dosyasından kolayca değiştirebilirsiniz:
- **Dosyaların Kaydedileceği Klasör:** Satır `88` civarındaki `self.save_dir = os.path.expanduser("~\\Pictures\\Screenshots")` kodunu bularak istediğiniz bir klasör yolunu (Örn: `C:\\Kayıtlar`) yazabilirsiniz.
- **Video FPS Ayarı:** Satır `275` civarındaki `fps = 25.0` değerini `30.0` (TV) veya `60.0` (Oyun akıcılığı) olarak değiştirebilirsiniz.

### 👨‍💻 Geliştirici
**Developer:** Altan Sezer Ayan
*Bu araç, ASA Intelligence yapay zeka ve otomasyon sistemleri kapsamında geliştirilmiştir.*

---

<a id="english-version"></a>
## 🇬🇧 ASA Screenshot & Video Tool (English)

> [!WARNING]
> **System Requirement:** This tool is designed **exclusively for Windows**. It relies heavily on Windows core libraries (Win32 API) for Clipboard management (CF_HDROP), Mutex (Single Instance), and DPI awareness. It will not work on macOS or Linux.

> [!TIP]
> ⚡ **Built for Artificial Intelligence (AI) and Terminal (CLI) Tools!** Captured image paths land instantly in your clipboard. Paste them into your terminal or AI assistant in seconds and double your development speed (workflow)! Just (Ctrl+V)

This project is a high-performance, background-running screen capture and video recording automation tool triggered by global hotkeys (Shift+Alt), developed for the ASA Intelligence ecosystem.

### 🚀 Features
- **Instant Screenshots:** Select any screen region and save it instantly as a high-quality PNG.
- **High-Quality Video Recording:** Record a specific screen region in MP4 format at 25 FPS (European/PAL TV Standard) without stretching or losing the original aspect ratio.
- **Smart Dual-Clipboard Integration:** Copies captured photos or videos to the clipboard simultaneously as both a *File Object (CF_HDROP)* and *Text/Path (CF_UNICODETEXT)*.
- **Single Instance Lock:** Uses Windows Mutex to guarantee that only one instance of the application runs at any given time.
- **DPI Awareness:** Immune to Windows display scaling issues; it precisely maps logical coordinates to physical pixels.

### 🛠 Installation and Dependencies
For the system to work properly, you must first have **Python 3.x** and the **pip** package manager installed.
*If you don't have them:* Download Python from [Python.org](https://www.python.org/downloads/windows/) and **make sure to check the "Add python.exe to PATH"** box during installation. This step is crucial for your terminal to recognize the `pip` command.

Then, to install the required libraries, open your terminal (CMD or PowerShell) and run:
```bash
pip install pillow pyperclip keyboard pywin32 mss opencv-python numpy
```

**What do these dependencies do?**
1. **Pillow (PIL)**: Captures images and converts pixel formats.
2. **keyboard**: Listens to global keyboard shortcuts (`Shift+Alt`) in the background.
3. **pywin32**: Provides low-level Windows API access for robust clipboard manipulation and Mutex locks.
4. **mss**: An ultra-fast, zero-latency screen capture library used to grab frames for video recording.
5. **opencv-python**: Encodes the captured frames into an MP4 video file.
6. **numpy**: Converts raw screen pixels into OpenCV matrix structures.
7. **pyperclip**: Serves as a fallback system to copy the file path as plain text if the Windows API fails.

### 🕹 Usage
1. Open a terminal in the project directory and run: `python screenshot_tool.py`
2. **Take a Screenshot:** Press `Shift + Alt`. Select a region using your mouse.
3. **Record a Video:** Press `Shift + Alt`, then press the `R` key. Select a region, and recording will start automatically.
4. **Stop Recording:** Click the red **⏹ STOP** button at the bottom right of your screen, or press `ESC`.

### ⚙️ Auto-Start on Windows Boot (VBScript)
To run this tool completely hidden in the background every time Windows starts, you can create a VBScript.
1. Create a file named `asa_screenshot_tool.vbs`.
2. Paste the following code inside (Update the directory path according to your system):
```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\YourName\repos\asa-screenshoter"
WshShell.Run "pythonw.exe screenshot_tool.py", 0, False
```
3. Press `Win + R`, type `shell:startup`, and press Enter. Move the `.vbs` file into this Startup folder. The tool will now start automatically in stealth mode on every boot.

### 🛠️ Customization (Changing Settings)
You can easily change the default settings (FPS and Save Directory) directly inside the `screenshot_tool.py` file:
- **Save Directory:** Locate line `88` approx. `self.save_dir = os.path.expanduser("~\\Pictures\\Screenshots")` and change it to any absolute path (e.g., `C:\\Records`).
- **Video FPS Rate:** Locate line `275` approx. `fps = 25.0` and change the value to `30.0` or `60.0` depending on your required smoothness.

### 👨‍💻 Developer
**Developer:** Altan Sezer Ayan
*Developed under the ASA Intelligence AI and automation systems.*
