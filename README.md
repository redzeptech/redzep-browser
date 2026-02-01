# Redzep Browser

PyQt6 + QtWebEngine ile geliştirilmiş sekmeli mini masaüstü web tarayıcı.

## Özellikler
- Sekmeler (Ctrl+T yeni sekme, Ctrl+W sekme kapat)
- Adres çubuğu + Geri/İleri/Yenile/Home
- Yer imleri: ekle, menüden aç
- Yer imi yönetimi: tek tek sil, tümünü temizle
- 🛡 Secure Mode: JavaScript Aç/Kapat (status bar bildirimleri)

## Kurulum (Windows)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
