# 🤖 YouTube Notify Bot

Telegram bot: YouTube kanallarida yangi video chiqqanda foydalanuvchilarga Gemini AI tahlili bilan xabar yuboradi.

## 📁 Fayl tuzilishi

```
youtube-notify-bot/
├── main.py          # Asosiy kirish nuqtasi (Flask + Bot + Monitor)
├── bot.py           # Telegram bot logikasi
├── monitor.py       # YouTube kanallarni kuzatish
├── gemini_ai.py     # Gemini AI mazmun tahlili
├── database.py      # JSON orqali ma'lumotlar
├── config.py        # Sozlamalar
├── requirements.txt # Kutubxonalar
├── render.yaml      # Render deploy konfiguratsiyasi
└── data/            # Ma'lumotlar (channels.json, subscribers.json, last_video.json)
```

## 🚀 Render ga deploy qilish

### 1. GitHub ga yuklash
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/sizning-username/youtube-notify-bot.git
git push -u origin main
```

### 2. Render da sozlash
1. [render.com](https://render.com) ga kiring → **New Web Service**
2. GitHub repo ni ulang
3. **Environment Variables** ga kiriting:
   - `BOT_TOKEN` = `9055967885:AAH...`
   - `ADMIN_ID` = `9214461706`
   - `GEMINI_API_KEY` = `AIzaSy...`
4. **Deploy** tugmasini bosing ✅

## 🔄 Doim ishlab turishi uchun (UptimeRobot)

1. [uptimerobot.com](https://uptimerobot.com) ga bepul ro'yxatdan o'ting
2. **New Monitor** → HTTP(s)
3. URL: `https://your-app.onrender.com/ping`
4. Interval: **5 daqiqa**

Bu orqali Render app 5 daqiqada bir marta uyg'otiladi va bot to'xtamaydi.

## 📱 Bot buyruqlari

| Buyruq | Kim uchun | Tavsif |
|--------|-----------|--------|
| `/start` | Hammaga | Obuna bo'lish |
| `/unsubscribe` | Hammaga | Obunani bekor qilish |
| `/admin` | Faqat admin | Admin panel |

## ⚙️ Admin panel imkoniyatlari
- 📋 Kanallar ro'yxatini ko'rish
- ➕ Yangi kanal qo'shish
- 🗑️ Kanal o'chirish
- 👥 Obunachlar sonini ko'rish
- 📣 Barcha obunachilarga xabar yuborish
