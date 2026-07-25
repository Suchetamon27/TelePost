# TelePost
<p align="center">
  <img src="img/banner.png" alt="TelePost banner" width="800">
</p>

<p align="center">
  <b>Post to Telegram channels and groups directly from your terminal — fast, secure, and developer friendly.</b>
</p>

<h1 align="center">TelePost — Telegram Terminal Poster</h1>

<p align="center">
  <b>Terminal → Telegram Post in Seconds</b><br>
  Developed by <a href="https://www.suchetamondal.site/">Sucheta Mondal</a>
</p>

---

## Overview
TelePost is a lightweight Python CLI tool designed for developers, bot owners, and automation users who want to **post messages, images, GIFs, or documents to Telegram channels and groups directly from the terminal**.

It supports inline buttons, media uploads, HTML formatting, and admin preview confirmation for safe publishing.

No complex frameworks required — simple, fast, and reliable.

---

## ⚡Features

- Post to Telegram channels and groups
- Send text, photo, GIF, or document
- Inline button support (JSON config)
- HTML caption formatting
- Admin preview before posting
- Confirmation prompt for safety
- Supports username, URL, or chat ID
- Lightweight and fast
- No database required

---

## 📦 Requirements

- Python 3.7+
- requests library

Install dependency:

```bash
pip install requests
````

---

## 🛠 Setup

### 1. Clone repository

```bash
git clone https://github.com/Suchetamon27/TelePost.git
cd TelePost
```

---

### 2. Edit config.py

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = YOUR_TELEGRAM_CHAT_USER_ID
```

---

### 3. Edit message.txt

Example:

```txt
📢 <b>Official Announcement</b>

TelePost is now live.

Click the button below to view the repository.

Thank you 💙
```

---

### 4. Edit message.json

Example:

```json
{
  "photo_enable": true,

  "photo": "announcement.png",
  "parse_mode": "HTML",

  "has_spoiler": false,
  "protect_content": false,

  "buttons_enable": true,
  "button_count": 2,

  "buttons": [
    { "text": "View Repository 💻", "style": "success", "url": "https://github.com/Suchetamon27/TelePost" },
    { "text": "Join Channel 📢", "style": "primary", "url": "https://t.me/telepostone" }
  ]
}
```

### 🎨 Button Color (style) Usage

TelePost supports optional button colors using the `style` field.

Available styles:

| Style | Color | Example |
|------|------|---------|
| `primary` | 🔵 Blue | Main action |
| `success` | 🟢 Green | Confirm / Positive action |
| `danger` | 🔴 Red | Warning / Delete |

Example with colors:

```json
{
  "buttons": [
    { "text": "View Repository 💻", "style": "success", "url": "https://github.com/Suchetamon27/TelePost" },
    { "text": "Join Channel 📢", "style": "primary", "url": "https://t.me/telepostone" }
  ]
}
````

### Disable color (default button)

If you don't want colored buttons, set the `style` value to an empty string:

```json
{ "text": "View Repository 💻", "style": "", "url": "https://github.com/Suchetamon27/TelePost" },
{ "text": "Join Channel 📢", "style": "", "url": "https://telepostone" }
```

which will show the default Telegram button.

### Notes

* `style` is optional
* If not specified, Telegram shows default button
* Invalid style values will be ignored

---

## ▶️ Usage

Run the script:

```bash
python main.py
```

Enter target:

```
@your_channel_username
```

Preview will be sent to admin.
Type:

```
Y
```

To confirm posting.

---

## 🎯 Supported Targets

You can use:

```
@channelusername
t.me/channelusername
https://t.me/channelusername
-100xxxxxxxxxx
```

---

## 🧩 Use Cases

### Channel Automation

Post updates instantly from terminal.

### Developer Workflows

Integrate posting into scripts or pipelines.

### Content Management

Quickly publish announcements or media.

### Bot Systems

Use as backend publishing utility.

---

## 🔒 Security

* No data storage
* No external tracking
* Uses official Telegram Bot API
* Runs locally on your machine

---

## ⚠️ Important

Bot must be admin in channel with permission:

* ✅ Post Messages

---

## 📜 License

MIT License © 2026 Sucheta Mondal

---

<p align="center">
  <b>Made with ❤️ by Sucheta Mondal</b><br>
 

