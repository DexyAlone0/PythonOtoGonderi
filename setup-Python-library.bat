@echo off
echo Python 3.12 kütüphaneleri yükleniyor...

:: Python 3.12'nin yüklenip yüklenmediğini kontrol edin
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 3.12 bulunamadı. Lütfen Python 3.12'yi yükleyin.
    pause
    exit /b
)

:: Python paketlerini yükleyin
python -m pip install --upgrade pip
python -m pip install pandas instagrapi selenium

:: Selenium için Chrome WebDriver'ı indirip kurmanız gerekebilir.
:: WebDriver'in zaten PATH içinde olduğunu varsayıyoruz. Eğer değilse, manuel olarak indirip PATH'e eklemeniz gerekebilir.

echo Kütüphaneler başarıyla yüklendi.
pause
