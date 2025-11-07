import qrcode
from io import BytesIO
from PIL import Image
from app.config import settings
from app.services.cache import cache_get, cache_set
import logging

logger = logging.getLogger(__name__)


async def generate_qr_code(uuid: str) -> BytesIO:
    """Generate QR code for file deep link with 7-day caching"""
    cache_key = f"qr:{uuid}"
    
    # Try cache first
    cached = await cache_get(cache_key)
    if cached:
        logger.debug(f"QR cache hit for {uuid}")
        buffer = BytesIO(cached)
        buffer.name = 'qr_code.png'
        buffer.seek(0)
        return buffer
    
    # Generate QR
    deep_link = f"https://t.me/{settings.BOT_USERNAME}?start={uuid}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2
    )
    qr.add_data(deep_link)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((512, 512), Image.Resampling.LANCZOS)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_bytes = buffer.getvalue()
    
    # Cache for 7 days
    await cache_set(cache_key, qr_bytes, ttl=604800)
    
    logger.info(f"Generated QR code for {uuid}")
    
    # Return buffer with name attribute
    result_buffer = BytesIO(qr_bytes)
    result_buffer.name = 'qr_code.png'
    result_buffer.seek(0)
    return result_buffer
