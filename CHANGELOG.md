# Changelog

Bu proje [Keep a Changelog](https://keepachangelog.com/) formatını ve [Semantic Versioning](https://semver.org/) kurallarını takip eder.

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
