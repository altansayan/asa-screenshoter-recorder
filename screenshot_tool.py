"""
ASA-AI Screenshot & Video Tool
Developer: Altan Sezer Ayan

Bu kod, ASA Intelligence otomasyon sistemleri kapsamında 
arka planda ekran görüntüsü ve yüksek kalite MP4 video yakalamak için geliştirilmiştir.
"""

import tkinter as tk
from PIL import ImageGrab
import pyperclip
import keyboard
import os
import win32clipboard
from io import BytesIO
from datetime import datetime
import time
import sys
import threading
import ctypes
from ctypes import wintypes
import cv2
import mss
import numpy as np
import win32event
import win32api
import winerror
import winreg
import locale

class DROPFILES(ctypes.Structure):
    """
    Windows Clipboard API'sinde HDROP (dosya kopyalama) formatı için gereken C bellek yapısıdır.
    Panoya (clipboard) metin yerine gerçek bir dosya nesnesi eklemek için kullanılır.
    """
    _fields_ = [('pFiles', wintypes.DWORD),
                ('pt', wintypes.POINT),
                ('fNC', wintypes.BOOL),
                ('fWide', wintypes.BOOL)]

def copy_file_to_clipboard(filepath):
    """
    Verilen dosya yolundaki (filepath) dosyayı Windows panosuna kopyalar.
    Hem metin (dosyanın bilgisayardaki konumu) hem de CF_HDROP (fiziksel dosya) formatında panoya veri ekler.
    Bu sayede Word, Excel veya WhatsApp'a doğrudan yapıştırıldığında dosya algılanır.
    
    Args:
        filepath (str): Kopyalanacak dosyanın mutlak yolu (absolute path).
    Returns:
        bool: İşlem başarılıysa True, aksi halde False.
    """
    try:
        # C bellek yapılandırması (Memory Allocation)
        offset = ctypes.sizeof(DROPFILES)
        length = len(filepath) + 1
        size = offset + (length + 1) * ctypes.sizeof(ctypes.c_wchar)
        
        buf = (ctypes.c_char * size)()
        df = DROPFILES.from_buffer(buf)
        df.pFiles, df.fWide = offset, True
        
        # Dosya yolunu C buffer'ına yaz
        ctypes.memmove(ctypes.addressof(buf) + offset, 
                       filepath.encode('utf-16le'), 
                       length * ctypes.sizeof(ctypes.c_wchar))
                       
        # Windows Panosunu kilitle, temizle ve yeni veriyi koy
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, bytes(buf)) # Dosya nesnesi olarak
        win32clipboard.SetClipboardText(filepath, win32clipboard.CF_UNICODETEXT) # Düz metin (URL) olarak
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"[HATA] Dosya panoya kopyalanamadi: {e}")
        return False

class ScreenshotApp:
    """
    Ekran kaydı (resim veya video) yapmak için gerekli arayüz ve mantığı barındıran ana sınıf.
    """
    def __init__(self):
        """
        Sınıf başlatıldığında Windows çözünürlük ayarlarını (DPI) sisteme göre ayarlar 
        ve gerekli değişkenleri (koordinatlar, UI nesneleri) başlatır.
        """
        # Windows DPI ayarlarından etkilenmemek (Görüntü bulanıklığını/kalite düşüşünü önlemek) için
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass
            
        self.root = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.size_text = None
        self.canvas = None
        self.record_mode = False
        self.stop_event = threading.Event()
        self.record_thread = None
        
        # Ekran görüntüleri ve videoları kaydedeceğimiz klasör yolu oluşturulur
        self.save_dir = os.path.expanduser("~\\Pictures\\Screenshots")
        os.makedirs(self.save_dir, exist_ok=True)
        
    def start_capture(self):
        """
        Shift+Alt tuşlarına basıldığında çağrılır. 
        Tüm ekranı kaplayan, şeffaf bir 'tkinter' penceresi (canvas) açar.
        Kullanıcı fareyle çizim yaparken bu ekran üzerinden koordinatlar alınır.
        """
        self.record_mode = False
        self.root = tk.Tk()
        
        # Ekran ayarları (Tam ekran, %30 saydam, en üstte)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(background='black')
        self.root.config(cursor="cross")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Olay dinleyicileri (Fare tıklama, sürükleme ve bırakma eylemleri)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # R tuşuna basınca video moduna geç (Dil ve CapsLock'tan bagimsiz global klavye kontrolü)
        self.root.bind("<Key>", self.check_key_press)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # Ekranda sol üstteki bilgilendirme metni
        self.info_text = self.canvas.create_text(
            10, 10, anchor="nw", 
            text="Resim Secimi Icin Farenizi Surukleyin. Video kaydetmek icin 'R' tusuna basin. Iptal icin ESC.", 
            fill="white", font=("Arial", 14, "bold")
        )
        
        self.root.focus_force()
        self.root.mainloop()

    def check_key_press(self, event):
        """
        Tkinter açıkken basılan tüm tuşları yakalar. 
        Klavye dili İngilizce veya Türkçe olsa da, Caps Lock açık veya kapalı olsa da 
        'R' harfini doğru algılayabilmek için güvenli bir metottur.
        """
        if hasattr(event, 'char') and event.char:
            if event.char.lower() == 'r' or event.char.lower() == 'R':
                self.toggle_record_mode(event)

    def toggle_record_mode(self, event):
        """
        Video Modu (Kayıt) ile Fotoğraf Modu (Ekran görüntüsü) arasında geçiş yapar.
        Arayüzün arka plan rengini kırmızı/siyah arasında değiştirerek kullanıcıyı bilgilendirir.
        """
        self.record_mode = not self.record_mode
        if self.record_mode:
            self.root.attributes("-alpha", 0.4)
            self.canvas.configure(bg="#400000") # Hafif kırmızı arkaplan
            self.canvas.itemconfig(self.info_text, text="🎥 VIDEO MODU: Kayit edilecek alani secin. Kapatmak icin 'R'", fill="yellow")
        else:
            self.root.attributes("-alpha", 0.3)
            self.canvas.configure(bg="black")
            self.canvas.itemconfig(self.info_text, text="Resim Secimi Icin Farenizi Surukleyin. Video kaydetmek icin 'R' tusuna basin.", fill="white")

    def on_button_press(self, event):
        """
        Fare sol tuşuna tıklandığında seçimin (karenin) başlangıç (X,Y) koordinatlarını kaydeder.
        """
        self.start_x = event.x
        self.start_y = event.y
        color = 'yellow' if self.record_mode else 'red'
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, 1, 1, 
            outline=color, width=2, fill="white"
        )
        
        # Boyut ölçülerini (WxH) göstereceğimiz dinamik metin nesnesini farenin yanına oluşturuyoruz
        self.size_text = self.canvas.create_text(
            event.x + 15, event.y + 15, 
            text="0 x 0", fill=color, font=("Arial", 12, "bold"), anchor="nw"
        )

    def on_move_press(self, event):
        """
        Fare basılı tutup sürüklendiğinde çizilen dikdörtgenin (rect) boyutunu günceller.
        Ayrıca farenin (+ imlecinin) yanında canlı olarak seçili alanın piksel ölçülerini gösterir.
        """
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        
        # Seçili alanın genişlik ve yüksekliğini hesapla
        w = abs(cur_x - self.start_x)
        h = abs(cur_y - self.start_y)
        
        # Metni güncelle ve farenin hareketine göre sağ/alt çapraza konumlandır
        self.canvas.itemconfig(self.size_text, text=f"{w} x {h}")
        self.canvas.coords(self.size_text, cur_x + 15, cur_y + 15)

    def on_button_release(self, event):
        """
        Fare sol tuşu bırakıldığında seçimi tamamlar.
        Seçilen alanın min/max koordinatlarını (bbox) hesaplar ve şeffaf pencereyi kapatır.
        Hangi modda (Video/Resim) olduğunu kontrol edip ilgili fonksiyonu tetikler.
        """
        end_x, end_y = (event.x, event.y)
        self.root.destroy()
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        # Çok ufak/yanlış tıklamaları filtrele (en az 10 piksellik bir alan olmalı)
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            time.sleep(0.2) # Arayüzün kapanması için çok kısa bir bekleme süresi
            if self.record_mode:
                self.start_video_recording(x1, y1, x2, y2)
            else:
                self.capture_and_save_image(x1, y1, x2, y2)

    def capture_and_save_image(self, x1, y1, x2, y2):
        """
        Seçili koordinatlar (bbox) içerisindeki piksellerin anlık bir fotoğrafını (PNG) çeker.
        Fotoğrafı sabit diske kaydeder ve ardından panoya (clipboard) kopyalar.
        """
        bbox = (x1, y1, x2, y2)
        img = ImageGrab.grab(bbox) # Pillow (PIL) ile ekran yakalama
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.save_dir, filename)
        img.save(filepath)
        
        # Fotoğraf piksellerini panoya koyabilmek için DIB (BMP pikselleri) formatına çevir
        output = BytesIO()
        img.convert("RGB").save(output, "BMP")
        dib_data = output.getvalue()[14:]
        output.close()
        
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(filepath, win32clipboard.CF_UNICODETEXT) # Dosya yolu
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, dib_data) # Resim verisi
            win32clipboard.CloseClipboard()
            print(f"\n[BASARILI] Görüntü kaydedildi: {filepath}")
        except Exception as e:
            print(f"\n[HATA] Resim Clipboard kopyalama başarisiz: {e}")
            pyperclip.copy(filepath)

    def start_video_recording(self, x1, y1, x2, y2):
        """
        Seçilen alanın (x1,y1'den x2,y2'ye) kesintisiz videosunu kaydetmeye başlar.
        Kayıt işleminin arayüzü kilitlememesi için ayrı bir iş parçacığı (Thread) oluşturur.
        """
        self.stop_event.clear()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        filepath = os.path.join(self.save_dir, filename)
        
        w = x2 - x1
        h = y2 - y1
        
        # mp4v codec'i tek sayılarda (odd numbers) bozulabilir, bu sebeple her zaman çift sayı (even) yapıyoruz
        w = w if w % 2 == 0 else w + 1
        h = h if h % 2 == 0 else h + 1
        
        # OpenCV (cv2) Video Kaydedici nesnesi oluşturuluyor
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 25.0
        out = cv2.VideoWriter(filepath, fourcc, fps, (w, h))
        
        def record():
            """
            Arka planda (Thread içinde) çalışan asıl video kayıt döngüsüdür.
            mss kütüphanesi saniyede ~20 kare yakalar ve OpenCV bu kareleri peş peşe yazar.
            """
            print(f"\n[KAYIT] Video kaydi basladi ({w}x{h})...")
            with mss.MSS() as sct:
                monitor = {"top": y1, "left": x1, "width": w, "height": h}
                # Kullanıcı durdurma butonuna basana kadar sonsuz döngüde çalışır
                while not self.stop_event.is_set():
                    start_time = time.time()
                    
                    # Ekrani yakala (Çok hızlıdır)
                    img = sct.grab(monitor)
                    frame = np.array(img)
                    
                    # mss'den gelen pikseller BGRA formatındadır, OpenCV MP4 için BGR bekler, çeviriyoruz:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
                    
                    # Çekilen videonun aşırı hızlanmaması veya yavaşlamaması için FPS'yi (25.0) sabitliyoruz
                    elapsed = time.time() - start_time
                    time_to_sleep = max(1.0/fps - elapsed, 0)
                    time.sleep(time_to_sleep)
                    
            # Döngü bittiğinde video dosyasını kapat ve kaydet
            out.release()
            print(f"[BASARILI] Video kaydedildi: {filepath}")
            
            # Videoyu panoya (CF_HDROP dosyasi olarak) kopyala
            success = copy_file_to_clipboard(filepath)
            if not success:
                pyperclip.copy(filepath) # Hata olursa metin olarak kopyalar
            print("[BILGI] Video dosyasi panoya kopyalandi!")

        # Kayıt thread'ini başlat
        self.record_thread = threading.Thread(target=record)
        self.record_thread.start()
        
        # Kaydı durdurma butonunu ekrana getir
        self.show_stop_button()

    def show_stop_button(self):
        """
        Kayıt başladığında sağ alt köşede yüzen (floating), taşınamaz, ufak bir kırmızı buton çıkarır.
        """
        self.stop_root = tk.Tk()
        self.stop_root.title("Stop")
        
        # Ekranın tam sag alt kosesine sabitlemek icin Tkinter negatif kordinatlarini kullanırız
        # (-10: sağ köşeden 10px boşluk, -50: alt köşeden 50px boşluk)
        self.stop_root.geometry("150x50-10-50")
        
        self.stop_root.attributes("-topmost", True) # Her zaman pencerelerin en üstünde kalır
        self.stop_root.overrideredirect(True) # Windows pencere kenarlıklarını (Kapat, Küçült butonları) gizler
        self.stop_root.configure(bg="black")
        
        # Ekran/UI gorunmese bile kullanıcı paniklerse ESC ile kapatabilmesi için yedek kısayol (fallback)
        self.stop_root.bind("<Escape>", lambda e: self.stop_recording())
        
        btn = tk.Button(
            self.stop_root, text="⏹ STOP", 
            bg="red", fg="white", font=("Arial", 10, "bold"),
            command=self.stop_recording
        )
        btn.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.stop_root.mainloop()

    def stop_recording(self):
        """
        Kullanıcı 'Durdur' butonuna bastığında çağrılır.
        Kayıt döngüsünü (Thread) durdurur, pencereyi kapatır ve sistemin belleğini temizler.
        """
        self.stop_event.set() # Thread döngüsünü kırar
        if self.record_thread:
            self.record_thread.join() # Thread'in işini sağ salim bitirmesini bekler
        self.stop_root.destroy() # Kırmızı butonu yok eder

def add_to_startup():
    """
    Eğer uygulama (.exe) olarak çalışıyorsa, kendisini Windows başlangıcına (Registry) otomatik ekler.
    """
    if getattr(sys, 'frozen', False): # Sadece PyInstaller ile EXE yapıldığında tetiklenir
        app_path = sys.executable
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            # Yolu tırnak içine alarak ekle
            winreg.SetValueEx(key, "ASA_Screenshot_Tool", 0, winreg.REG_SZ, f'"{app_path}"')
            winreg.CloseKey(key)
        except Exception as e:
            print(f"[HATA] Registry baslangicina eklenirken sorun olustu: {e}")

def show_splash_screen(already_running=False):
    """
    Kullanıcıya programın başladığını veya zaten çalıştığını bildiren zarif,
    otomatik dil tanımalı (TR/EN) geçici açılış ekranıdır.
    """
    try:
        lang = locale.getdefaultlocale()[0]
        is_turkish = lang and lang.startswith('tr')
    except Exception:
        is_turkish = False
        
    splash = tk.Tk()
    splash.overrideredirect(True) # Çerçevesiz (Kapatma tuşu vs. yok)
    splash.attributes('-topmost', True) # Hep en üstte
    splash.configure(bg='#2d3436') # Havalı koyu gri arka plan
    
    # Ekranın tam ortasına yerleştir
    w = 480
    h = 160
    ws = splash.winfo_screenwidth()
    hs = splash.winfo_screenheight()
    x = int((ws/2) - (w/2))
    y = int((hs/2) - (h/2))
    splash.geometry(f'{w}x{h}+{x}+{y}')
    
    title_lbl = tk.Label(splash, text="ASA Screenshot & Screen Video Recorder Tool", font=('Segoe UI', 12, 'bold'), bg='#2d3436', fg='#0984e3')
    title_lbl.pack(pady=(20, 10))
    
    status_lbl = tk.Label(splash, font=('Segoe UI', 10), bg='#2d3436', fg='#dfe6e9')
    status_lbl.pack(pady=5)
    
    copy_lbl = tk.Label(splash, text="Copyright © 2026 Altan Sezer Ayan", font=('Segoe UI', 8), bg='#2d3436', fg='#636e72')
    copy_lbl.pack(side='bottom', pady=10)

    if already_running:
        if is_turkish:
            status_lbl.config(text="Uygulama zaten arka planda çalışıyor!")
        else:
            status_lbl.config(text="Application is already running in the background!")
        
        # 2 saniye göster ve kapan
        splash.after(2000, splash.destroy)
        splash.mainloop()
    else:
        if is_turkish:
            status_lbl.config(text="Başlatılıyor...")
            ready_text = "Tamamlandı! (Shift+Alt ile kullanabilirsiniz)"
        else:
            status_lbl.config(text="Starting...")
            ready_text = "Ready! (You can use the Shift+Alt shortcut)"
            
        def show_ready():
            status_lbl.config(text=ready_text, fg='#00b894') # Yeşile döner
            splash.after(2500, splash.destroy) # 2.5s sonra kapat
            
        # 1 saniye başlatılıyor yazısı kalsın, sonra hazır ekranını göster
        splash.after(1000, show_ready) 
        splash.mainloop()

def main():
    """
    Programın ana yürütme noktasıdır.
    Mutex kontrolünü yapar, ekrana bilgileri yazar ve sistem dinlemeye başlar.
    """
    # Sadece TEK BIR uygulamanin calismasini garantiye al (Single Instance Lock / Mutex)
    # Eğer ikinci bir python penceresinden bu kod başlatılırsa, ilk olan ezilmemesi için ikinci kapanır.
    mutex = win32event.CreateMutex(None, False, "ASA_Screenshot_Video_Tool_Mutex_Lock")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        print("[BILGI] Uygulama zaten calisiyor. Ikinci kopya kapatiliyor.")
        show_splash_screen(already_running=True)
        return
        
    # Exe modundaysa başlangıca otomatik kayıt ol
    add_to_startup()
    
    # Başlangıç splash ekranını göster
    show_splash_screen(already_running=False)
    
    app = ScreenshotApp()
    
    print("=====================================================")
    print(" ASA Screenshot & Video Araci Baslatildi!")
    print(" Kısayol: Secim baslatmak icin 'Shift + Alt' tuslarina basin.")
    print(" Video Modu: Secim ekranindayken 'R' tusuna basin.")
    print(" Cikis: Bu pencereyi kapatin veya 'Ctrl+C' yapin.")
    print("=====================================================")
    
    app = ScreenshotApp()
    
    # Global klavye (işletim sistemi) hook'u kurarak Shift+Alt dinlemeye başlar
    while True:
        try:
            keyboard.wait('shift+alt') # Ana program döngüsünü dondurup bu tuşu bekler
            app.start_capture()
        except KeyboardInterrupt:
            # Kullanıcı terminalde Ctrl+C yaparsa program temiz kapanır
            print("\nCikis yapiliyor...")
            sys.exit(0)
        except Exception as e:
            print(f"\n[HATA] Bir sorun olustu: {e}")

if __name__ == "__main__":
    main()
