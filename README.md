# 🤖 Telegram File Share Bot

High-performance Python Telegram bot for file sharing with QR codes, deep links, and dual admin panels.

## ✨ Features

- 📤 Store any media type to private Telegram channel
- 🔗 Generate shareable deep links
- 📱 QR codes with spoiler effect
- 👥 Web-based admin panel with dark UI
- 🤖 In-bot admin controls via inline keyboards
- 📊 Rich statistics and analytics
- 🔒 Rate limiting and security
- ⚡ Redis caching for performance
- 🐳 Docker deployment ready

## 🛠 Tech Stack

- **Bot Framework**: aiogram v3.15
- **Web Framework**: FastAPI
- **Server**: Gunicorn + Uvicorn
- **Database**: MongoDB Atlas (Motor driver)
- **Cache**: Redis
- **Event Loop**: uvloop
- **JSON**: orjson

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- MongoDB Atlas account (free tier)
- Telegram Bot Token
- Domain with HTTPS (for webhooks)

### 2. Clone & Configure

git clone <repo-url>
cd telegram-file-share-bot
cp .env.example .env

text

Edit `.env` with your values:
- `BOT_TOKEN`: Get from @BotFather
- `STORAGE_CHANNEL_ID`: Private channel ID (create one, add bot as admin)
- `MONGODB_URI`: MongoDB Atlas connection string
- `WEBHOOK_BASE_URL`: Your domain (https://yourdomain.com)

### 3. Deploy

docker-compose up -d

text

### 4. Check Status

docker-compose logs -f bot

text

## 📁 Project Structure

python/app/
├── bot/ # Telegram bot handlers & keyboards
├── web/ # FastAPI web admin panel
├── db/ # MongoDB connection & indexes
├── services/ # Business logic (files, users, QR, cache)
└── utils/ # Helper functions

text

## 🔐 Admin Access

- **Web Admin**: `https://yourdomain.com/admin/login`
  - Email: from `.env` ADMIN_EMAIL
  - Password: from `.env` ADMIN_PASSWORD

- **Bot Admin**: Send `/admin` to bot (must be in ADMIN_IDS)

## ⚙️ Configuration

All settings in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_FILE_SIZE_MB` | Max file size | 2000 |
| `USER_RATE_LIMIT_PER_MIN` | Rate limit per user | 20 |
| `MAINTENANCE_MODE` | Enable maintenance | false |

## 📊 Performance

- Connection pool: 100 max, 10 min
- Redis caching: 7-day TTL for QR codes
- Rate limiting: Per-user and global
- Optimized MongoDB indexes

## 🐛 Troubleshooting

**Webhook not working:**
Check logs
docker-compose logs bot

Verify webhook URL is HTTPS
Check firewall allows incoming connections
text

**MongoDB connection failed:**
Verify MONGODB_URI is correct
Check IP whitelist in MongoDB Atlas (allow all: 0.0.0.0/0)
text

**Redis not connecting:**
Check Redis is running
docker-compose ps redis

Redis is optional - bot works without it (no caching)
text

## 📝 License

MIT

## 🤝 Contributing

Pull requests welcome!

## 📧 Support

Create an issue for support.
🎯 DEPLOYMENT INSTRUCTIONS
Step 1: Setup
bash
# Clone or create project directory
mkdir telegram-file-share-bot
cd telegram-file-share-bot

# Copy all files above into their respective paths

# Configure environment
cp .env.example .env
nano .env  # Edit with your values
Step 2: Create Storage Channel
Create a new Telegram channel (private)

Add your bot as admin with post messages permission

Get channel ID (forward a message from channel to @userinfobot)

Add to .env as STORAGE_CHANNEL_ID=-1001234567890

Step 3: Deploy
bash
docker-compose up -d
Step 4: Verify
bash
# Check logs
docker-compose logs -f

# Test bot
# Send /start to your bot in Telegram

# Access web admin
# Open https://yourdomain.com/admin/login
