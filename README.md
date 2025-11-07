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

