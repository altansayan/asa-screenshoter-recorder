# Changelog

Bu proje [Keep a Changelog](https://keepachangelog.com/) formatını ve [Semantic Versioning](https://semver.org/) kurallarını takip eder.

## [1.3.1] - 2026-07-14

### Fixed
- Uygulama bazen açılışta `ImportError: cannot import name '_umath_linalg' from partially initialized module 'numpy.linalg'` hatasıyla çöküyordu. Kök neden: `.spec` dosyaları onefile modunda derleniyordu, yani numpy/opencv'nin tüm DLL'leri (~70 MB) her açılışta yeniden `%TEMP%\_MEIxxxxxx` klasörüne extract ediliyordu; bu tekrarlanan extract sırasında antivirüs taramasının dosyaları anlık kilitlemesi, Python'un derlenmiş `_umath_linalg` alt modülünü "yarım" görmesine yol açıyordu (aynı anda görülen "Failed to remove temporary directory" uyarısı da bunun kanıtıydı).
- **Not:** İlk aşamada `upx=True` ayarı şüpheli görülüp `upx=False` yapıldı, fakat bu makinede UPX zaten hiç kurulu değildi (etkisizdi) — asıl kök neden bu değildi.

### Changed
- `screenshot_tool.spec`, `screenshotandrecoder.spec` ve `asa_screen.spec` dosyaları **onefile'dan onedir moduna** geçirildi (`EXE(..., exclude_binaries=True)` + `COLLECT(...)`). DLL'ler artık build sırasında bir kez `dist/<isim>/` klasörüne yazılıyor, her açılışta yeniden extract edilmiyor — antivirüs yarış durumu tamamen ortadan kalktı. Dağıtım artık tek bir `.exe` değil, exe + `_internal/` klasörünü birlikte içeren bir dizin (`add_to_startup()` fonksiyonu `sys.executable` kullandığı için Windows başlangıç kaydı otomatik doğru yolu buluyor, kod değişikliği gerekmedi).

## [1.3.0] - 2026-07-11

### Changed
- **BREAKING:** Global kısayol `Shift+Alt`'tan **`Shift+Alt+S`**'ye değiştirildi.
- Kısayol mekanizması tamamen değişti: üçüncü parti `keyboard` kütüphanesi (ve onun 60 saniyelik yenileme watchdog'u) kaldırıldı, yerine Windows'un yerel `RegisterHotKey` API'si kullanıldı. Gerçek kullanım testinde kanıtlandı: `keyboard` kütüphanesinin low-level hook'u uyku/uyanma sonrası yeniden kurulsa bile gerçek tuş olaylarını almayı kesebiliyordu (kök neden buydu, watchdog'un tekrar kurması yeterli değildi). `RegisterHotKey`, işletim sistemi tarafından oturum seviyesinde yönetildiği için uyku/uyanma/güç kesintisi sonrası da güvenilir çalışıyor — gerçek kullanımda test edilip doğrulandı.
- Ana döngü artık `keyboard` kütüphanesi yerine doğrudan Windows mesaj döngüsü (`GetMessageW`/`WM_HOTKEY`/`WM_TIMER`) kullanıyor; günlük bakım kontrolü için 5 dakikalık `SetTimer` ile tetikleniyor.

### Removed
- Geçici teşhis (diagnostic) amacıyla eklenen log dosyası mekanizması kaldırıldı (kullanılmıyordu, gereksiz büyümesin diye).

## [1.2.0] - 2026-07-10

### Added
- Günlük kendini yeniden başlatma (self-restart) mekanizması: uygulama, en az bir gece yarısı (00:00) geçtikten sonra, video kaydı aktif değilken kendini tamamen kapatıp yeniden başlatır. Bu, haftalarca/aylarca hiç kapanmadan çalışan bir process'te üçüncü parti `keyboard` kütüphanesinin native hook döngüsünde zamanla oluşabilecek olası birikimleri günlük olarak sıfırlar.
- Ana döngü artık kısayola hiç basılmasa bile 5 dakikada bir periyodik olarak uyanıp tarih kontrolü yapabiliyor (`capture_event.wait(timeout=300)`).

## [1.1.0] - 2026-07-10

### Fixed
- Shift+Alt global kısayolunun bilgisayar uykuya girip çıktıktan (sleep/resume) sonra sessizce tepkisiz kalması düzeltildi. Kısayol artık 60 saniyede bir kendini yenileyen bir bekçi (watchdog) thread'i ile korunuyor.
- Seçim ekranındaki bilgilendirme metni artık ayrı, tam opak bir pencerede gösteriliyor. Önceki halinde ana pencerenin %30 saydamlığından etkilenip okunması zor hale geliyordu.
- `main()` içindeki tekrarlanan `ScreenshotApp()` satırı kaldırıldı.

### Changed
- Seçim ekranı metinleri düzgün Türkçe karakterlerle yeniden yazıldı ve "Resim" yerine "Ekran Görüntüsü" ifadesi kullanıldı.
- Çıkış kısayolu artık her iki modda da (fotoğraf ve video) "Çıkış İçin: 'Esc'" şeklinde, diğer tuş isimleriyle tutarlı tırnaklı biçimde gösteriliyor.

### Added
- Seçim ekranı metinleri artık splash ekranı gibi otomatik dil algılama (TR/EN) ile çalışıyor; İngilizce sistemlerde İngilizce metin gösteriliyor.

## [1.0.0] - 2026-05-02

### Added
- İlk sürüm: Shift+Alt ile tetiklenen ekran görüntüsü ve video kaydı aracı.
- Seçili alanın PNG olarak anlık ekran görüntüsünü alma.
- Seçili alanın 25 FPS MP4 video kaydı (kayıt sırasında 'R' tuşu ile mod geçişi).
- Pano (clipboard) entegrasyonu: dosya (CF_HDROP) ve metin/yol (CF_UNICODETEXT) olarak kopyalama.
- Windows Mutex ile tekil çalışma (single instance) garantisi.
- DPI farkındalığı.
- Windows başlangıcına otomatik kayıt (registry).
- Çok dilli (TR/EN) açılış (splash) ekranı.
- PyInstaller ile tek dosyalık `.exe` derleme desteği.
