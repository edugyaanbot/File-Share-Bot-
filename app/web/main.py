from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import ORJSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvloop
import logging
from datetime import timedelta
from pathlib import Path

from app.config import settings
from app.db.mongo import connect_db, close_db
from app.services.cache import init_redis, close_redis
from app.web.api import stats, users, files, settings as settings_api, broadcast
from app.web.auth import verify_admin_credentials, create_access_token, get_current_admin
from app.bot.main import setup_bot, get_bot_dispatcher, get_bot

# Set uvloop as event loop
uvloop.install()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting application...")
    await connect_db()
    await init_redis()
    await setup_bot()
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_redis()
    await close_db()


app = FastAPI(
    title="File Share Bot Admin",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


# Templates - Use absolute path
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Root endpoint
@app.get("/")
async def root():
    """Redirect root to admin login"""
    return RedirectResponse(url="/admin/login")


# Health check
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Login page
@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page"""
    return templates.TemplateResponse("login.html", {"request": request})


# Login handler
@app.post("/admin/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Handle login"""
    if verify_admin_credentials(email, password):
        access_token_expires = timedelta(minutes=60 * 24)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=86400,
            samesite="lax"
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Dashboard page
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Show admin dashboard"""
    # Check if logged in via cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/admin/login")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "webhook_url": settings.WEBHOOK_BASE_URL
    })


# Users page
@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    """Show users management page"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/admin/login")
    
    return templates.TemplateResponse("users.html", {"request": request})


# Files page
@app.get("/admin/files", response_class=HTMLResponse)
async def admin_files(request: Request):
    """Show files management page"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/admin/login")
    
    return templates.TemplateResponse("files.html", {"request": request})


# Settings page
@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    """Show settings page"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/admin/login")
    
    return templates.TemplateResponse("settings.html", {"request": request})


# Logout
@app.get("/admin/logout")
async def logout():
    """Logout and clear cookie"""
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("access_token")
    return response


# Include API routers
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(settings_api.router, prefix="/api", tags=["settings"])
app.include_router(broadcast.router, prefix="/api", tags=["broadcast"])


# Webhook endpoint
from aiogram.types import Update

@app.post("/webhook")
async def webhook(request: Request):
    """Telegram webhook endpoint"""
    dp = get_bot_dispatcher()
    bot = get_bot()
    
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
